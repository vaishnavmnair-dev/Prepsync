"""
Database Adapter & SQL Payload Parser.
Bridges the PostgreSQL schema from `01_schema.sql` and `05_ai_planning_context.sql`
with the Python AI engine models.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List
import uuid

from core.models import (
    AcademicTask,
    CareerGoal,
    CompanyTier,
    DailyPlan,
    EnergyLevel,
    FullAIPlanningContext,
    RecentProgress,
    SkillCategory,
    StudentProfile,
    StudentSkillItem,
    StudyAvailability,
)


class DatabaseAdapter:
    """
    Parses PostgreSQL JSON payloads produced by `fn_get_ai_daily_plan_context`
    and maps them to internal Pydantic models.
    """

    @classmethod
    def parse_postgres_payload(cls, payload: Dict[str, Any]) -> FullAIPlanningContext:
        student_raw = payload.get("student", {})
        career_raw = payload.get("career_goal", {})
        avail_raw = payload.get("today_availability", {})
        gaps_raw = payload.get("priority_skill_gaps", []) or []
        acad_raw = payload.get("academic_deadlines", []) or []
        prog_raw = payload.get("recent_progress", {}) or {}

        # 1. Map Student
        student = StudentProfile(
            student_id=str(student_raw.get("student_id", uuid.uuid4())),
            full_name=student_raw.get("full_name", "Student"),
            college_name=student_raw.get("college_name", "College"),
            degree=student_raw.get("degree", "B.Tech"),
            branch=student_raw.get("branch", "CSE"),
            current_year=student_raw.get("current_year", 1),
            current_semester=student_raw.get("current_semester", 1),
            graduation_year=student_raw.get("graduation_year", 2030),
            daily_available_prep_minutes=student_raw.get("daily_available_prep_minutes", 150),
            preferred_study_hours_per_day=float(student_raw.get("preferred_study_hours_per_day", 3.0)),
            timezone=student_raw.get("timezone", "Asia/Kolkata")
        )

        # 2. Map Career Goal
        tier_str = career_raw.get("target_company_type", "Product-based")
        try:
            tier_enum = CompanyTier(tier_str)
        except ValueError:
            tier_enum = CompanyTier.PRODUCT_BASED

        target_date = career_raw.get("target_placement_date")
        if isinstance(target_date, str):
            parsed_date = date.fromisoformat(target_date)
        elif isinstance(target_date, date):
            parsed_date = target_date
        else:
            parsed_date = date.today()

        career_goal = CareerGoal(
            role_title=career_raw.get("primary_goal", "Software Developer"),
            target_company_type=tier_enum,
            target_placement_date=parsed_date,
            priority_rank=career_raw.get("priority_rank", 1)
        )

        # 3. Map Skills
        skills: List[StudentSkillItem] = []
        for g in gaps_raw:
            cat_str = g.get("skill_category", "Programming")
            try:
                cat_enum = SkillCategory(cat_str)
            except ValueError:
                cat_enum = SkillCategory.PROGRAMMING

            skills.append(
                StudentSkillItem(
                    skill_name=g.get("skill_name", "DSA"),
                    category=cat_enum,
                    current_proficiency=int(g.get("current_proficiency", 0)),
                    target_proficiency=int(g.get("required_proficiency", 4)),
                    confidence_level=g.get("confidence_level", "Medium")
                )
            )

        # 4. Map Academic Tasks
        academic_tasks: List[AcademicTask] = []
        now = datetime.now(timezone.utc)
        for a in acad_raw:
            deadline_val = a.get("deadline")
            if isinstance(deadline_val, str):
                try:
                    dt = datetime.fromisoformat(deadline_val.replace("Z", "+00:00"))
                except Exception:
                    dt = now
            elif isinstance(deadline_val, datetime):
                dt = deadline_val
            else:
                dt = now

            academic_tasks.append(
                AcademicTask(
                    task_id=str(a.get("task_id", uuid.uuid4())),
                    subject=a.get("subject", "Academics"),
                    task_title=a.get("task_title", "Assignment"),
                    task_type=a.get("task_type", "Assignment"),
                    priority=a.get("declared_priority", "Medium"),
                    difficulty=a.get("difficulty", "Medium"),
                    estimated_duration_minutes=int(a.get("remaining_duration_minutes", 60)),
                    remaining_duration_minutes=int(a.get("remaining_duration_minutes", 60)),
                    deadline=dt,
                    status=a.get("status", "In Progress")
                )
            )

        # 5. Map Study Availability
        energy_str = avail_raw.get("energy_level", "Medium")
        try:
            energy_enum = EnergyLevel(energy_str)
        except ValueError:
            energy_enum = EnergyLevel.MEDIUM

        today_avail = StudyAvailability(
            availability_date=date.today(),
            available_start_time=avail_raw.get("available_start_time", "18:00")[:5] if avail_raw.get("available_start_time") else "18:00",
            available_end_time=avail_raw.get("available_end_time", "22:00")[:5] if avail_raw.get("available_end_time") else "22:00",
            available_duration_minutes=int(avail_raw.get("available_duration_minutes", 150)),
            energy_level=energy_enum,
            preferred_activity=avail_raw.get("preferred_activity", "Mixed"),
            notes=avail_raw.get("notes")
        )

        # 6. Map Recent Progress
        recent_prog = RecentProgress(
            total_study_hours_last_7d=float(prog_raw.get("total_study_hours_last_7d", 0.0) or 0.0),
            academic_minutes_last_7d=int(prog_raw.get("academic_minutes_last_7d", 0) or 0),
            placement_minutes_last_7d=int(prog_raw.get("placement_minutes_last_7d", 0) or 0),
            coding_problems_solved_last_7d=int(prog_raw.get("coding_problems_solved_last_7d", 0) or 0),
            current_streak_days=int(prog_raw.get("current_streak_days", 0) or 0)
        )

        return FullAIPlanningContext(
            student=student,
            career_goal=career_goal,
            skills=skills,
            academic_tasks=academic_tasks,
            today_availability=today_avail,
            recent_progress=recent_prog
        )

    @classmethod
    def export_plan_to_sql_inserts(cls, plan: DailyPlan, student_id: str) -> str:
        """
        Generates PostgreSQL INSERT statements to persist the AI Daily Plan
        into `daily_plans` and `daily_plan_items` tables.
        """
        sql_lines = []
        plan_id = plan.plan_id
        plan_date = plan.plan_date.isoformat()
        reasoning_escaped = plan.ai_strategic_summary.replace("'", "''")

        sql_lines.append(
            f"INSERT INTO daily_plans (plan_id, student_id, plan_date, total_available_minutes, "
            f"total_planned_minutes, academic_workload_minutes, placement_prep_minutes, plan_status, ai_reasoning) "
            f"VALUES ('{plan_id}', '{student_id}', '{plan_date}', {plan.total_available_minutes}, "
            f"{plan.total_planned_minutes}, {plan.academic_workload_minutes}, {plan.placement_prep_minutes}, "
            f"'Generated', '{reasoning_escaped}') ON CONFLICT (student_id, plan_date) DO UPDATE "
            f"SET total_planned_minutes = EXCLUDED.total_planned_minutes, ai_reasoning = EXCLUDED.ai_reasoning;"
        )

        for item in plan.items:
            cat = "Placement" if item.task_category.value == "Placement" else "Academic"
            title_esc = item.title.replace("'", "''")
            reason_esc = item.ai_reasoning.replace("'", "''")

            # Check if valid UUID or generate new
            item_uuid = str(uuid.uuid4())
            acad_id_val = f"'{item.task_id}'" if (cat == "Academic" and item.task_id and len(item.task_id) == 36) else "NULL"
            learn_id_val = f"'{item.task_id}'" if (cat == "Placement" and item.task_id and len(item.task_id) == 36) else "NULL"

            # If task_id is a placeholder (like acad-task-001 or mvpt-dsa), set FK to NULL and custom title to title
            if acad_id_val != "NULL" and "-" in item.task_id and len(item.task_id) != 36:
                acad_id_val = "NULL"
            if learn_id_val != "NULL" and "-" in item.task_id and len(item.task_id) != 36:
                learn_id_val = "NULL"

            sql_lines.append(
                f"INSERT INTO daily_plan_items (plan_item_id, plan_id, task_category, custom_title, "
                f"scheduled_start_time, scheduled_end_time, planned_duration_minutes, priority_score, "
                f"ai_item_reasoning, status, item_order) VALUES ("
                f"'{item_uuid}', '{plan_id}', '{cat}', '{title_esc}', '{item.scheduled_start_time}:00', "
                f"'{item.scheduled_end_time}:00', {item.planned_duration_minutes}, {item.priority_score}, "
                f"'{reason_esc}', 'Scheduled', {item.item_order});"
            )

        return "\n".join(sql_lines)

