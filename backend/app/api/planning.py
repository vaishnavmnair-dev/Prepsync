"""Dynamic Fatigue-Aware Daily and Weekly Planning API Router."""

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.security import get_current_student
from app.database.connection import execute_query, fetch_all, fetch_one
from app.services.ai_service import AIService
from core.bandwidth_engine import BandwidthEngine
from core.models import AdaptationTrigger, DailyPlan, PlanAdaptationResponse, WeeklyPlan

router = APIRouter(prefix="/plan", tags=["Dynamic Adaptive Planning"])


class DailyPlanGenerateRequest(BaseModel):
    target_date: Optional[date] = None
    energy_level: Optional[str] = Field(None, description="High, Medium, Low")
    available_minutes: Optional[int] = Field(None, ge=30, le=720)


class PlanAdaptationApiRequest(BaseModel):
    trigger_event: str = Field(
        "Surprise Academic Assignment",
        description="Surprise Academic Assignment, Cognitive Exhaustion / Fatigue, Academic Task Took Longer Than Estimated"
    )
    details: Dict[str, Any] = Field(default_factory=dict, description="e.g. {'title': 'Emergency Lab Record', 'subject': 'DBMS'}")
    new_energy_level: Optional[str] = Field(None, description="High, Medium, Low")
    additional_academic_minutes: Optional[int] = Field(None, description="Extra minutes needed for surprise task")
    new_available_minutes: Optional[int] = None


class ItemStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Scheduled, In Progress, Completed, Skipped")


@router.post("/daily/generate", response_model=DailyPlan)
def generate_daily_plan(
    req: DailyPlanGenerateRequest = DailyPlanGenerateRequest(),
    student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Executes the Fatigue-Aware Bandwidth Engine:
    1. Time-boxes academic obligations (Academic Triage) to avoid deadline penalties.
    2. Protects a Minimum Viable Placement Task (MVPT) to defend preparation continuity.
    3. Allocates rest buffers based on student cognitive energy.
    Saves the schedule to the database.
    """
    plan = AIService.generate_and_save_daily_plan(
        student_id=student["student_id"],
        target_date=req.target_date,
        custom_energy=req.energy_level,
        custom_avail_minutes=req.available_minutes
    )
    return plan


@router.get("/daily/today", response_model=Dict[str, Any])
def get_today_plan(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Retrieves today's generated study schedule and granular time-boxed tasks.
    If today's plan has not been generated yet, automatically calculates and persists one.
    """
    student_id = student["student_id"]
    today_iso = date.today().isoformat()

    plan_row = fetch_one("""
    SELECT * FROM daily_plans WHERE student_id = ? AND plan_date = ?
    """, (student_id, today_iso))

    if not plan_row:
        plan = AIService.generate_and_save_daily_plan(student_id)
        plan_row = fetch_one("""
        SELECT * FROM daily_plans WHERE student_id = ? AND plan_date = ?
        """, (student_id, today_iso))

    items = fetch_all("""
    SELECT * FROM daily_plan_items WHERE plan_id = ? ORDER BY item_order ASC
    """, (plan_row["plan_id"],))

    return {
        "status": "success",
        "plan": plan_row,
        "items": items
    }


@router.post("/weekly/generate", response_model=WeeklyPlan)
def generate_weekly_plan(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Generates a 7-day adaptive schedule balancing high-workload weekday lecture/lab blocks
    with weekend deep-work interview sprints.
    """
    context = AIService.build_planning_context(student["student_id"])
    weekly_plan = BandwidthEngine.generate_weekly_plan(context)
    return weekly_plan


@router.post("/adapt", response_model=PlanAdaptationResponse)
def adapt_daily_plan(
    req: PlanAdaptationApiRequest,
    student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Real-Time Dynamic Adaptation Engine:
    Recalculates the day's schedule when unforeseen disruptions occur
    (e.g., surprise assignment, extreme exhaustion, lecture overrun).
    Guilt-free compression guarantees streak preservation with zero broken momentum.
    """
    response = AIService.adapt_daily_plan(
        student_id=student["student_id"],
        trigger_event=req.trigger_event,
        details=req.details,
        new_energy_level=req.new_energy_level,
        additional_academic_minutes=req.additional_academic_minutes,
        new_available_minutes=req.new_available_minutes
    )
    return response


@router.put("/items/{item_id}/status", response_model=Dict[str, Any])
def update_plan_item_status(
    item_id: str,
    req: ItemStatusUpdateRequest,
    student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Updates the execution status of a scheduled daily plan item.
    If marked as 'Completed', automatically logs study progress and advances the student's streak!
    """
    item = fetch_one("SELECT * FROM daily_plan_items WHERE plan_item_id = ?", (item_id,))
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily plan item not found.")

    execute_query("UPDATE daily_plan_items SET status = ? WHERE plan_item_id = ?", (req.status, item_id))

    # If completed, advance streak and log progress
    if req.status == "Completed":
        student_id = student["student_id"]
        today_iso = date.today().isoformat()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Update streak
        execute_query("""
        UPDATE student_streaks
        SET current_streak_days = current_streak_days + 1,
            longest_streak_days = MAX(longest_streak_days, current_streak_days + 1),
            last_active_date = ?,
            updated_at = ?
        WHERE student_id = ?
        """, (today_iso, now_iso, student_id))

        # Log entry
        execute_query("""
        INSERT INTO progress_logs (
            log_id, student_id, task_category, task_title, duration_minutes,
            problems_solved, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), student_id, item["task_category"], item["title"],
            item["planned_duration_minutes"], 1 if item["task_category"] == "Placement" else 0,
            "Completed via daily plan schedule", now_iso
        ))

    updated_item = fetch_one("SELECT * FROM daily_plan_items WHERE plan_item_id = ?", (item_id,))
    return {
        "status": "success",
        "message": f"Task '{item['title']}' updated to '{req.status}'.",
        "item": updated_item
    }
