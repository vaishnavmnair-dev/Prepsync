"""
Dynamic Adaptation & Guilt-Free Rescheduling Engine.
Responds dynamically to real-time disruptions (surprise assignments, cognitive fatigue,
task overruns, missed sessions) without guilt or broken streaks.
"""

from datetime import datetime, timedelta
from typing import List
from core.models import (
    AdaptationTrigger,
    DailyPlan,
    DailyPlanItem,
    EnergyLevel,
    PlanAdaptationRequest,
    PlanAdaptationResponse,
    TaskCategory,
)


class AdaptationEngine:
    """
    Dynamically adjusts and reschedules daily plans when real-world constraints change.
    """

    @classmethod
    def adapt_plan(cls, request: PlanAdaptationRequest) -> PlanAdaptationResponse:
        current_plan = request.current_plan
        trigger = request.trigger_event
        items = [item.model_copy() for item in current_plan.items]

        tasks_compressed: List[str] = []
        tasks_deferred: List[str] = []
        mvpt_adjusted = False
        adaptation_summary = ""
        guilt_free_message = ""

        if trigger == AdaptationTrigger.SURPRISE_ASSIGNMENT:
            extra_mins = request.additional_academic_minutes or 45
            # Add surprise academic task
            surprise_title = request.details.get("title", "Surprise Academic Assignment")
            surprise_subject = request.details.get("subject", "College Workload")

            # Compress or drop non-critical items to make space
            # Defer non-urgent academic tasks if any
            for item in items:
                if item.task_category != TaskCategory.PLACEMENT and "Due in" not in item.ai_reasoning:
                    tasks_deferred.append(item.title)
                    items.remove(item)
                    break

            # Compress placement task to 15-minute MVPT to preserve streak
            for item in items:
                if item.task_category == TaskCategory.PLACEMENT:
                    old_dur = item.planned_duration_minutes
                    item.planned_duration_minutes = 15
                    item.title = f"Emergency Streak Protector: {item.subject_or_skill} Concept Drill (15 min)"
                    item.ai_reasoning = (
                        f"Compressed from {old_dur}m to 15m to accommodate urgent surprise assignment. "
                        f"Streak is 100% preserved. Zero guilt."
                    )
                    tasks_compressed.append(f"Placement prep compressed to 15 min")
                    mvpt_adjusted = True

            # Insert surprise academic task at beginning
            surprise_item = DailyPlanItem(
                item_order=1,
                task_category=TaskCategory.ACADEMIC,
                task_id="surprise-acad-001",
                title=f"URGENT: {surprise_subject} - {surprise_title}",
                subject_or_skill=surprise_subject,
                scheduled_start_time="18:30",
                scheduled_end_time="19:15",
                planned_duration_minutes=extra_mins,
                priority_score=10.0,
                energy_requirement=EnergyLevel.MEDIUM,
                ai_reasoning="Urgent college requirement injected. Handled first to protect attendance and grades.",
                is_mvpt=False,
                status="Scheduled"
            )
            items.insert(0, surprise_item)

            adaptation_summary = (
                f"Absorbed {extra_mins}-min surprise college assignment. Placement prep scaled down to "
                f"15-minute streak protector without breaking continuity."
            )
            guilt_free_message = (
                "College surprises happen to every student. You did not fail today's schedule—the engine adapted! "
                "Your placement streak remains active."
            )

        elif trigger == AdaptationTrigger.ENERGY_DROP_FATIGUE:
            # Cognitive burnout detected: downgrade intensity
            for item in items:
                if item.task_category == TaskCategory.PLACEMENT:
                    item.planned_duration_minutes = 15
                    item.energy_requirement = EnergyLevel.LOW
                    item.title = f"Low-Fatigue MVPT: 15-min {item.subject_or_skill} Audio/Flashcard Revision"
                    item.ai_reasoning = "Energy dropped: complex coding replaced with low-cognitive-load review. Streak stays safe."
                    tasks_compressed.append(item.title)
                    mvpt_adjusted = True
                elif item.planned_duration_minutes > 45:
                    # Soft cap academic block
                    old_d = item.planned_duration_minutes
                    item.planned_duration_minutes = max(30, old_d - 20)
                    tasks_compressed.append(f"{item.title} (reduced by 20 min)")

            adaptation_summary = "Fatigue detected: Replaced deep coding with lightweight 15-min review and expanded rest buffer."
            guilt_free_message = "Rest is part of the training cycle. Protecting your energy prevents multi-day burnout."

        elif trigger == AdaptationTrigger.TASK_OVERRUN:
            overrun = request.details.get("overrun_minutes", 30)
            # Find and trim secondary items
            if len(items) > 1:
                last_acad = [it for it in items if it.task_category != TaskCategory.PLACEMENT]
                if last_acad:
                    target = last_acad[-1]
                    tasks_deferred.append(target.title)
                    items.remove(target)

            adaptation_summary = f"Handled {overrun}-min academic task overrun by deferring low-priority reading."
            guilt_free_message = "Assignments often take longer than expected. No problem—tomorrow's buffer will absorb the difference."

        else:
            adaptation_summary = "Adjusted timeline and re-synchronized time slots."
            guilt_free_message = "Timeline re-synced successfully. Ready to execute."

        # Re-index item order and recalculate times
        start_dt = datetime(2026, 1, 1, 18, 30)
        current_dt = start_dt
        for idx, item in enumerate(items, 1):
            item.item_order = idx
            end_dt = current_dt + timedelta(minutes=item.planned_duration_minutes)
            item.scheduled_start_time = current_dt.strftime("%H:%M")
            item.scheduled_end_time = end_dt.strftime("%H:%M")
            current_dt = end_dt + timedelta(minutes=10)

        # Recalculate totals
        tot_planned = sum(i.planned_duration_minutes for i in items)
        acad_mins = sum(i.planned_duration_minutes for i in items if i.task_category != TaskCategory.PLACEMENT)
        prep_mins = sum(i.planned_duration_minutes for i in items if i.task_category == TaskCategory.PLACEMENT)

        updated_plan = current_plan.model_copy(
            update={
                "items": items,
                "total_planned_minutes": tot_planned,
                "academic_workload_minutes": acad_mins,
                "placement_prep_minutes": prep_mins,
                "buffer_rest_minutes": max(0, current_plan.total_available_minutes - tot_planned),
                "feasibility_rating": "Adapted & Feasible (Guilt-Free Rebalance)",
                "burnout_risk_score": max(20.0, current_plan.burnout_risk_score - 15.0),
                "ai_strategic_summary": f"Adapted plan: {adaptation_summary} {guilt_free_message}"
            }
        )

        return PlanAdaptationResponse(
            updated_plan=updated_plan,
            trigger_handled=trigger,
            adaptation_summary=adaptation_summary,
            tasks_compressed=tasks_compressed,
            tasks_deferred=tasks_deferred,
            mvpt_adjusted=mvpt_adjusted,
            guilt_free_reassurance=guilt_free_message
        )

