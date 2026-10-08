"""
Interactive Terminal CLI for Bandwidth AI (PrepPilot).
Demonstrates the complete AI engine live:
1. Multidimensional Skill Gap & Readiness Index
2. Academic-Placement Overlap / Synergy Detection
3. Phased 4-Phase Placement Roadmap
4. Cognitive-Aware Daily Schedule with Protected MVPT
5. Guilt-Free Dynamic Adaptation & Rescheduling
6. Live Interview Micro-Drill
7. SQL Synchronization Export
"""

import argparse
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
from datetime import date
from typing import Dict, Any

from core.models import (
    AdaptationTrigger,
    EnergyLevel,
    FullAIPlanningContext,
    PlanAdaptationRequest,
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from core.roadmap_generator import PlacementRoadmapGenerator
from core.bandwidth_engine import BandwidthEngine
from core.adaptation_engine import AdaptationEngine
from core.llm_advisor import LLMAdvisor
from core.db_connector import DatabaseAdapter
from data.sample_inputs import (
    DEMO_STUDENT_PAYLOAD,
    MIDTERM_CRUNCH_PAYLOAD,
    WEEKEND_SPRINT_PAYLOAD,
)


# Terminal ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"


def print_banner():
    banner = f"""
{CYAN}{BOLD}================================================================================
   BANDWIDTH AI (PrepPilot) - COLLEGE & PLACEMENT COMPANION ENGINE
   "The Fatigue-Aware Execution Engine that Protects Your Placement Runway"
================================================================================{RESET}
"""
    print(banner)


def display_readiness(readiness, gaps):
    print(f"\n{BOLD}{MAGENTA}--- [1] MULTIDIMENSIONAL SKILL GAP & READINESS ANALYSIS ---{RESET}")
    print(f"Target Career Role: {BOLD}{readiness.role_title}{RESET} | Company Tier: {BOLD}{readiness.target_company_type}{RESET}")
    print(f"Overall Placement Readiness Index: {BOLD}{readiness.overall_readiness_percentage}%{RESET}")
    print(f"Feasibility Status: {GREEN if 'On Track' in readiness.feasibility_status else YELLOW}{readiness.feasibility_status}{RESET}")
    print(f"Total Prep Hours Needed: {readiness.estimated_prep_hours_needed} hrs | Estimated Weeks: {readiness.estimated_weeks_to_ready} weeks")
    print(f"Months Remaining on Runway: {readiness.months_until_placement} months")
    print(f"Critical Gaps: {RED}{readiness.critical_gaps_count}{RESET} / {readiness.total_skills_evaluated} skills evaluated\n")

    print(f"{'SKILL NAME':<20} | {'CATEGORY':<12} | {'CURRENT':<8} | {'TARGET':<8} | {'GAP':<6} | {'STATUS':<15} | {'URGENCY'}")
    print("-" * 88)
    for g in gaps:
        status_col = GREEN if g.status == "Ready" else (RED if g.status == "Critical Gap" else YELLOW)
        print(
            f"{g.skill_name:<20} | {g.category.value:<12} | {g.current_proficiency:<8} | "
            f"{g.required_proficiency:<8} | {g.skill_gap:<6} | {status_col}{g.status:<15}{RESET} | {g.gap_urgency_score}"
        )


def display_synergies(synergies):
    print(f"\n{BOLD}{CYAN}--- [2] ACADEMIC-PLACEMENT OVERLAP DETECTOR (SYNERGIES) ---{RESET}")
    print(f"Identified {len(synergies)} areas where college homework directly builds placement interview skills:\n")
    total_saved = sum(s.time_saved_minutes for s in synergies)
    for idx, syn in enumerate(synergies, 1):
        print(f"{BOLD}{idx}. College Task:{RESET} {syn.academic_subject} - {syn.academic_task_title}")
        print(f"   {BLUE}-> Maps to Placement Skill:{RESET} {BOLD}{syn.relevant_placement_skill}{RESET} ({syn.synergy_type})")
        print(f"   {GREEN}-> Time Saved:{RESET} ~{syn.time_saved_minutes} mins of duplicate placement study")
        print(f"   {YELLOW}-> Interview Angle:{RESET} {syn.recommended_interview_takeaway}\n")
    print(f"{BOLD}Total Duplicate Study Time Eliminated: {GREEN}{total_saved} minutes{RESET}\n")


def display_roadmap(roadmap):
    print(f"\n{BOLD}{BLUE}--- [3] PERSONALIZED PLACEMENT ROADMAP ---{RESET}")
    print(f"Title: {roadmap['roadmap_title']}")
    print(f"Total Duration: {roadmap['total_estimated_duration_weeks']} weeks\n")
    for phase in roadmap["phases"]:
        status_col = GREEN if phase["status"] == "Completed" else (CYAN if phase["status"] == "In Progress" else YELLOW)
        print(f"{BOLD}{phase['phase_name']}{RESET} [{status_col}{phase['status']}{RESET} - {phase['completion_progress_percent']}%]")
        print(f"Focus: {phase['focus_theme']}")
        print(f"Duration: {phase['duration_weeks']} weeks | Skills: {', '.join(phase['skills_covered'])}")
        print("Key Milestones:")
        for m in phase["milestones"]:
            print(f"  * {m}")
        print()


def display_daily_plan(plan: Any):
    print(f"\n{BOLD}{GREEN}--- [4] FATIGUE-AWARE DAILY PLAN (BANDWIDTH ENGINE) ---{RESET}")
    print(f"Date: {plan.plan_date} | Student: {plan.student_name}")
    print(f"Available Bandwidth: {plan.total_available_minutes} mins | Planned: {plan.total_planned_minutes} mins | Buffer: {plan.buffer_rest_minutes} mins")
    print(f"Academic Load: {plan.academic_workload_minutes} mins | Placement Micro-Prep: {plan.placement_prep_minutes} mins")
    print(f"Feasibility Rating: {BOLD}{plan.feasibility_rating}{RESET}")
    print(f"Burnout Risk Score: {RED if plan.burnout_risk_score > 70 else (YELLOW if plan.burnout_risk_score > 40 else GREEN)}{plan.burnout_risk_score}%{RESET}")
    print(f"Triage Headline: {BOLD}{plan.triage_headline}{RESET}")
    print(f"Strategic Rationale: {plan.ai_strategic_summary}\n")

    print(f"{'#':<3} | {'TIME':<13} | {'DUR':<6} | {'CATEGORY':<10} | {'TASK & DETAILS'}")
    print("-" * 88)
    for item in plan.items:
        cat_badge = (
            f"{GREEN}[PLACEMENT]{RESET}"
            if item.task_category.value == "Placement"
            else (f"{CYAN}[SYNERGY]{RESET}" if item.task_category.value == "Synergy" else f"{YELLOW}[ACADEMIC]{RESET}")
        )
        mvpt_star = f" {BOLD}{RED}[* PROTECTED MVPT]{RESET}" if item.is_mvpt else ""
        print(f"{item.item_order:<3} | {item.scheduled_start_time}-{item.scheduled_end_time} | {item.planned_duration_minutes}m   | {cat_badge:<19} | {BOLD}{item.title}{RESET}{mvpt_star}")
        print(f"    Reasoning: {item.ai_reasoning}")
        if item.synergy_tip:
            print(f"    {CYAN}Overlap Insight: {item.synergy_tip}{RESET}")
        print()


def simulate_adaptation(daily_plan):
    print(f"\n{BOLD}{RED}--- [5] REAL-TIME SIMULATION: SURPRISE DISRUPTION & GUILT-FREE ADAPTATION ---{RESET}")
    print(f"{YELLOW}Scenario: At 6:00 PM, college professor assigns a surprise 45-minute C programming record due tomorrow morning!{RESET}")
    print("Normal student reaction: Placement prep abandoned, streak broken, guilt accumulates.")
    print(f"{GREEN}Bandwidth AI reaction: Real-time re-triage + MVPT compression to 15 min (Streak 100% saved!){RESET}\n")

    adapt_req = PlanAdaptationRequest(
        current_plan=daily_plan,
        trigger_event=AdaptationTrigger.SURPRISE_ASSIGNMENT,
        details={"title": "Emergency C Programming Record", "subject": "Programming in C"},
        additional_academic_minutes=45
    )

    resp = AdaptationEngine.adapt_plan(adapt_req)
    print(f"{BOLD}Adaptation Summary:{RESET} {resp.adaptation_summary}")
    print(f"{BOLD}Guilt-Free Message:{RESET} {GREEN}{resp.guilt_free_reassurance}{RESET}")
    print(f"Tasks Compressed: {resp.tasks_compressed}")
    print(f"Tasks Deferred: {resp.tasks_deferred or ['None - all fitted via compression']}")

    print(f"\n{BOLD}Updated Dynamic Timeline:{RESET}")
    for item in resp.updated_plan.items:
        mvpt_badge = " (Streak Protector)" if item.is_mvpt else ""
        print(f"  [{item.scheduled_start_time} - {item.scheduled_end_time}] ({item.planned_duration_minutes}m) - {item.title}{mvpt_badge}")


def display_micro_drill(energy: EnergyLevel):
    print(f"\n{BOLD}{YELLOW}--- [6] DAILY 15-MIN INTERVIEW MICRO-DRILL (FOR MVPT SLOT) ---{RESET}")
    drill = LLMAdvisor.generate_micro_drill("DSA", energy)
    print(f"Drill Title: {BOLD}{drill['title']}{RESET} ({drill['estimated_minutes']} min)")
    print(f"Question: {drill['question']}")
    print(f"Hint 1: {drill['hint_1']}")
    print(f"Hint 2: {drill['hint_2']}")
    print(f"Interview Relevance: {GREEN}{drill['interview_takeaway']}{RESET}")
    if drill.get("sample_code"):
        print(f"\nOptimal Solution Pattern:\n{CYAN}{drill['sample_code']}{RESET}")


def run_full_pipeline(scenario_name: str = "demo"):
    print_banner()

    if scenario_name == "midterm":
        payload = MIDTERM_CRUNCH_PAYLOAD
        print(f"{YELLOW}[Active Scenario]: Midterm Exam Crunch (Low Energy, Heavy Academic Workload){RESET}\n")
    elif scenario_name == "weekend":
        payload = WEEKEND_SPRINT_PAYLOAD
        print(f"{GREEN}[Active Scenario]: Weekend Placement Sprint (High Energy, 5 Hours Available){RESET}\n")
    else:
        payload = DEMO_STUDENT_PAYLOAD
        print(f"{CYAN}[Active Scenario]: Ideathon Canonical Demo Student (Semester 1 B.Tech CSE AI&ML){RESET}\n")

    context = FullAIPlanningContext(**payload)

    # 1. Skill Gaps & Readiness
    gaps, readiness = SkillAnalyzer.analyze_gaps(context.skills, context.career_goal)
    display_readiness(readiness, gaps)

    # 2. Synergies
    synergies = SynergyDetector.detect_synergies(context.academic_tasks)
    display_synergies(synergies)

    # 3. Roadmap
    roadmap = PlacementRoadmapGenerator.generate_roadmap(context.student, context.career_goal, gaps)
    display_roadmap(roadmap)

    # 4. Daily Plan
    daily_plan = BandwidthEngine.generate_daily_plan(context)
    display_daily_plan(daily_plan)

    # 5. Dynamic Adaptation Simulation
    simulate_adaptation(daily_plan)

    # 6. Micro-Drill
    display_micro_drill(context.today_availability.energy_level)

    # 7. AI Advisor Quote
    coach_advice = LLMAdvisor.generate_coach_guidance(context)
    print(f"\n{BOLD}{MAGENTA}--- [7] AI ADVISOR STRATEGIC COACHING ---{RESET}")
    print(f"\"{coach_advice}\"\n")

    # 8. PostgreSQL SQL Export
    sql_statements = DatabaseAdapter.export_plan_to_sql_inserts(daily_plan, context.student.student_id)
    print(f"{BOLD}{BLUE}--- [8] POSTGRESQL INSERT STATEMENTS (READY FOR DB EXECUTION) ---{RESET}")
    print(f"Generated {len(sql_statements.splitlines())} SQL statements syncing AI plan with database.\n")


def main():
    parser = argparse.ArgumentParser(description="Bandwidth AI (PrepPilot) Execution Engine CLI")
    parser.add_argument("--scenario", choices=["demo", "midterm", "weekend"], default="demo", help="Choose student scenario")
    args = parser.parse_args()

    run_full_pipeline(args.scenario)


if __name__ == "__main__":
    main()
