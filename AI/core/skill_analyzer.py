"""
Skill Gap Analysis and Placement Readiness Engine.
Calculates multidimensional skill gaps against career benchmarks,
evaluates role readiness indices, and projects realistic time-to-competence.
"""

from datetime import date
from typing import Dict, List, Tuple
from core.models import (
    CareerGoal,
    CompanyTier,
    ReadinessSummary,
    SkillCategory,
    SkillGapReportItem,
    StudentSkillItem,
)
from data.roles_catalog import ROLE_REQUIREMENTS, TIER_PROFICIENCY_MODIFIERS


class SkillAnalyzer:
    """
    Evaluates current student skill proficiencies against target career role requirements,
    taking into account target company tier standards and runway deadlines.
    """

    @classmethod
    def analyze_gaps(
        cls,
        current_skills: List[StudentSkillItem],
        career_goal: CareerGoal,
    ) -> Tuple[List[SkillGapReportItem], ReadinessSummary]:
        role = career_goal.role_title
        tier = career_goal.target_company_type.value if hasattr(career_goal.target_company_type, "value") else str(career_goal.target_company_type)

        # Lookup role requirements or fallback to Software Developer
        requirements = ROLE_REQUIREMENTS.get(role, ROLE_REQUIREMENTS["Software Developer"])
        tier_mod = TIER_PROFICIENCY_MODIFIERS.get(tier, TIER_PROFICIENCY_MODIFIERS["Product-based"])

        # Map current skills by name
        student_skill_map: Dict[str, StudentSkillItem] = {
            s.skill_name.strip().lower(): s for s in current_skills
        }

        gap_reports: List[SkillGapReportItem] = []
        total_possible_score = 0.0
        student_achieved_score = 0.0
        total_hours_needed = 0
        critical_gaps_count = 0

        hours_per_level = tier_mod.get("hours_per_proficiency_level", 30)

        for req in requirements:
            skill_name = req["skill_name"]
            req_key = skill_name.strip().lower()
            category_str = req["category"]
            base_required = req["required_proficiency"]
            base_weight = req["weight"]
            importance = req["importance"]
            order = req["recommended_order"]

            # Tier modifications
            adjusted_required = base_required
            if category_str == "DSA" and "dsa_boost" in tier_mod:
                adjusted_required += tier_mod["dsa_boost"]
            elif category_str == "Development" and "dev_boost" in tier_mod:
                adjusted_required += tier_mod["dev_boost"]
            elif category_str == "Core CS" and "core_cs_boost" in tier_mod:
                adjusted_required += tier_mod["core_cs_boost"]
            elif category_str == "Aptitude" and "aptitude_boost" in tier_mod:
                adjusted_required += tier_mod["aptitude_boost"]

            adjusted_required = max(1, min(5, adjusted_required))

            # Current student proficiency
            student_skill = student_skill_map.get(req_key)
            current_prof = student_skill.current_proficiency if student_skill else 0

            gap = max(0, adjusted_required - current_prof)
            urgency_score = round(gap * base_weight * tier_mod.get("urgency_multiplier", 1.0), 2)

            # Cumulative scoring for readiness calculation
            max_skill_score = adjusted_required * base_weight
            student_skill_score = min(adjusted_required, current_prof) * base_weight
            total_possible_score += max_skill_score
            student_achieved_score += student_skill_score

            # Hours estimation
            hours_needed = gap * hours_per_level
            total_hours_needed += hours_needed

            if gap >= 2 and importance in ("Critical", "High"):
                status = "Critical Gap"
                critical_gaps_count += 1
            elif gap > 0:
                status = "Needs Practice"
            else:
                status = "Ready"

            # Parse category safely into enum
            try:
                cat_enum = SkillCategory(category_str)
            except ValueError:
                cat_enum = SkillCategory.PROGRAMMING

            gap_reports.append(
                SkillGapReportItem(
                    skill_name=skill_name,
                    category=cat_enum,
                    current_proficiency=current_prof,
                    required_proficiency=adjusted_required,
                    skill_gap=gap,
                    importance_level=importance,
                    weight_score=base_weight,
                    gap_urgency_score=urgency_score,
                    recommended_focus_order=order,
                    status=status
                )
            )

        # Sort gaps by urgency score descending
        gap_reports.sort(key=lambda x: (x.gap_urgency_score, x.recommended_focus_order), reverse=True)

        # Calculate readiness percentage
        readiness_pct = (
            round((student_achieved_score / total_possible_score) * 100, 1)
            if total_possible_score > 0
            else 0.0
        )

        # Months and weeks remaining
        today = date.today()
        target_date = career_goal.target_placement_date
        days_remaining = max(1, (target_date - today).days)
        months_remaining = round(days_remaining / 30.4, 1)

        # Assuming 2 hours of prep per day (14 hrs/week) baseline pace
        est_weeks = round(total_hours_needed / 14.0, 1)

        # Feasibility classification
        weeks_available = days_remaining / 7.0
        if est_weeks <= weeks_available * 0.75:
            feasibility = "On Track (Comfortable Runway)"
        elif est_weeks <= weeks_available:
            feasibility = "Tight Schedule (Requires Consistent Micro-Prep)"
        else:
            feasibility = "High Risk / Acceleration Needed (Expand Daily Study Bandwidth)"

        readiness_summary = ReadinessSummary(
            overall_readiness_percentage=readiness_pct,
            role_title=role,
            target_company_type=tier,
            months_until_placement=months_remaining,
            estimated_prep_hours_needed=total_hours_needed,
            estimated_weeks_to_ready=est_weeks,
            feasibility_status=feasibility,
            critical_gaps_count=critical_gaps_count,
            total_skills_evaluated=len(gap_reports)
        )

        return gap_reports, readiness_summary

