"""Academic Workload and Deadlines Management API Router."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.auth.security import get_current_student
from app.database.connection import execute_query, fetch_all, fetch_one

router = APIRouter(prefix="/academic", tags=["Academic Workload"])


class AcademicTaskCreateRequest(BaseModel):
    subject: str = Field(..., description="Subject or Course (e.g., DBMS, OS, Mathematics)")
    task_title: str = Field(..., description="Title of assignment, lab record, or project")
    task_type: str = Field("Assignment", description="Assignment, Lab, Exam, Project, Quiz")
    priority: str = Field("Medium", description="Critical, High, Medium, Low")
    difficulty: str = Field("Medium", description="Easy, Medium, Hard")
    estimated_duration_minutes: int = Field(60, ge=15, le=480)
    deadline: datetime = Field(..., description="ISO 8601 deadline timestamp")


class AcademicTaskUpdateRequest(BaseModel):
    remaining_duration_minutes: Optional[int] = Field(None, ge=0, le=480)
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    priority: Optional[str] = None
    status: Optional[str] = Field(None, description="Not Started, In Progress, Completed")


@router.get("/tasks", response_model=List[Dict[str, Any]])
def list_academic_tasks(student: Dict[str, Any] = Depends(get_current_student)):
    """Retrieves all academic assignments, labs, and exam preparations for current student."""
    return fetch_all("""
    SELECT * FROM academic_tasks
    WHERE student_id = ?
    ORDER BY CASE status WHEN 'Completed' THEN 1 ELSE 0 END, deadline ASC
    """, (student["student_id"],))


@router.post("/tasks", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_academic_task(req: AcademicTaskCreateRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """Logs a new academic commitment or assignment deadline into the student's workload inbox."""
    student_id = student["student_id"]
    task_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    deadline_iso = req.deadline.isoformat()

    execute_query("""
    INSERT INTO academic_tasks (
        task_id, student_id, subject, task_title, task_type, priority, difficulty,
        estimated_duration_minutes, remaining_duration_minutes, deadline,
        completion_percentage, status, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'Not Started', ?, ?)
    """, (
        task_id, student_id, req.subject.strip(), req.task_title.strip(),
        req.task_type, req.priority, req.difficulty, req.estimated_duration_minutes,
        req.estimated_duration_minutes, deadline_iso, now_iso, now_iso
    ))

    task = fetch_one("SELECT * FROM academic_tasks WHERE task_id = ?", (task_id,))
    return {"status": "success", "message": f"Added task '{req.task_title}'.", "task": task}


@router.put("/tasks/{task_id}", response_model=Dict[str, Any])
def update_academic_task(task_id: str, req: AcademicTaskUpdateRequest, student: Dict[str, Any] = Depends(get_current_student)):
    """Updates progress or status on an academic task."""
    student_id = student["student_id"]
    existing = fetch_one("SELECT * FROM academic_tasks WHERE task_id = ? AND student_id = ?", (task_id, student_id))
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic task not found.")

    now_iso = datetime.now(timezone.utc).isoformat()
    updates = []
    params = []

    if req.remaining_duration_minutes is not None:
        updates.append("remaining_duration_minutes = ?")
        params.append(req.remaining_duration_minutes)
    if req.completion_percentage is not None:
        updates.append("completion_percentage = ?")
        params.append(req.completion_percentage)
        if req.completion_percentage == 100:
            updates.append("status = 'Completed'")
            updates.append("remaining_duration_minutes = 0")
    if req.priority is not None:
        updates.append("priority = ?")
        params.append(req.priority)
    if req.status is not None:
        updates.append("status = ?")
        params.append(req.status)
        if req.status == "Completed":
            updates.append("completion_percentage = 100")
            updates.append("remaining_duration_minutes = 0")

    if not updates:
        return {"task": existing, "message": "No changes requested."}

    updates.append("updated_at = ?")
    params.append(now_iso)
    params.append(task_id)
    params.append(student_id)

    query = f"UPDATE academic_tasks SET {', '.join(updates)} WHERE task_id = ? AND student_id = ?"
    execute_query(query, tuple(params))

    updated_task = fetch_one("SELECT * FROM academic_tasks WHERE task_id = ?", (task_id,))
    return {"status": "success", "message": "Task updated successfully.", "task": updated_task}


@router.delete("/tasks/{task_id}", response_model=Dict[str, Any])
def delete_academic_task(task_id: str, student: Dict[str, Any] = Depends(get_current_student)):
    """Removes an academic task from student's active commitments."""
    student_id = student["student_id"]
    affected = execute_query("DELETE FROM academic_tasks WHERE task_id = ? AND student_id = ?", (task_id, student_id))
    if affected == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Academic task not found.")
    return {"status": "success", "message": "Academic task deleted."}
