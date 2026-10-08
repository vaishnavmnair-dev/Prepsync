"""
Bandwidth Execution Engine (Dynamic Daily & Weekly Scheduler).
Implements the core cognitive load model, academic triage time-boxing,
Minimum Viable Placement Task (MVPT) streak protection, and realistic feasibility scoring.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
import uuid

from core.models import (
    AcademicPlacementSynergy,
    AcademicTask,
    CareerGoal,
    DailyPlan,
    DailyPlanItem,
    EnergyLevel,
    FullAIPlanningContext,
    SkillGapReportItem,
    StudyAvailability,
    TaskCategory,
    WeeklyPlan,
    WeeklyPlanDay,
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from data.skills_taxonomy import SKILLS_TAXONOMY


class BandwidthEngine:
    """
    Synthesizes academic workload, placement goals, energy levels, and available time
    into a realistic, fatigue-aware daily and weekly execution plan.
    """

    @classmethod
    def generate_daily_plan(cls, context: FullAIPlanningContext) -> DailyPlan:
        student = context.student
        availability = context.today_availability
        career_goal = context.career_goal

        # 1. Evaluate Skill Gaps & Urgencies
        skill_gaps, readiness = SkillAnalyzer.analyze_gaps(context.skills, career_goal)

        # 2. Detect Synergies between College and Placement
        synergies = SynergyDetector.detect_synergies(context.academic_tasks)
        synergy_map = {syn.academic_task_id: syn for syn in synergies}

        # 3. Categorize & Triage Academic Tasks by Deadline
        now = datetime.now(timezone.utc)
        critical_academic: List[Tuple[AcademicTask, float]] = []
        high_academic: List[Tuple[AcademicTask, float]] = []
        medium_academic: List[Tuple[AcademicTask, float]] = []

        for task in context.academic_tasks:
            if task.status in ("Completed", "Cancelled"):
                continue

            # Calculate hours to deadline
            # Ensure timezone awareness
            deadline_tz = task.deadline if task.deadline.tzinfo else task.deadline.replace(tzinfo=timezone.utc)
            hours_left = max(0.1, (deadline_tz - now).total_seconds() / 3600.0)

            if hours_left <= 24.0 or task.priority == "Critical":
                critical_academic.append((task, hours_left))
            elif hours_left <= 48.0 or task.priority == "High":
                high_academic.append((task, hours_left))
            else:
                medium_academic.append((task, hours_left))

        # Sort each group by hours left ascending
        critical_academic.sort(key=lambda x: x[1])
        high_academic.sort(key=lambda x: x[1])
        medium_academic.sort(key=lambda x: x[1])

        # 4. Energy & Bandwidth Allocation
        available_mins = availability.available_duration_minutes
        energy = availability.energy_level

        # Minimum Viable Placement Task (MVPT) duration based on energy
        if energy == EnergyLevel.LOW:
            mvpt_duration = 20  # Low cognitive load 20-min drill
            mvpt_target_intensity = "LOW"
        elif energy == EnergyLevel.MEDIUM:
            mvpt_duration = 35  # 35-min focused concept or medium drill
            mvpt_target_intensity = "MEDIUM"
        else:  # HIGH
            mvpt_duration = 50  # 50-min deep DSA / project feature
            mvpt_target_intensity = "HIGH"

        # Ensure we don't exceed available time
        if available_mins < 45:
            mvpt_duration = 15  # absolute minimum streak protector

        # Academic time-box budget
        academic_budget = max(0, available_mins - mvpt_duration)

        # 5. Select Academic Tasks to Fit in Budget
        planned_academic_items: List[Dict[str, Any]] = []
        used_academic_mins = 0

        # Pass 1: Critical (Due <= 24h)
        for task, hrs in critical_academic:
            needed = task.remaining_duration_minutes
            if used_academic_mins + needed <= academic_budget:
                planned_academic_items.append({
                    "task": task,
                    "allocated_mins": needed,
                    "triage_reason": f"Mandatory compliance: due in {round(hrs, 1)} hrs. Complete remaining {needed} mins to protect internal marks."
                })
                used_academic_mins += needed
            else:
                # Time-box chunking: allocate what remains of budget
                remaining_slot = max(25, academic_budget - used_academic_mins)
                if remaining_slot > 0:
                    planned_academic_items.append({
                        "task": task,
                        "allocated_mins": remaining_slot,
                        "triage_reason": f"Time-boxed to {remaining_slot} mins (Due in {round(hrs, 1)} hrs). Focus strictly on highest-scoring components."
                    })
                    used_academic_mins += remaining_slot
                break

        # Pass 2: High (Due <= 48h) if budget permits
        if used_academic_mins < academic_budget:
            for task, hrs in high_academic:
                needed = task.remaining_duration_minutes
                available_space = academic_budget - used_academic_mins
                if available_space <= 0:
                    break
                alloc = min(needed, available_space)
                planned_academic_items.append({
                    "task": task,
                    "allocated_mins": alloc,
                    "triage_reason": f"Proactive progress: due in {round(hrs, 1)} hrs. Knock out {alloc} mins now to avoid tomorrow's crunch."
                })
                used_academic_mins += alloc

        # 6. Select Top Skill Gap for Protected MVPT
        top_gap_skill = "DSA"
        for gap in skill_gaps:
            if gap.skill_gap > 0:
                top_gap_skill = gap.skill_name
                break

        # Fetch micro-prep templates for this skill
        taxonomy_info = SKILLS_TAXONOMY.get(top_gap_skill, SKILLS_TAXONOMY["DSA"])
        tasks_pool = taxonomy_info.get("micro_prep_tasks", ["Review core algorithmic principles (20 min)"])
        mvpt_title = tasks_pool[0]

        # 7. Build Chronological Time Blocks
        # Parse start time (e.g., "18:00")
        try:
            start_hour, start_minute = map(int, availability.available_start_time.split(":"))
        except Exception:
            start_hour, start_minute = 18, 0

        current_dt = datetime(2026, 1, 1, start_hour, start_minute)
        plan_items: List[DailyPlanItem] = []
        item_order = 1

        # Determine optimal sequencing:
        # If energy is HIGH, do MVPT FIRST (eat the frog).
        # If energy is MEDIUM or LOW, do Urgent Academic first to clear the mental burden, then MVPT.
        do_mvpt_first = (energy == EnergyLevel.HIGH)

        def add_mvpt_item(order_idx: int, cur_dt: datetime) -> Tuple[DailyPlanItem, datetime]:
            end_dt = cur_dt + timedelta(minutes=mvpt_duration)
            item = DailyPlanItem(
                item_order=order_idx,
                task_category=TaskCategory.PLACEMENT,
                task_id=f"mvpt-{top_gap_skill.lower()}",
                title=f"Protected Micro-Prep: {mvpt_title}",
                subject_or_skill=top_gap_skill,
                scheduled_start_time=cur_dt.strftime("%H:%M"),
                scheduled_end_time=end_dt.strftime("%H:%M"),
                planned_duration_minutes=mvpt_duration,
                priority_score=9.5,
                energy_requirement=energy,
                ai_reasoning=(
                    f"Non-negotiable placement momentum: target role '{career_goal.role_title}' requires "
                    f"{top_gap_skill} mastery. Even with college deadlines, this protected {mvpt_duration}-minute "
                    f"block maintains your streak and prevents interview muscle-memory decay."
                ),
                is_mvpt=True,
                status="Scheduled"
            )
            return item, end_dt

        protected_mvpt_ref: Optional[DailyPlanItem] = None

        if do_mvpt_first:
            mvpt_item, current_dt = add_mvpt_item(item_order, current_dt)
            plan_items.append(mvpt_item)
            protected_mvpt_ref = mvpt_item
            item_order += 1
            # Add small 10-min transition buffer
            current_dt += timedelta(minutes=10)

        # Add Academic Tasks
        for p_acad in planned_academic_items:
            task: AcademicTask = p_acad["task"]
            alloc_mins = p_acad["allocated_mins"]
            end_dt = current_dt + timedelta(minutes=alloc_mins)

            synergy = synergy_map.get(task.task_id)
            synergy_tip = synergy.recommended_interview_takeaway if synergy else None

            item = DailyPlanItem(
                item_order=item_order,
                task_category=TaskCategory.ACADEMIC if not synergy else TaskCategory.SYNERGY,
                task_id=task.task_id,
                title=f"{task.subject}: {task.task_title}",
                subject_or_skill=task.subject,
                scheduled_start_time=current_dt.strftime("%H:%M"),
                scheduled_end_time=end_dt.strftime("%H:%M"),
                planned_duration_minutes=alloc_mins,
                priority_score=9.0 if task.priority == "Critical" else 8.0,
                energy_requirement=energy,
                ai_reasoning=p_acad["triage_reason"],
                is_mvpt=False,
                synergy_tip=synergy_tip,
                status="Scheduled"
            )
            plan_items.append(item)
            item_order += 1
            current_dt = end_dt + timedelta(minutes=10)  # 10 min break

        if not do_mvpt_first:
            mvpt_item, current_dt = add_mvpt_item(item_order, current_dt)
            plan_items.append(mvpt_item)
            protected_mvpt_ref = mvpt_item
            item_order += 1

        # 8. Feasibility & Burnout Risk Calculation
        total_planned = sum(i.planned_duration_minutes for i in plan_items)
        buffer_rest = max(0, available_mins - total_planned)

        # Risk score calculation based on ratio of mandatory tasks to capacity and energy level
        load_ratio = total_planned / max(1, available_mins)
        base_risk = min(100.0, load_ratio * 70.0)
        if energy == EnergyLevel.LOW:
            base_risk = min(100.0, base_risk + 25.0)
        elif energy == EnergyLevel.HIGH:
            base_risk = max(5.0, base_risk - 15.0)

        burnout_risk = round(base_risk, 1)

        if burnout_risk < 50:
            feasibility = "Highly Feasible (Balanced & Sustainable)"
        elif burnout_risk < 80:
            feasibility = "Challenging but Achievable (Execute without distractions)"
        else:
            feasibility = "Heavy Load / Triaged (Strictly time-boxed to prevent burnout)"

        # 9. Strategic Summary Headlines
        acad_mins = sum(i.planned_duration_minutes for i in plan_items if i.task_category != TaskCategory.PLACEMENT)
        prep_mins = sum(i.planned_duration_minutes for i in plan_items if i.task_category == TaskCategory.PLACEMENT)

        triage_headline = (
            f"Triaged: {len(planned_academic_items)} Academic Milestones ({acad_mins} min) + "
            f"1 Protected Placement Micro-Prep ({prep_mins} min)"
        )

        strategic_summary = (
            f"Plan built for {student.full_name} targeting {career_goal.role_title}. "
            f"Today's {available_mins}-minute bandwidth is optimized for {energy.value} energy. "
            f"Academic submissions due <= 24 hours are time-boxed to secure grades. "
            f"Placement prep is protected via a focused {mvpt_duration}-minute drill on {top_gap_skill}, "
            f"ensuring your placement runway stays active without mental exhaustion."
        )

        return DailyPlan(
            plan_id=str(uuid.uuid4()),
            plan_date=availability.availability_date,
            student_name=student.full_name,
            total_available_minutes=available_mins,
            total_planned_minutes=total_planned,
            academic_workload_minutes=acad_mins,
            placement_prep_minutes=prep_mins,
            buffer_rest_minutes=buffer_rest,
            burnout_risk_score=burnout_risk,
            feasibility_rating=feasibility,
            triage_headline=triage_headline,
            ai_strategic_summary=strategic_summary,
            items=plan_items,
            protected_mvpt=protected_mvpt_ref,
            synergies_detected=synergies
        )

    @classmethod
    def generate_weekly_plan(cls, context: FullAIPlanningContext) -> WeeklyPlan:
        student = context.student
        career_goal = context.career_goal
        skill_gaps, _ = SkillAnalyzer.analyze_gaps(context.skills, career_goal)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = date.today()
        # Find start of current week
        start_of_week = today - timedelta(days=today.weekday())

        top_gaps = [g.skill_name for g in skill_gaps if g.skill_gap > 0][:4]
        if not top_gaps:
            top_gaps = ["DSA", "Operating Systems", "SQL", "Web Development"]

        daily_breakdown: List[WeeklyPlanDay] = []
        total_acad_hrs = 0.0
        total_prep_hrs = 0.0

        for idx, day_name in enumerate(days):
            cur_date = start_of_week + timedelta(days=idx)
            is_weekend = day_name in ("Saturday", "Sunday")

            if is_weekend:
                acad_min = 60
                prep_min = 180
                theme = "Deep Placement Sprint"
                deliverable = f"Solve 4 Medium {top_gaps[idx % len(top_gaps)]} problems & push git commit"
            elif day_name in ("Monday", "Wednesday"):
                acad_min = 120
                prep_min = 35
                theme = "Academic Triage + Micro-Prep"
                deliverable = f"Complete assignment draft + 30-min {top_gaps[idx % len(top_gaps)]} drill"
            else:
                acad_min = 90
                prep_min = 45
                theme = "Core CS & Lab Synergy"
                deliverable = f"Finish lab submission + review interview questions for {top_gaps[idx % len(top_gaps)]}"

            total_acad_hrs += acad_min / 60.0
            total_prep_hrs += prep_min / 60.0

            daily_breakdown.append(
                WeeklyPlanDay(
                    day_name=day_name,
                    date_str=cur_date.strftime("%b %d, %Y"),
                    academic_minutes=acad_min,
                    placement_minutes=prep_min,
                    focus_theme=theme,
                    key_deliverable=deliverable
                )
            )

        return WeeklyPlan(
            week_start_date=start_of_week,
            target_role=career_goal.role_title,
            weekly_goal_summary=(
                f"Balanced weekly rhythm: {round(total_acad_hrs, 1)}h Academic Compliance + "
                f"{round(total_prep_hrs, 1)}h Protected Placement Runway. 0 broken streaks."
            ),
            total_academic_hours=round(total_acad_hrs, 1),
            total_placement_hours=round(total_prep_hrs, 1),
            projected_streak_target=context.recent_progress.current_streak_days + 7,
            daily_breakdown=daily_breakdown,
            milestone_targets=[
                f"Master core foundations of {top_gaps[0] if top_gaps else 'DSA'}",
                "Ensure 100% on-time college assignment submissions",
                "Log at least 5 consecutive active placement prep days"
            ]
        )

