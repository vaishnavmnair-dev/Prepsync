"""Unified Student Dashboard Summary API Router."""

from datetime import date
from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.auth.security import get_current_student
from app.database.connection import fetch_all, fetch_one
from app.services.ai_service import AIService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=Dict[str, Any])
def get_dashboard_summary(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Consolidated Dashboard Endpoint:
    Returns the complete picture bridging academic workload and placement prep in a single request:
    - Profile & Target Dream Role
    - AI Placement Readiness Index & Critical Skill Gaps
    - Detected Academic Synergies & Hours Saved
    - Today's Fatigue-Aware Plan (Academic Triage + Protected Micro-Prep)
    - Active Urgent Deadlines
    - Preparation Streak & Velocity
    """
    student_id = student["student_id"]
    today_iso = date.today().isoformat()

    # 1. Career Goal
    goal = fetch_one("""
    SELECT role_title, target_company_type, target_placement_date, priority_rank, status
    FROM student_career_goals
    WHERE student_id = ? AND status = 'Active'
    ORDER BY priority_rank ASC LIMIT 1
    """, (student_id,))

    # 2. AI Skill Gap Analysis & Readiness Index
    try:
        gaps, readiness = AIService.analyze_skills(student_id)
        readiness_dict = readiness.model_dump()
        top_gaps = [g.model_dump() for g in gaps[:4]]
    except Exception:
        readiness_dict = None
        top_gaps = []

    # 3. AI Academic Synergies
    try:
        synergies = AIService.detect_synergies(student_id)
        synergies_list = [s.model_dump() for s in synergies]
        total_saved_mins = sum(s.time_saved_minutes for s in synergies)
    except Exception:
        synergies_list = []
        total_saved_mins = 0

    # 4. Today's Plan
    plan_row = fetch_one("""
    SELECT * FROM daily_plans WHERE student_id = ? AND plan_date = ?
    """, (student_id, today_iso))

    if plan_row:
        plan_items = fetch_all("""
        SELECT * FROM daily_plan_items WHERE plan_id = ? ORDER BY item_order ASC
        """, (plan_row["plan_id"],))
    else:
        # Auto generate today's plan
        try:
            generated = AIService.generate_and_save_daily_plan(student_id)
            plan_row = fetch_one("""
            SELECT * FROM daily_plans WHERE student_id = ? AND plan_date = ?
            """, (student_id, today_iso))
            plan_items = fetch_all("""
            SELECT * FROM daily_plan_items WHERE plan_id = ? ORDER BY item_order ASC
            """, (plan_row["plan_id"],)) if plan_row else []
        except Exception:
            plan_items = []

    # 5. Urgent Academic Deadlines
    urgent_tasks = fetch_all("""
    SELECT task_id, subject, task_title, priority, remaining_duration_minutes, deadline, status
    FROM academic_tasks
    WHERE student_id = ? AND status != 'Completed'
    ORDER BY deadline ASC LIMIT 5
    """, (student_id,))

    # 6. Streak
    streak = fetch_one("""
    SELECT current_streak_days, longest_streak_days, last_active_date
    FROM student_streaks WHERE student_id = ?
    """, (student_id,))

    return {
        "status": "success",
        "student": student,
        "career_goal": goal,
        "readiness_summary": readiness_dict,
        "top_skill_gaps": top_gaps,
        "synergies": {
            "count": len(synergies_list),
            "total_time_saved_minutes": total_saved_mins,
            "items": synergies_list
        },
        "today_plan": {
            "header": plan_row,
            "items": plan_items
        },
        "urgent_academic_deadlines": urgent_tasks,
        "streak": streak or {"current_streak_days": 0, "longest_streak_days": 0}
    }
