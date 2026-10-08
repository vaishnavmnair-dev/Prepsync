"""
Pydantic data models for the AI College & Placement Companion.
Defines schemas for student profiles, career goals, skill gaps,
academic workloads, study availability, generated plans, and adaptations.
"""

from datetime import date, datetime, time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EnergyLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class UrgencyCategory(str, Enum):
    CRITICAL = "CRITICAL (Due <= 24h)"
    HIGH = "HIGH (Due <= 48h)"
    MEDIUM = "MEDIUM (Due This Week)"
    LOW = "LOW (Due Later)"
    OVERDUE = "OVERDUE"


class TaskCategory(str, Enum):
    ACADEMIC = "Academic"
    PLACEMENT = "Placement"
    SYNERGY = "Synergy"


class SkillCategory(str, Enum):
    PROGRAMMING = "Programming"
    DSA = "DSA"
    CORE_CS = "Core CS"
    DEVELOPMENT = "Development"
    APTITUDE = "Aptitude"
    INTERVIEW = "Interview"
    SOFT_SKILLS = "Soft Skills"


class CompanyTier(str, Enum):
    PRODUCT_BASED = "Product-based"
    FAANG_TIER1 = "FAANG / Tier-1"
    SERVICE_BASED = "Service-based"
    STARTUP = "Early-stage Startup"
    UNICORN = "Unicorn Startup"
    OPEN = "Open to All"


# ============================================================================
# Student & Academic Inputs
# ============================================================================

class StudentProfile(BaseModel):
    student_id: str = "demo-student-id"
    full_name: str
    college_name: str
    degree: str = "B.Tech"
    branch: str = "Computer Science"
    current_year: int = Field(ge=1, le=5)
    current_semester: int = Field(ge=1, le=10)
    graduation_year: int
    daily_available_prep_minutes: int = 150
    preferred_study_hours_per_day: float = 3.0
    timezone: str = "Asia/Kolkata"


class CareerGoal(BaseModel):
    role_title: str  # e.g., "Software Developer", "Backend Developer", "AI/ML Engineer"
    target_company_type: CompanyTier = CompanyTier.PRODUCT_BASED
    target_placement_date: date
    priority_rank: int = 1
    notes: Optional[str] = None


class StudentSkillItem(BaseModel):
    skill_name: str
    category: SkillCategory
    current_proficiency: int = Field(ge=0, le=5, description="0=None, 1=Beginner, 2=Basic, 3=Intermediate, 4=Advanced, 5=Expert")
    target_proficiency: int = Field(ge=0, le=5, default=4)
    confidence_level: str = "Medium"
    assessment_source: str = "Self Assessment"


class AcademicTask(BaseModel):
    task_id: str
    subject: str
    task_title: str
    task_type: str = "Assignment"  # Assignment, Lab, Exam, Project, Quiz
    priority: str = "Medium"  # Low, Medium, High, Critical
    difficulty: str = "Medium"  # Easy, Medium, Hard
    estimated_duration_minutes: int
    remaining_duration_minutes: int
    deadline: datetime
    completion_percentage: int = 0
    status: str = "Not Started"


class ScheduleBlock(BaseModel):
    day_of_week: str
    start_time: str  # "09:30"
    end_time: str    # "16:30"
    activity_name: str
    activity_type: str = "Lecture"  # Lecture, Lab, Tutorial, Transit


class StudyAvailability(BaseModel):
    availability_date: date
    available_start_time: str = "17:30"
    available_end_time: str = "22:30"
    available_duration_minutes: int = 150
    energy_level: EnergyLevel = EnergyLevel.MEDIUM
    preferred_activity: str = "Mixed"
    notes: Optional[str] = None


class RecentProgress(BaseModel):
    total_study_hours_last_7d: float = 0.0
    academic_minutes_last_7d: int = 0
    placement_minutes_last_7d: int = 0
    coding_problems_solved_last_7d: int = 0
    current_streak_days: int = 0
    longest_streak_days: int = 0


# ============================================================================
# Skill Gap & Synergy Analysis Models
# ============================================================================

