"""AI Placement Coach and Micro-Drills API Router."""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.security import get_current_student
from app.services.ai_service import AIService
from core.llm_advisor import LLMAdvisor
from core.models import EnergyLevel

router = APIRouter(prefix="/coach", tags=["AI Placement Coach"])


class MicroDrillRequest(BaseModel):
    skill_name: str = Field("DSA", description="Skill to drill: DSA, SQL/DBMS, Operating Systems, Computer Networks, System Design, Aptitude")
    energy_level: str = Field("Medium", description="High, Medium, or Low")


@router.post("/micro-drill", response_model=Dict[str, Any])
def get_energy_matched_micro_drill(
    req: MicroDrillRequest,
    student: Dict[str, Any] = Depends(get_current_student)
):
    """
    Returns a bite-sized 15-30 minute interview drill tailored to remaining mental energy.
    Ensures placement momentum continues even on high-fatigue academic days without burnout.
    """
    try:
        e_level = EnergyLevel(req.energy_level)
    except Exception:
        e_level = EnergyLevel.MEDIUM

    drill = LLMAdvisor.generate_micro_drill(req.skill_name, e_level)
    return {
        "status": "success",
        "student_name": student["full_name"],
        "skill": req.skill_name,
        "energy_level": e_level.value,
        "drill": drill
    }


@router.get("/guidance", response_model=Dict[str, Any])
def get_strategic_guidance(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Synthesizes holistic mentor guidance evaluating the student's academic commitments,
    upcoming deadlines, remaining time to placements, and active skill gaps.
    """
    context = AIService.build_planning_context(student["student_id"])
    guidance = LLMAdvisor.generate_coach_guidance(context)
    return {
        "status": "success",
        "student_name": student["full_name"],
        "guidance": guidance
    }
