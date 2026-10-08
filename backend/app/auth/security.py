"""Authentication, Password Hashing, and Bearer Token Security."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, Query, status
from app.config import settings
from app.database.connection import execute_query, fetch_one


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Generates cryptographic PBKDF2 HMAC SHA-256 hash with salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return pw_hash, salt


def verify_password(plain_password: str, stored_hash: str, salt: str) -> bool:
    """Verifies plain password against stored salt and hash in constant time."""
    computed_hash, _ = hash_password(plain_password, salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def create_student_session(student_id: str) -> str:
    """Creates a new session token, persists it in the database with expiry, and returns it."""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=settings.SESSION_TOKEN_EXPIRE_HOURS)).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    execute_query("""
    UPDATE students
    SET token_session = ?, token_expires_at = ?, updated_at = ?
    WHERE student_id = ?
    """, (token, expires_at, now_iso, student_id))

    return token


def revoke_student_session(token: str) -> bool:
    """Invalidates the student's active session token upon logout."""
    affected = execute_query("""
    UPDATE students
    SET token_session = NULL, token_expires_at = NULL, updated_at = ?
    WHERE token_session = ?
    """, (datetime.now(timezone.utc).isoformat(), token))
    return affected > 0


def get_current_student(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract and authenticate current student via:
    1. 'Authorization: Bearer <token>' header
    2. Optional '?token=<token>' query parameter (convenient for testing / direct URLs)
    """
    extracted_token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            extracted_token = parts[1]
        elif len(parts) == 1:
            extracted_token = parts[0]
    elif token:
        extracted_token = token

    if not extracted_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or Bearer token. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Lookup student by active session token
    student = fetch_one("""
    SELECT student_id, full_name, email, college_name, degree, branch,
           current_year, current_semester, graduation_year, preferred_study_hours_per_day,
           daily_available_prep_minutes, timezone, token_session, token_expires_at
    FROM students
    WHERE token_session = ?
    """, (extracted_token,))

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check expiration
    if student.get("token_expires_at"):
        try:
            exp_dt = datetime.fromisoformat(student["token_expires_at"])
            if datetime.now(timezone.utc) > exp_dt:
                revoke_student_session(extracted_token)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session has expired. Please log in again.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except Exception:
            pass

    return student
