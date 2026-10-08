"""Authentication and Profile Pydantic Schemas."""

from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class StudentSignupRequest(BaseModel):
    email: str = Field(..., description="Student college or personal email")
    password: str = Field(..., min_length=6, description="Minimum 6 character password")
    full_name: str = Field(..., description="Student's full name")
    college_name: str = Field(..., description="Name of university or institute")
    degree: str = Field("B.Tech", description="Degree program (e.g., B.Tech, B.E., M.Tech)")
    branch: str = Field("Computer Science", description="Branch/Stream (e.g., CSE, ECE, AI&ML)")
    current_year: int = Field(3, ge=1, le=5)
    current_semester: int = Field(5, ge=1, le=10)
    graduation_year: int = Field(2026, ge=2024, le=2032)
    daily_available_prep_minutes: int = Field(150, ge=30, le=720)
    preferred_study_hours_per_day: float = Field(3.0, ge=0.5, le=16.0)
    target_role: Optional[str] = Field("Software Developer", description="Target dream role")
    target_company_type: Optional[str] = Field("FAANG / Tier-1", description="Target company tier")


class StudentLoginRequest(BaseModel):
    email: str
    password: str


class StudentProfileResponse(BaseModel):
    student_id: str
    full_name: str
    email: str
    college_name: str
    degree: str
    branch: str
    current_year: int
    current_semester: int
    graduation_year: int
    daily_available_prep_minutes: int
    preferred_study_hours_per_day: float
    timezone: str


class AuthResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    expires_in_hours: int = 72
    student: Dict[str, Any]
    message: str = "Authentication successful"


class MessageResponse(BaseModel):
    status: str = "success"
    message: str