class SkillGapReportItem(BaseModel):
    skill_name: str
    category: SkillCategory
    current_proficiency: int
    required_proficiency: int
    skill_gap: int
    importance_level: str  # Critical, High, Medium, Low
    weight_score: float
    gap_urgency_score: float
    recommended_focus_order: int
    status: str  # "Ready", "Needs Practice", "Critical Gap"


class ReadinessSummary(BaseModel):
    overall_readiness_percentage: float
    role_title: str
    target_company_type: str
    months_until_placement: float
    estimated_prep_hours_needed: int
    estimated_weeks_to_ready: float
    feasibility_status: str  # "On Track", "Tight Schedule", "High Risk / Acceleration Needed"
    critical_gaps_count: int
    total_skills_evaluated: int


class AcademicPlacementSynergy(BaseModel):
    academic_task_id: str
    academic_task_title: str
    academic_subject: str
    relevant_placement_skill: str
    synergy_type: str  # Direct Concept, Coding Practical, System Design Principle
    synergy_description: str
    recommended_interview_takeaway: str
    time_saved_minutes: int


# ============================================================================
# Daily & Weekly Planning Models
# ============================================================================

class DailyPlanItem(BaseModel):
    item_order: int
    task_category: TaskCategory
    task_id: Optional[str] = None
    title: str
    subject_or_skill: str
    scheduled_start_time: str
    scheduled_end_time: str
    planned_duration_minutes: int
    priority_score: float
    energy_requirement: EnergyLevel
    ai_reasoning: str
    is_mvpt: bool = False  # Minimum Viable Placement Task (streak protector)
    synergy_tip: Optional[str] = None
    status: str = "Scheduled"


class DailyPlan(BaseModel):
    plan_id: str
    plan_date: date
    student_name: str
    total_available_minutes: int
    total_planned_minutes: int
    academic_workload_minutes: int
    placement_prep_minutes: int
    buffer_rest_minutes: int
    burnout_risk_score: float = Field(ge=0.0, le=100.0, description="0=Safe, 100=Severe Overload")
    feasibility_rating: str  # "Highly Feasible", "Challenging but Achievable", "Overloaded"
    triage_headline: str
    ai_strategic_summary: str
    items: List[DailyPlanItem]
    protected_mvpt: Optional[DailyPlanItem] = None
    synergies_detected: List[AcademicPlacementSynergy] = []


class WeeklyPlanDay(BaseModel):
    day_name: str
    date_str: str
    academic_minutes: int
    placement_minutes: int
    focus_theme: str
    key_deliverable: str


class WeeklyPlan(BaseModel):
    week_start_date: date
    target_role: str
    weekly_goal_summary: str
    total_academic_hours: float
    total_placement_hours: float
    projected_streak_target: int
    daily_breakdown: List[WeeklyPlanDay]
    milestone_targets: List[str]


# ============================================================================
# Adaptation & Context Payloads
# ============================================================================

class AdaptationTrigger(str, Enum):
    SURPRISE_ASSIGNMENT = "Surprise Academic Assignment"
    ENERGY_DROP_FATIGUE = "Cognitive Exhaustion / Fatigue"
    TASK_OVERRUN = "Academic Task Took Longer Than Estimated"
    MISSED_SESSION = "Missed Scheduled Time Window"
    SUDDEN_FREE_TIME = "Unexpected Free Time Available"


class PlanAdaptationRequest(BaseModel):
    current_plan: DailyPlan
    trigger_event: AdaptationTrigger
    details: Dict[str, Any] = Field(default_factory=dict)
    new_energy_level: Optional[EnergyLevel] = None
    additional_academic_minutes: Optional[int] = None
    new_available_minutes: Optional[int] = None


class PlanAdaptationResponse(BaseModel):
    updated_plan: DailyPlan
    trigger_handled: AdaptationTrigger
    adaptation_summary: str
    tasks_compressed: List[str]
    tasks_deferred: List[str]
    mvpt_adjusted: bool
    guilt_free_reassurance: str


class FullAIPlanningContext(BaseModel):
    student: StudentProfile
    career_goal: CareerGoal
    skills: List[StudentSkillItem]
    academic_tasks: List[AcademicTask]
    schedule_blocks: List[ScheduleBlock] = []
    today_availability: StudyAvailability
    recent_progress: RecentProgress = Field(default_factory=RecentProgress)

