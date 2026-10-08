"""AI Bridge Service: Links Relational Database Records with AI Engine Modules."""

import json
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.database.connection import execute_query, fetch_all, fetch_one

# Import AI Engine Models & Algorithms from ../AI/core
from core.models import (
    AcademicPlacementSynergy,
    AcademicTask,
    AdaptationTrigger,
    CareerGoal,
    CompanyTier,
    DailyPlan,
    DailyPlanItem,
    EnergyLevel,
    FullAIPlanningContext,
    PlanAdaptationRequest,
    PlanAdaptationResponse,
    RecentProgress,
    SkillCategory,
    SkillGapReportItem,
    StudentProfile,
    StudentSkillItem,
    StudyAvailability,
    TaskCategory,
    WeeklyPlan,
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from core.roadmap_generator import PlacementRoadmapGenerator
from core.bandwidth_engine import BandwidthEngine
from core.adaptation_engine import AdaptationEngine
from core.llm_advisor import LLMAdvisor


class AIService:
    """
    Bridge connecting backend database tables to the fatigue-aware AI planning algorithms.
    """

    @classmethod
    def build_planning_context(
        cls,
        student_id: str,
        target_date: Optional[date] = None,
        custom_energy: Optional[str] = None,
        custom_avail_minutes: Optional[int] = None
    ) -> FullAIPlanningContext:
        """
        Gathers comprehensive academic, career, and availability state from DB
        to assemble the FullAIPlanningContext required by the AI engine.
        """
        if target_date is None:
            target_date = date.today()

        # 1. Fetch Student Profile
        s_row = fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,))
        if not s_row:
            raise ValueError(f"Student {student_id} not found in database.")

        student = StudentProfile(
            student_id=s_row["student_id"],
            full_name=s_row["full_name"],
            college_name=s_row["college_name"],
            degree=s_row["degree"],
            branch=s_row["branch"],
            current_year=s_row["current_year"],
            current_semester=s_row["current_semester"],
            graduation_year=s_row["graduation_year"],
            daily_available_prep_minutes=s_row["daily_available_prep_minutes"],
            preferred_study_hours_per_day=float(s_row["preferred_study_hours_per_day"]),
            timezone=s_row["timezone"]
        )

        # 2. Fetch Career Goal
        cg_row = fetch_one("""
        SELECT * FROM student_career_goals
        WHERE student_id = ? AND status = 'Active'
        ORDER BY priority_rank ASC LIMIT 1
        """, (student_id,))

        if cg_row:
            try:
                tier = CompanyTier(cg_row["target_company_type"])
            except Exception:
                tier = CompanyTier.PRODUCT_BASED

            try:
                target_p_date = date.fromisoformat(cg_row["target_placement_date"])
            except Exception:
                target_p_date = date.today() + timedelta(days=240)

            career_goal = CareerGoal(
                role_title=cg_row["role_title"],
                target_company_type=tier,
                target_placement_date=target_p_date,
                priority_rank=cg_row["priority_rank"],
                notes=cg_row.get("notes")
            )
        else:
            career_goal = CareerGoal(
                role_title="Software Developer",
                target_company_type=CompanyTier.PRODUCT_BASED,
                target_placement_date=date.today() + timedelta(days=240),
                priority_rank=1
            )

        # 3. Fetch Student Skills
        skill_rows = fetch_all("SELECT * FROM student_skills WHERE student_id = ?", (student_id,))
        skills: List[StudentSkillItem] = []
        for r in skill_rows:
            try:
                cat = SkillCategory(r["category"])
            except Exception:
                cat = SkillCategory.PROGRAMMING

            skills.append(
                StudentSkillItem(
                    skill_name=r["skill_name"],
                    category=cat,
                    current_proficiency=int(r["current_proficiency"]),
                    target_proficiency=int(r["target_proficiency"]),
                    confidence_level=r.get("confidence_level", "Medium"),
                    assessment_source=r.get("assessment_source", "Self Assessment")
                )
            )

        # 4. Fetch Active Academic Tasks
        task_rows = fetch_all("""
        SELECT * FROM academic_tasks
        WHERE student_id = ? AND status != 'Completed'
        ORDER BY deadline ASC
        """, (student_id,))

        now = datetime.now(timezone.utc)
        academic_tasks: List[AcademicTask] = []
        for t in task_rows:
            try:
                deadline_dt = datetime.fromisoformat(t["deadline"])
            except Exception:
                deadline_dt = now + timedelta(days=2)

            academic_tasks.append(
                AcademicTask(
                    task_id=t["task_id"],
                    subject=t["subject"],
                    task_title=t["task_title"],
                    task_type=t["task_type"],
                    priority=t["priority"],
                    difficulty=t["difficulty"],
                    estimated_duration_minutes=int(t["estimated_duration_minutes"]),
                    remaining_duration_minutes=int(t["remaining_duration_minutes"]),
                    deadline=deadline_dt,
                    completion_percentage=int(t.get("completion_percentage", 0)),
                    status=t["status"]
                )
            )

        # 5. Fetch or Build Today's Study Availability
        avail_row = fetch_one("""
        SELECT * FROM study_availability
        WHERE student_id = ? AND availability_date = ?
        """, (student_id, target_date.isoformat()))

        if avail_row:
            energy_val = custom_energy or avail_row["energy_level"]
            duration_val = custom_avail_minutes or avail_row["available_duration_minutes"]
            try:
                energy_enum = EnergyLevel(energy_val)
            except Exception:
                energy_enum = EnergyLevel.MEDIUM

            today_avail = StudyAvailability(
                availability_date=target_date,
                available_start_time=avail_row["available_start_time"],
                available_end_time=avail_row["available_end_time"],
                available_duration_minutes=duration_val,
                energy_level=energy_enum,
                preferred_activity=avail_row.get("preferred_activity", "Mixed"),
                notes=avail_row.get("notes")
            )
        else:
            energy_val = custom_energy or "Medium"
            duration_val = custom_avail_minutes or student.daily_available_prep_minutes
            try:
                energy_enum = EnergyLevel(energy_val)
            except Exception:
                energy_enum = EnergyLevel.MEDIUM

            today_avail = StudyAvailability(
                availability_date=target_date,
                available_start_time="17:30",
                available_end_time="22:30",
                available_duration_minutes=duration_val,
                energy_level=energy_enum,
                preferred_activity="Mixed"
            )

        # 6. Fetch Recent Progress & Streak
        streak_row = fetch_one("SELECT * FROM student_streaks WHERE student_id = ?", (student_id,))
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        logs_7d = fetch_all("""
        SELECT * FROM progress_logs
        WHERE student_id = ? AND created_at >= ?
        """, (student_id, seven_days_ago))

        total_study_mins = sum(int(l["duration_minutes"]) for l in logs_7d)
        acad_mins = sum(int(l["duration_minutes"]) for l in logs_7d if l["task_category"] == "Academic")
        prep_mins = sum(int(l["duration_minutes"]) for l in logs_7d if l["task_category"] == "Placement")
        problems_solved = sum(int(l.get("problems_solved", 0)) for l in logs_7d)

        recent_progress = RecentProgress(
            total_study_hours_last_7d=round(total_study_mins / 60.0, 1),
            academic_minutes_last_7d=acad_mins,
            placement_minutes_last_7d=prep_mins,
            coding_problems_solved_last_7d=problems_solved,
            current_streak_days=streak_row["current_streak_days"] if streak_row else 0,
            longest_streak_days=streak_row["longest_streak_days"] if streak_row else 0
        )

        return FullAIPlanningContext(
            student=student,
            career_goal=career_goal,
            skills=skills,
            academic_tasks=academic_tasks,
            today_availability=today_avail,
            recent_progress=recent_progress
        )

    @classmethod
    def analyze_skills(cls, student_id: str) -> Tuple[List[SkillGapReportItem], Any]:
        """Runs Skill Gap Analysis against target placement benchmarks."""
        context = cls.build_planning_context(student_id)
        gaps, summary = SkillAnalyzer.analyze_gaps(context.skills, context.career_goal)
        return gaps, summary

    @classmethod
    def detect_synergies(cls, student_id: str) -> List[AcademicPlacementSynergy]:
        """Detects high-yield overlaps between academic homework and placement topics."""
        context = cls.build_planning_context(student_id)
        return SynergyDetector.detect_synergies(context.academic_tasks)

    @classmethod
    def generate_and_save_daily_plan(
        cls,
        student_id: str,
        target_date: Optional[date] = None,
        custom_energy: Optional[str] = None,
        custom_avail_minutes: Optional[int] = None
    ) -> DailyPlan:
        """
        Executes Bandwidth Engine daily scheduling and persists the generated
        plan and scheduled items into the database.
        """
        if target_date is None:
            target_date = date.today()

        context = cls.build_planning_context(
            student_id,
            target_date=target_date,
            custom_energy=custom_energy,
            custom_avail_minutes=custom_avail_minutes
        )

        # Generate Fatigue-Aware Schedule
        plan = BandwidthEngine.generate_daily_plan(context)
        now_iso = datetime.now(timezone.utc).isoformat()

        # Reuse existing plan_id if record already exists for this day
        existing_plan = fetch_one(
            "SELECT plan_id FROM daily_plans WHERE student_id = ? AND plan_date = ?",
            (student_id, plan.plan_date.isoformat())
        )
        if existing_plan:
            plan.plan_id = existing_plan["plan_id"]

        # Persist Plan Header into DB
        execute_query("""
        INSERT INTO daily_plans (
            plan_id, student_id, plan_date, total_available_minutes, total_planned_minutes,
            academic_workload_minutes, placement_prep_minutes, buffer_rest_minutes,
            burnout_risk_score, feasibility_rating, triage_headline, ai_strategic_summary,
            plan_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, plan_date) DO UPDATE SET
            total_available_minutes = excluded.total_available_minutes,
            total_planned_minutes = excluded.total_planned_minutes,
            academic_workload_minutes = excluded.academic_workload_minutes,
            placement_prep_minutes = excluded.placement_prep_minutes,
            buffer_rest_minutes = excluded.buffer_rest_minutes,
            burnout_risk_score = excluded.burnout_risk_score,
            feasibility_rating = excluded.feasibility_rating,
            triage_headline = excluded.triage_headline,
            ai_strategic_summary = excluded.ai_strategic_summary,
            plan_status = 'Generated'
        """, (
            plan.plan_id, student_id, plan.plan_date.isoformat(),
            plan.total_available_minutes, plan.total_planned_minutes,
            plan.academic_workload_minutes, plan.placement_prep_minutes, plan.buffer_rest_minutes,
            plan.burnout_risk_score, plan.feasibility_rating, plan.triage_headline,
            plan.ai_strategic_summary, "Generated", now_iso
        ))

        # Clear existing plan items for this plan if regenerating
        execute_query("DELETE FROM daily_plan_items WHERE plan_id = ?", (plan.plan_id,))

        # Persist Granular Items
        for item in plan.items:
            execute_query("""
            INSERT INTO daily_plan_items (
                plan_item_id, plan_id, item_order, task_category, task_id, title,
                subject_or_skill, scheduled_start_time, scheduled_end_time,
                planned_duration_minutes, priority_score, energy_requirement,
                ai_reasoning, is_mvpt, synergy_tip, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()), plan.plan_id, item.item_order, item.task_category.value,
                item.task_id, item.title, item.subject_or_skill, item.scheduled_start_time,
                item.scheduled_end_time, item.planned_duration_minutes, item.priority_score,
                item.energy_requirement.value, item.ai_reasoning, 1 if item.is_mvpt else 0,
                item.synergy_tip, "Scheduled"
            ))

        return plan

    @classmethod
    def generate_and_save_roadmap(cls, student_id: str) -> Dict[str, Any]:
        """Synthesizes and records 4-phase placement roadmap."""
        context = cls.build_planning_context(student_id)
        gaps, _ = SkillAnalyzer.analyze_gaps(context.skills, context.career_goal)
        roadmap = PlacementRoadmapGenerator.generate_roadmap(context.student, context.career_goal, gaps)

        now_iso = datetime.now(timezone.utc).isoformat()
        roadmap_id = str(uuid.uuid4())

        execute_query("""
        INSERT INTO placement_roadmaps (
            roadmap_id, student_id, role_title, target_company_type,
            total_estimated_duration_weeks, phases_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            roadmap_id, student_id, context.career_goal.role_title,
            context.career_goal.target_company_type.value,
            roadmap["total_estimated_duration_weeks"],
            json.dumps(roadmap["phases"]),
            now_iso
        ))

        roadmap["roadmap_id"] = roadmap_id
        return roadmap

    @classmethod
    def adapt_daily_plan(
        cls,
        student_id: str,
        trigger_event: str,
        details: Optional[Dict[str, Any]] = None,
        new_energy_level: Optional[str] = None,
        additional_academic_minutes: Optional[int] = None,
        new_available_minutes: Optional[int] = None
    ) -> PlanAdaptationResponse:
        """
        Adapts today's schedule dynamically in response to surprises, fatigue, or delays,
        persisting changes to the database.
        """
        today_iso = date.today().isoformat()
        plan_row = fetch_one("""
        SELECT plan_id FROM daily_plans WHERE student_id = ? AND plan_date = ?
        """, (student_id, today_iso))

        if not plan_row:
            # Generate initial plan first
            cls.generate_and_save_daily_plan(student_id)
            plan_row = fetch_one("""
            SELECT plan_id FROM daily_plans WHERE student_id = ? AND plan_date = ?
            """, (student_id, today_iso))

        plan_id = plan_row["plan_id"]
        context = cls.build_planning_context(student_id)
        current_plan = BandwidthEngine.generate_daily_plan(context)
        current_plan.plan_id = plan_id

        # Map enum
        try:
            trigger_enum = AdaptationTrigger(trigger_event)
        except Exception:
            trigger_enum = AdaptationTrigger.SURPRISE_ASSIGNMENT

        energy_enum = None
        if new_energy_level:
            try:
                energy_enum = EnergyLevel(new_energy_level)
            except Exception:
                pass

        adapt_request = PlanAdaptationRequest(
            current_plan=current_plan,
            trigger_event=trigger_enum,
            details=details or {},
            new_energy_level=energy_enum,
            additional_academic_minutes=additional_academic_minutes,
            new_available_minutes=new_available_minutes
        )

        response = AdaptationEngine.adapt_plan(adapt_request)
        now_iso = datetime.now(timezone.utc).isoformat()

        # Update Daily Plan in DB
        up_plan = response.updated_plan
        execute_query("""
        UPDATE daily_plans
        SET total_available_minutes = ?, total_planned_minutes = ?,
            academic_workload_minutes = ?, placement_prep_minutes = ?,
            buffer_rest_minutes = ?, ai_strategic_summary = ?,
            plan_status = 'Adapted'
        WHERE plan_id = ?
        """, (
            up_plan.total_available_minutes, up_plan.total_planned_minutes,
            up_plan.academic_workload_minutes, up_plan.placement_prep_minutes,
            up_plan.buffer_rest_minutes, up_plan.ai_strategic_summary, plan_id
        ))

        # Re-save adapted items
        execute_query("DELETE FROM daily_plan_items WHERE plan_id = ?", (plan_id,))
        for item in up_plan.items:
            execute_query("""
            INSERT INTO daily_plan_items (
                plan_item_id, plan_id, item_order, task_category, task_id, title,
                subject_or_skill, scheduled_start_time, scheduled_end_time,
                planned_duration_minutes, priority_score, energy_requirement,
                ai_reasoning, is_mvpt, synergy_tip, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()), plan_id, item.item_order, item.task_category.value,
                item.task_id, item.title, item.subject_or_skill, item.scheduled_start_time,
                item.scheduled_end_time, item.planned_duration_minutes, item.priority_score,
                item.energy_requirement.value, item.ai_reasoning, 1 if item.is_mvpt else 0,
                item.synergy_tip, "Scheduled"
            ))

        # Record Adaptation in Log
        execute_query("""
        INSERT INTO plan_adaptations (
            adaptation_id, plan_id, student_id, trigger_event, adaptation_summary,
            tasks_compressed, tasks_deferred, guilt_free_reassurance, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), plan_id, student_id, trigger_enum.value,
            response.adaptation_summary, json.dumps(response.tasks_compressed),
            json.dumps(response.tasks_deferred), response.guilt_free_reassurance, now_iso
        ))

        return response
