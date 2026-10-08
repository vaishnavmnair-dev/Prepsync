"""Career Goals and Skills Management API Router."""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.auth.security import get_current_student
from app.database.connection import execute_query, fetch_all, fetch_one

router = APIRouter(prefix="/career", tags=["Career & Skills"])


class CareerGoalRequest(BaseModel):
    role_title: str = Field(..., description="Target role (e.g., Software Developer, AI/ML Engineer)")
    target_company_type: str = Field("FAANG / Tier-1", description="Target tier: FAANG / Tier-1, Product-based, Service-based, Early-stage Startup")
    target_placement_date: Optional[date] = None
    priority_rank: int = Field(1, ge=1)
    notes: Optional[str] = None


class SkillItemRequest(BaseModel):
    skill_name: str
    category: str = Field("DSA", description="DSA, Programming, Core CS, Development, Aptitude, Soft Skills")
    current_proficiency: int = Field(..., ge=0, le=5, description="0=None, 1=Beginner, 2=Basic, 3=Intermediate, 4=Advanced, 5=Expert")
    target_proficiency: int = Field(4, ge=1, le=5)
    confidence_level: str = Field("Medium", description="Low, Medium, High")


@router.get("/roles", response_model=List[Dict[str, Any]])
def list_career_roles():
    """Returns standard career track roles and benchmark details."""
    return fetch_all("SELECT * FROM career_roles ORDER BY role_title ASC")


@router.get("/goal", response_model=Dict[str, Any])
def get_career_goal(student: Dict[str, Any] = Depends(get_current_student)):
    """Retrieves current student's target career aspiration."""
    goal = fetch_one("""
    SELECT * FROM student_career_goals
    WHERE student_id = ? AND status = 'Active'
    ORDER BY priority_rank ASC LIMIT 1
    """, (student["student_id"],))

    if not goal:
        return {"goal": None, "message": "No active career goal declared yet."}
    return {"goal": goal}


@router.post("/goal", response_model=Dict[str, Any])
def set_career_goal(req: CareerGoalRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """Sets or updates the primary career target and company tier."""
    student_id = student["student_id"]
    target_d = req.target_placement_date or (date.today() + timedelta(days=240))
    target_d_iso = target_d.isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Deactivate previous active goals if updating primary
    execute_query("""
    UPDATE student_career_goals SET status = 'Paused'
    WHERE student_id = ? AND priority_rank = ?
    """, (student_id, req.priority_rank))

    goal_id = str(uuid.uuid4())
    execute_query("""
    INSERT INTO student_career_goals (
        goal_id, student_id, role_title, target_company_type, target_placement_date,
        priority_rank, status, notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, 'Active', ?, ?)
    """, (goal_id, student_id, req.role_title, req.target_company_type, target_d_iso, req.priority_rank, req.notes, now_iso))

    goal = fetch_one("SELECT * FROM student_career_goals WHERE goal_id = ?", (goal_id,))
    return {"status": "success", "message": f"Target set to {req.role_title} ({req.target_company_type}).", "goal": goal}


@router.get("/skills", response_model=List[Dict[str, Any]])
def list_student_skills(student: Dict[str, Any] = Depends(get_current_student)):
    """Retrieves all assessed skills and proficiency ratings for the student."""
    return fetch_all("""
    SELECT * FROM student_skills WHERE student_id = ? ORDER BY category, skill_name
    """, (student["student_id"],))


@router.post("/skills", response_model=Dict[str, Any])
def upsert_student_skill(req: SkillItemRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """Records or updates student proficiency in a specific skill."""
    student_id = student["student_id"]
    now_iso = datetime.now(timezone.utc).isoformat()

    execute_query("""
    INSERT INTO student_skills (
        id, student_id, skill_name, category, current_proficiency, target_proficiency,
        confidence_level, assessment_source, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Self Assessment', ?, ?)
    ON CONFLICT(student_id, skill_name) DO UPDATE SET
        category = excluded.category,
        current_proficiency = excluded.current_proficiency,
        target_proficiency = excluded.target_proficiency,
        confidence_level = excluded.confidence_level,
        updated_at = excluded.updated_at
    """, (
        str(uuid.uuid4()), student_id, req.skill_name.strip(), req.category,
        req.current_proficiency, req.target_proficiency, req.confidence_level,
        now_iso, now_iso
    ))

    skill = fetch_one("""
    SELECT * FROM student_skills WHERE student_id = ? AND skill_name = ?
    """, (student_id, req.skill_name.strip()))

    return {"status": "success", "message": f"Updated skill '{req.skill_name}'.", "skill": skill}
