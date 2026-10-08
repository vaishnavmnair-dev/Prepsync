"""Authentication API Router: Signup, Signin/Login, Logout, and Current User."""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.auth.security import create_student_session, get_current_student, hash_password, revoke_student_session, verify_password
from app.database.connection import execute_query, fetch_one
from app.schemas.auth_schemas import AuthResponse, MessageResponse, StudentLoginRequest, StudentSignupRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def register_student(req: StudentSignupRequest):
    """
    Registers a new student account, establishes their career baseline,
    creates initial academic skill slots, and returns an authentication session token.
    """
    # 1. Check if email already exists
    existing = fetch_one("SELECT student_id FROM students WHERE LOWER(email) = LOWER(?)", (req.email.strip(),))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in."
        )

    student_id = str(uuid.uuid4())
    pw_hash, salt = hash_password(req.password)
    now_iso = datetime.now(timezone.utc).isoformat()

    # 2. Insert Student
    execute_query("""
    INSERT INTO students (
        student_id, full_name, email, password_hash, salt, college_name, degree, branch,
        current_year, current_semester, graduation_year, daily_available_prep_minutes,
        preferred_study_hours_per_day, timezone, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id, req.full_name.strip(), req.email.strip().lower(), pw_hash, salt,
        req.college_name.strip(), req.degree.strip(), req.branch.strip(),
        req.current_year, req.current_semester, req.graduation_year,
        req.daily_available_prep_minutes, req.preferred_study_hours_per_day,
        "Asia/Kolkata", now_iso, now_iso
    ))

    # 3. Insert Career Goal
    target_date = (date.today() + timedelta(days=270)).isoformat()
    execute_query("""
    INSERT INTO student_career_goals (
        goal_id, student_id, role_title, target_company_type, target_placement_date, priority_rank, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), student_id, req.target_role or "Software Developer",
        req.target_company_type or "FAANG / Tier-1", target_date, 1, "Active", now_iso
    ))

    # 4. Insert Baseline Skills
    baseline_skills = [
        ("DSA", "DSA", 1, 4, "Medium"),
        ("C/C++", "Programming", 2, 3, "Medium"),
        ("Python", "Programming", 2, 4, "Medium"),
        ("SQL & DBMS", "Core CS", 1, 4, "Low"),
        ("Operating Systems", "Core CS", 1, 3, "Low"),
        ("Computer Networks", "Core CS", 1, 3, "Low"),
        ("Web Development", "Development", 2, 4, "Medium"),
        ("Quantitative Aptitude", "Aptitude", 1, 4, "Medium")
    ]
    for sname, scat, cur, tgt, conf in baseline_skills:
        execute_query("""
        INSERT INTO student_skills (
            id, student_id, skill_name, category, current_proficiency, target_proficiency, confidence_level, assessment_source, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), student_id, sname, scat, cur, tgt, conf, "Initial Onboarding", now_iso, now_iso))

    # 5. Initialize Streaks
    execute_query("""
    INSERT INTO student_streaks (student_id, current_streak_days, longest_streak_days, last_active_date, updated_at)
    VALUES (?, 0, 0, ?, ?)
    """, (student_id, date.today().isoformat(), now_iso))

    # 6. Issue Session Token
    token = create_student_session(student_id)

    student_profile = fetch_one("""
    SELECT student_id, full_name, email, college_name, degree, branch,
           current_year, current_semester, graduation_year, daily_available_prep_minutes,
           preferred_study_hours_per_day, timezone
    FROM students WHERE student_id = ?
    """, (student_id,))

    return AuthResponse(
        token=token,
        token_type="bearer",
        student=student_profile,
        message="Account created successfully! Welcome to PrepPilot."
    )


@router.post("/login", response_model=AuthResponse)
@router.post("/signin", response_model=AuthResponse, include_in_schema=False)
def login_student(req: StudentLoginRequest):
    """
    Authenticates student credentials, validates password hash,
    and returns an active session token.
    """
    student = fetch_one("""
    SELECT student_id, full_name, email, password_hash, salt, college_name, degree, branch,
           current_year, current_semester, graduation_year, daily_available_prep_minutes,
           preferred_study_hours_per_day, timezone
    FROM students
    WHERE LOWER(email) = LOWER(?)
    """, (req.email.strip(),))

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    if not verify_password(req.password, student["password_hash"], student["salt"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    # Issue session token
    token = create_student_session(student["student_id"])

    student_safe = {
        "student_id": student["student_id"],
        "full_name": student["full_name"],
        "email": student["email"],
        "college_name": student["college_name"],
        "degree": student["degree"],
        "branch": student["branch"],
        "current_year": student["current_year"],
        "current_semester": student["current_semester"],
        "graduation_year": student["graduation_year"],
        "daily_available_prep_minutes": student["daily_available_prep_minutes"],
        "preferred_study_hours_per_day": student["preferred_study_hours_per_day"],
        "timezone": student["timezone"]
    }

    return AuthResponse(
        token=token,
        token_type="bearer",
        student=student_safe,
        message="Login successful. Welcome back!"
    )


@router.post("/logout", response_model=MessageResponse)
def logout_student(authorization: str = Header(None)):
    """
    Invalidates the active session token, logging the student out.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization header.")

    token = authorization.replace("Bearer ", "").strip()
    revoked = revoke_student_session(token)

    return MessageResponse(
        status="success" if revoked else "ignored",
        message="Successfully logged out." if revoked else "Token was already inactive."
    )


@router.get("/me", response_model=Dict[str, Any])
def get_current_user_profile(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Returns the currently authenticated student profile, their active career goal, and streak.
    """
    goal = fetch_one("""
    SELECT role_title, target_company_type, target_placement_date, priority_rank, status
    FROM student_career_goals
    WHERE student_id = ? AND status = 'Active'
    ORDER BY priority_rank ASC LIMIT 1
    """, (student["student_id"],))

    streak = fetch_one("""
    SELECT current_streak_days, longest_streak_days, last_active_date
    FROM student_streaks
    WHERE student_id = ?
    """, (student["student_id"],))

    return {
        "student": student,
        "career_goal": goal,
        "streak": streak or {"current_streak_days": 0, "longest_streak_days": 0}
    }
