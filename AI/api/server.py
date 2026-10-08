"""
FastAPI Server for Bandwidth AI (PrepPilot Engine).
Exposes REST endpoints for skill gap analysis, personalized roadmaps,
synergy detection, dynamic fatigue-aware daily/weekly planning, and real-time adaptation.
"""

from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.models import (
    AdaptationTrigger,
    CareerGoal,
    DailyPlan,
    EnergyLevel,
    FullAIPlanningContext,
    PlanAdaptationRequest,
    PlanAdaptationResponse,
    StudentProfile,
    StudentSkillItem,
    StudyAvailability,
    WeeklyPlan,
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from core.roadmap_generator import PlacementRoadmapGenerator
from core.bandwidth_engine import BandwidthEngine
from core.adaptation_engine import AdaptationEngine
from core.llm_advisor import LLMAdvisor
from core.db_connector import DatabaseAdapter
from data.sample_inputs import DEMO_STUDENT_PAYLOAD, MIDTERM_CRUNCH_PAYLOAD


app = FastAPI(
    title="Bandwidth AI (PrepPilot) - Placement Companion Engine",
    description="The Fatigue-Aware Execution Engine that Bridges Academic Workload and Placement Preparation.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request schemas for standalone endpoints
class AnalyzeRequest(BaseModel):
    skills: List[StudentSkillItem]
    career_goal: CareerGoal


class RoadmapRequest(BaseModel):
    student: StudentProfile
    career_goal: CareerGoal
    skills: List[StudentSkillItem]


class MicroDrillRequest(BaseModel):
    skill_name: str = "DSA"
    energy_level: EnergyLevel = EnergyLevel.MEDIUM


@app.get("/")
def root():
    return {
        "engine": "Bandwidth AI (PrepPilot)",
        "status": "online",
        "version": "1.0.0",
        "purpose": "Bridging the Gap Between College Workload and Placement Preparation",
        "endpoints": [
            "/api/v1/profile/analyze",
            "/api/v1/roadmap/generate",
            "/api/v1/synergy/detect",
            "/api/v1/plan/daily",
            "/api/v1/plan/weekly",
            "/api/v1/plan/adapt",
            "/api/v1/coach/micro-drill",
            "/api/v1/db/context-plan",
            "/api/v1/demo"
        ]
    }


@app.post("/api/v1/profile/analyze")
def analyze_skill_gaps(req: AnalyzeRequest):
    """
    Evaluates student proficiency against industry benchmarks for target career role.
    Returns ranked skill gaps and overall placement readiness index.
    """
    try:
        gaps, summary = SkillAnalyzer.analyze_gaps(req.skills, req.career_goal)
        return {
            "readiness_summary": summary,
            "skill_gaps": gaps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/roadmap/generate")
def generate_placement_roadmap(req: RoadmapRequest):
    """
    Synthesizes a personalized 4-phase placement preparation roadmap with chronological milestones.
    """
    try:
        gaps, _ = SkillAnalyzer.analyze_gaps(req.skills, req.career_goal)
        roadmap = PlacementRoadmapGenerator.generate_roadmap(req.student, req.career_goal, gaps)
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/synergy/detect")
def detect_academic_synergies(tasks: List[Any]):
    """
    Identifies direct overlaps where college homework/labs fulfill interview topics.
    """
    try:
        # Convert raw dicts or objects into AcademicTasks
        academic_tasks = []
        for t in tasks:
            if hasattr(t, "subject"):
                academic_tasks.append(t)
            else:
                academic_tasks.append(AcademicTask(**t))
        synergies = SynergyDetector.detect_synergies(academic_tasks)
        return {
            "synergies_detected_count": len(synergies),
            "synergies": synergies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan/daily", response_model=DailyPlan)
def generate_daily_plan(context: FullAIPlanningContext):
    """
    Generates a realistic, fatigue-aware daily schedule balancing Academic Triage and Protected Micro-Prep (MVPT).
    """
    try:
        plan = BandwidthEngine.generate_daily_plan(context)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan/weekly", response_model=WeeklyPlan)
def generate_weekly_plan(context: FullAIPlanningContext):
    """
    Generates a 7-day adaptive schedule balancing lecture/lab days and weekend deep-work sprints.
    """
    try:
        plan = BandwidthEngine.generate_weekly_plan(context)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/plan/adapt", response_model=PlanAdaptationResponse)
def adapt_plan_dynamically(request: PlanAdaptationRequest):
    """
    Dynamically recalculates schedule when disruptions occur (surprise assignment, fatigue, overrun)
    without guilt or broken streaks.
    """
    try:
        response = AdaptationEngine.adapt_plan(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/coach/micro-drill")
def get_micro_drill(req: MicroDrillRequest):
    """
    Returns a bite-sized 15-30 minute interview drill tailored to remaining mental energy.
    """
    try:
        drill = LLMAdvisor.generate_micro_drill(req.skill_name, req.energy_level)
        return {
            "skill": req.skill_name,
            "energy_level": req.energy_level.value,
            "drill": drill
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/db/context-plan")
def plan_from_postgres_payload(payload: Dict[str, Any]):
    """
    Accepts raw JSON output from PostgreSQL `05_ai_planning_context.sql` query
    and outputs both the AI plan and ready-to-run PostgreSQL INSERT queries.
    """
    try:
        context = DatabaseAdapter.parse_postgres_payload(payload)
        plan = BandwidthEngine.generate_daily_plan(context)
        sql_inserts = DatabaseAdapter.export_plan_to_sql_inserts(plan, context.student.student_id)
        return {
            "daily_plan": plan,
            "sql_inserts": sql_inserts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/demo")
def run_full_simulation():
    """
    Executes a complete simulated workflow of the Ideathon Demo Student scenario:
    1. Skill gap & readiness analysis
    2. Academic-placement synergy detection
    3. Daily plan with triage & protected MVPT
    4. Simulated sudden disruption adaptation
    """
    context = FullAIPlanningContext(**DEMO_STUDENT_PAYLOAD)

    # 1. Gaps
    gaps, readiness = SkillAnalyzer.analyze_gaps(context.skills, context.career_goal)

    # 2. Synergies
    synergies = SynergyDetector.detect_synergies(context.academic_tasks)

    # 3. Daily Plan
    daily_plan = BandwidthEngine.generate_daily_plan(context)

    # 4. Weekly Plan
    weekly_plan = BandwidthEngine.generate_weekly_plan(context)

    # 5. Strategic Advice
    coach_advice = LLMAdvisor.generate_coach_guidance(context)

    # 6. Adaptation Simulation: Surprise Assignment arrives!
    adapt_req = PlanAdaptationRequest(
        current_plan=daily_plan,
        trigger_event=AdaptationTrigger.SURPRISE_ASSIGNMENT,
        details={"title": "Emergency C Lab Record", "subject": "Data Structures"},
        additional_academic_minutes=45
    )
    adapted_plan_response = AdaptationEngine.adapt_plan(adapt_req)

    return {
        "scenario": "B.Tech Demo Student (Semester 1 CSE AI&ML, SDE Target)",
        "readiness_summary": readiness,
        "synergies_detected": synergies,
        "daily_plan": daily_plan,
        "weekly_plan": weekly_plan,
        "coach_advice": coach_advice,
        "adaptation_simulation": {
            "trigger": "Surprise 45-min assignment assigned at 6 PM",
            "result_summary": adapted_plan_response.adaptation_summary,
            "guilt_free_reassurance": adapted_plan_response.guilt_free_reassurance,
            "tasks_compressed": adapted_plan_response.tasks_compressed,
            "adapted_items": adapted_plan_response.updated_plan.items
        }
    }

