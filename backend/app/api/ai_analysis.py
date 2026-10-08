"""AI Skill Gap and Academic-Placement Synergy Analysis API Router."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.auth.security import get_current_student
from app.services.ai_service import AIService
from core.llm_advisor import LLMAdvisor

router = APIRouter(prefix="/ai", tags=["AI Intelligence & Analysis"])


class TaskBreakdownRequest(BaseModel):
    task_title: str = Field(..., description="Task title")
    subject: Optional[str] = Field("Academics", description="Subject or domain")
    task_type: Optional[str] = Field("medium", description="hard, medium, light, or assignment/lab")
    duration_minutes: Optional[int] = Field(40, ge=10, le=480)


@router.get("/skills-analysis", response_model=Dict[str, Any])
def get_skill_gaps_and_readiness(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Evaluates the student's current proficiency in DSA, Core CS, and Dev against
    real-world industry benchmarks for their chosen dream role and company tier.
    Returns overall readiness percentage, estimated preparation hours needed, and ranked gaps.
    """
    gaps, summary = AIService.analyze_skills(student["student_id"])
    return {
        "status": "success",
        "student_name": student["full_name"],
        "readiness_summary": summary,
        "skill_gaps": gaps
    }


@router.get("/synergies", response_model=Dict[str, Any])
def detect_academic_synergies(student: Dict[str, Any] = Depends(get_current_student)):
    """
    AI Synergy Engine: Scans all pending college homework, lab records, and assignments to
    identify where college study directly fulfills placement interview topics.
    Eliminates duplicated effort and calculates hours saved.
    """
    synergies = AIService.detect_synergies(student["student_id"])
    total_time_saved = sum(s.time_saved_minutes for s in synergies)
    return {
        "status": "success",
        "synergies_detected_count": len(synergies),
        "total_time_saved_minutes": total_time_saved,
        "total_time_saved_hours": round(total_time_saved / 60.0, 1),
        "synergies": synergies
    }


@router.post("/task-breakdown", response_model=Dict[str, Any])
def breakdown_task(req: TaskBreakdownRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """
    Deconstructs an academic assignment, project, or prep task into actionable 5-15 minute micro-steps.
    """
    breakdown = LLMAdvisor.generate_task_breakdown(
        task_title=req.task_title,
        subject=req.subject or "Academics",
        task_type=req.task_type or "medium",
        duration_minutes=req.duration_minutes or 40
    )
    return {
        "status": "success",
        "task_title": req.task_title,
        "subject": req.subject,
        "kickstart": breakdown["kickstart"],
        "steps": breakdown["steps"],
        "step_minutes": breakdown.get("step_minutes", [10, 15, 10, 5])
    }

