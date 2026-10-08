"""
Personalized Placement Roadmap Generator.
Transforms skill gaps into a structured, phased master roadmap with chronological
milestones, prerequisite sequencing, and realistic timeframes tailored to the student's runway.
"""

from datetime import date
from typing import Any, Dict, List
from core.models import CareerGoal, SkillGapReportItem, StudentProfile


class PlacementRoadmapGenerator:
    """
    Generates a phase-wise, prerequisite-aware placement preparation roadmap.
    """

    @classmethod
    def generate_roadmap(
        cls,
        student: StudentProfile,
        career_goal: CareerGoal,
        skill_gaps: List[SkillGapReportItem],
    ) -> Dict[str, Any]:
        role = career_goal.role_title
        tier = career_goal.target_company_type.value if hasattr(career_goal.target_company_type, "value") else str(career_goal.target_company_type)

        gap_dict = {item.skill_name: item for item in skill_gaps}

        # Define standard 4-phase progression
        phases = [
            {
                "phase_number": 1,
                "phase_name": "Phase 1: Foundations & Core Language Mastery",
                "focus_theme": "Master 1 programming language, foundational logic, version control & basic linear data structures.",
                "duration_weeks": 4,
                "skills_covered": ["C/C++", "Python", "Git/GitHub"],
                "milestones": [
                    "Complete language syntax, memory model, and standard template library (STL / Python collections).",
                    "Push 2 well-documented repositories to GitHub demonstrating clean Git commits.",
                    "Solve 30 Easy problems on Arrays, Strings, and Two-Pointers."
                ]
            },
            {
                "phase_number": 2,
                "phase_name": "Phase 2: Core DSA & Core Computer Science Foundations",
                "focus_theme": "Non-linear data structures (Trees, Graphs) and high-yield Core CS topics (OS, DBMS, SQL).",
                "duration_weeks": 8,
                "skills_covered": ["DSA", "DBMS", "SQL", "Operating Systems"],
                "milestones": [
                    "Master Recursion, Binary Trees, BST, and Heap operations.",
                    "Complete Graph traversals (BFS, DFS) and shortest path algorithms.",
                    "Design normalized relational schemas (3NF) and write complex SQL joins & window functions.",
                    "Understand OS Process Synchronization, Deadlocks, and Paging concepts."
                ]
            },
            {
                "phase_number": 3,
                "phase_name": "Phase 3: Advanced Problem Solving & Portfolio Project",
                "focus_theme": "Dynamic Programming, Web/Backend Development, and a standout resume project.",
                "duration_weeks": 6,
                "skills_covered": ["DSA", "Web Development", "OOP", "Computer Networks"],
                "milestones": [
                    "Tackle classic 1D & 2D Dynamic Programming patterns.",
                    "Build and deploy a full-stack project with authentication, database integration, and live URL.",
                    "Master OOP design principles (SOLID) and basic Low-Level Design (LLD).",
                    "Draft ATS-friendly 1-page resume using the Google XYZ formula."
                ]
            },
            {
                "phase_number": 4,
                "phase_name": "Phase 4: Placement Sprints, Aptitude & Mock Interviews",
                "focus_theme": "Time-pressured mock tests, company-specific question banks, and behavioral STAR prep.",
                "duration_weeks": 4,
                "skills_covered": ["Aptitude", "Interview Preparation", "DSA"],
                "milestones": [
                    "Complete 10 full-length quantitative and logical aptitude mock tests.",
                    "Conduct 3 peer or AI technical mock interview sessions with live code walkthrough.",
                    "Refine STAR method responses for 5 common behavioral interview questions.",
                    "Solve company-tagged question archives for target companies."
                ]
            }
        ]

        # Calculate phase statuses based on student skill proficiencies
        enriched_phases = []
        for p in phases:
            skills = p["skills_covered"]
            completed_count = 0
            for s in skills:
                gap_item = gap_dict.get(s)
                if gap_item and gap_item.skill_gap == 0:
                    completed_count += 1

            if completed_count == len(skills):
                status = "Completed"
            elif completed_count > 0 or p["phase_number"] == 1:
                status = "In Progress"
            else:
                status = "Upcoming"

            enriched_phases.append({
                **p,
                "status": status,
                "completion_progress_percent": round((completed_count / len(skills)) * 100) if skills else 0
            })

        total_weeks = sum(p["duration_weeks"] for p in phases)

        return {
            "roadmap_title": f"Master Placement Roadmap for {role} ({tier})",
            "student_name": student.full_name,
            "target_role": role,
            "target_company_type": tier,
            "total_estimated_duration_weeks": total_weeks,
            "phases": enriched_phases,
            "success_metrics": [
                "150+ LeetCode problems (60 Easy, 75 Medium, 15 Hard)",
                "1 End-to-end production-grade portfolio project with README & live demo",
                "Proficiency in DBMS, OS, OOP, and SQL interview concepts",
                "Verified ATS-optimized 1-page resume"
            ]
        }

