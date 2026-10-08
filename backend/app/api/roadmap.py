"""Personalized Placement Roadmap API Router."""

import json
from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.auth.security import get_current_student
from app.database.connection import fetch_one
from app.services.ai_service import AIService

router = APIRouter(prefix="/roadmap", tags=["Placement Roadmap"])


@router.post("/generate", response_model=Dict[str, Any])
def generate_placement_roadmap(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Synthesizes a personalized 4-phase placement preparation roadmap structured around
    the student's target company tier, remaining months, and prioritized skill gaps.
    Persists the generated roadmap into the database.
    """
    roadmap = AIService.generate_and_save_roadmap(student["student_id"])
    return {
        "status": "success",
        "message": "Generated personalized placement roadmap.",
        "roadmap": roadmap
    }


@router.get("", response_model=Dict[str, Any])
def get_current_roadmap(student: Dict[str, Any] = Depends(get_current_student)):
    """
    Fetches the student's active placement roadmap from the database.
    If no roadmap has been generated yet, automatically synthesizes one.
    """
    student_id = student["student_id"]
    row = fetch_one("""
    SELECT * FROM placement_roadmaps
    WHERE student_id = ?
    ORDER BY created_at DESC LIMIT 1
    """, (student_id,))

    if not row:
        roadmap = AIService.generate_and_save_roadmap(student_id)
        return {"status": "success", "roadmap": roadmap}

    try:
        phases = json.loads(row["phases_json"])
    except Exception:
        phases = []

    return {
        "status": "success",
        "roadmap": {
            "roadmap_id": row["roadmap_id"],
            "target_role": row["role_title"],
            "target_company_type": row["target_company_type"],
            "total_estimated_duration_weeks": row["total_estimated_duration_weeks"],
            "phases": phases,
            "created_at": row["created_at"]
        }
    }
