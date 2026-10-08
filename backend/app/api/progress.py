"""Study Progress and Streak Tracking API Router."""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.auth.security import get_current_student
from app.database.connection import execute_query, fetch_all, fetch_one

router = APIRouter(prefix="/progress", tags=["Progress & Streaks"])


class ProgressLogRequest(BaseModel):
    task_category: str = Field("Placement", description="Placement, Academic, or Synergy")
    task_title: str = Field(..., description="Title of task completed")
    duration_minutes: int = Field(30, ge=5, le=360)
    problems_solved: int = Field(0, ge=0)
    notes: Optional[str] = None


@router.post("/log", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def log_progress_session(
    req: ProgressLogRequest,
    student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Records a completed study session or coding practice block,
    updating the student's daily preparation totals and active streak.
    """
    student_id = student["student_id"]
    now_iso = datetime.now(timezone.utc).isoformat()
    today_iso = date.today().isoformat()
    log_id = str(uuid.uuid4())

    execute_query("""
    INSERT INTO progress_logs (
        log_id, student_id, task_category, task_title, duration_minutes,
        problems_solved, notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        log_id, student_id, req.task_category, req.task_title.strip(),
        req.duration_minutes, req.problems_solved, req.notes, now_iso
    ))

    # Advance streak
    streak_row = fetch_one("SELECT * FROM student_streaks WHERE student_id = ?", (student_id,))
    if streak_row:
        last_active = streak_row.get("last_active_date")
        curr_streak = streak_row["current_streak_days"]
        longest = streak_row["longest_streak_days"]

        if last_active != today_iso:
            curr_streak += 1
            longest = max(longest, curr_streak)

        execute_query("""
        UPDATE student_streaks
        SET current_streak_days = ?, longest_streak_days = ?, last_active_date = ?, updated_at = ?
        WHERE student_id = ?
        """, (curr_streak, longest, today_iso, now_iso, student_id))
    else:
        execute_query("""
        INSERT INTO student_streaks (student_id, current_streak_days, longest_streak_days, last_active_date, updated_at)
        VALUES (?, 1, 1, ?, ?)
        """, (student_id, today_iso, now_iso))

    updated_streak = fetch_one("SELECT * FROM student_streaks WHERE student_id = ?", (student_id,))
    return {
        "status": "success",
        "message": f"Logged {req.duration_minutes}m of {req.task_category} prep! Streak is {updated_streak['current_streak_days']} days.",
        "streak": updated_streak
    }


@router.get("/streak", response_model=Dict[str, Any])
def get_streak_status(student: Dict[str, Any] = Depends(get_current_student)):
    """Retrieves current streak stats and recent active velocity."""
    student_id = student["student_id"]
    streak = fetch_one("SELECT * FROM student_streaks WHERE student_id = ?", (student_id,))

    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    logs_7d = fetch_all("""
    SELECT * FROM progress_logs
    WHERE student_id = ? AND created_at >= ?
    ORDER BY created_at DESC
    """, (student_id, seven_days_ago))

    total_study_minutes = sum(l["duration_minutes"] for l in logs_7d)
    total_problems = sum(l.get("problems_solved", 0) for l in logs_7d)

    return {
        "streak": streak or {"current_streak_days": 0, "longest_streak_days": 0},
        "last_7_days_stats": {
            "total_study_hours": round(total_study_minutes / 60.0, 1),
            "coding_problems_solved": total_problems,
            "session_count": len(logs_7d)
        }
    }


@router.get("/history", response_model=List[Dict[str, Any]])
def get_study_history(student: Dict[str, Any] = Depends(get_current_student)):
    """Retrieves past completed study activity logs."""
    return fetch_all("""
    SELECT * FROM progress_logs
    WHERE student_id = ?
    ORDER BY created_at DESC LIMIT 50
    """, (student["student_id"],))
