"""Student Profile and Study Availability API Router."""

import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.auth.security import get_current_student
from app.database.connection import execute_query, fetch_one

router = APIRouter(prefix="/profile", tags=["Profile & Availability"])


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    college_name: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    current_year: Optional[int] = Field(None, ge=1, le=5)
    current_semester: Optional[int] = Field(None, ge=1, le=10)
    graduation_year: Optional[int] = Field(None, ge=2024, le=2032)
    daily_available_prep_minutes: Optional[int] = Field(None, ge=30, le=720)
    preferred_study_hours_per_day: Optional[float] = Field(None, ge=0.5, le=16.0)


class AvailabilityDeclarationRequest(BaseModel):
    availability_date: Optional[date] = None
    available_start_time: str = Field("17:30", description="Start time in HH:MM format")
    available_end_time: str = Field("22:30", description="End time in HH:MM format")
    available_duration_minutes: int = Field(150, ge=15, le=720)
    energy_level: str = Field("Medium", description="High, Medium, or Low")
    preferred_activity: str = Field("Mixed", description="Coding, Reading, Project, or Mixed")
    notes: Optional[str] = None


@router.get("", response_model=Dict[str, Any])
def get_profile(student: Dict[str, Any] = Depends(get_current_student)):
    """Fetches full profile information of authenticated student."""
    return {"student": student}


@router.put("", response_model=Dict[str, Any])
def update_profile(req: ProfileUpdateRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """Updates student academic info and target prep bandwidth."""
    student_id = student["student_id"]
    now_iso = datetime.now(timezone.utc).isoformat()

    updates = []
    params = []

    if req.full_name is not None:
        updates.append("full_name = ?")
        params.append(req.full_name.strip())
    if req.college_name is not None:
        updates.append("college_name = ?")
        params.append(req.college_name.strip())
    if req.degree is not None:
        updates.append("degree = ?")
        params.append(req.degree.strip())
    if req.branch is not None:
        updates.append("branch = ?")
        params.append(req.branch.strip())
    if req.current_year is not None:
        updates.append("current_year = ?")
        params.append(req.current_year)
    if req.current_semester is not None:
        updates.append("current_semester = ?")
        params.append(req.current_semester)
    if req.graduation_year is not None:
        updates.append("graduation_year = ?")
        params.append(req.graduation_year)
    if req.daily_available_prep_minutes is not None:
        updates.append("daily_available_prep_minutes = ?")
        params.append(req.daily_available_prep_minutes)
    if req.preferred_study_hours_per_day is not None:
        updates.append("preferred_study_hours_per_day = ?")
        params.append(req.preferred_study_hours_per_day)

    if not updates:
        return {"student": student, "message": "No changes requested."}

    updates.append("updated_at = ?")
    params.append(now_iso)
    params.append(student_id)

    query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
    execute_query(query, tuple(params))

    updated_student = fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,))
    return {"student": updated_student, "message": "Profile updated successfully."}


@router.post("/availability", response_model=Dict[str, Any])
def declare_availability(req: AvailabilityDeclarationRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """
    Records or updates the student's study availability window and cognitive energy level
    for today or a target date.
    """
    student_id = student["student_id"]
    avail_date = req.availability_date or date.today()
    avail_date_iso = avail_date.isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    execute_query("""
    INSERT INTO study_availability (
        id, student_id, availability_date, available_start_time, available_end_time,
        available_duration_minutes, energy_level, preferred_activity, notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(student_id, availability_date) DO UPDATE SET
        available_start_time = excluded.available_start_time,
        available_end_time = excluded.available_end_time,
        available_duration_minutes = excluded.available_duration_minutes,
        energy_level = excluded.energy_level,
        preferred_activity = excluded.preferred_activity,
        notes = excluded.notes
    """, (
        str(uuid.uuid4()), student_id, avail_date_iso, req.available_start_time,
        req.available_end_time, req.available_duration_minutes, req.energy_level,
        req.preferred_activity, req.notes, now_iso
    ))

    record = fetch_one("""
    SELECT * FROM study_availability WHERE student_id = ? AND availability_date = ?
    """, (student_id, avail_date_iso))

    return {
        "status": "success",
        "message": f"Availability for {avail_date_iso} recorded ({req.energy_level} Energy, {req.available_duration_minutes} mins).",
        "availability": record
    }
