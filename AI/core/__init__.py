"""
Core modules for Bandwidth AI / PrepPilot Engine.
"""
from core.models import (
    StudentProfile,
    CareerGoal,
    StudentSkillItem,
    AcademicTask,
    StudyAvailability,
    DailyPlan,
    DailyPlanItem,
    WeeklyPlan,
    FullAIPlanningContext,
    EnergyLevel,
    TaskCategory,
    AdaptationTrigger,
    PlanAdaptationRequest,
    PlanAdaptationResponse
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from core.roadmap_generator import PlacementRoadmapGenerator
from core.bandwidth_engine import BandwidthEngine
from core.adaptation_engine import AdaptationEngine
from core.llm_advisor import LLMAdvisor
from core.db_connector import DatabaseAdapter

__all__ = [
    "StudentProfile",
    "CareerGoal",
    "StudentSkillItem",
    "AcademicTask",
    "StudyAvailability",
    "DailyPlan",
    "DailyPlanItem",
    "WeeklyPlan",
    "FullAIPlanningContext",
    "EnergyLevel",
    "TaskCategory",
    "AdaptationTrigger",
    "PlanAdaptationRequest",
    "PlanAdaptationResponse",
    "SkillAnalyzer",
    "SynergyDetector",
    "PlacementRoadmapGenerator",
    "BandwidthEngine",
    "AdaptationEngine",
    "LLMAdvisor",
    "DatabaseAdapter"
]

