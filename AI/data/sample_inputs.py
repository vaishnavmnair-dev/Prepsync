"""
Realistic student input payloads and test scenarios for the AI Engine.
Includes the canonical Ideathon Demo Student matching the PostgreSQL database seed,
as well as edge-case scenarios (Midterm Exam Crunch, Weekend Sprint, Low Energy Burnout).
"""

from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any


TODAY = date.today()
NOW = datetime.now(timezone.utc)

# ============================================================================
# SCENARIO 1: CANONICAL IDEATHON DEMO STUDENT (Matches DB Seed)
# ============================================================================
DEMO_STUDENT_PAYLOAD: Dict[str, Any] = {
    "student": {
        "student_id": "11111111-1111-1111-1111-111111111111",
        "full_name": "Demo Student",
        "college_name": "Apex Institute of Engineering & Technology",
        "degree": "B.Tech",
        "branch": "CSE (AI & ML)",
        "current_year": 1,
        "current_semester": 1,
        "graduation_year": 2030,
        "daily_available_prep_minutes": 150,
        "preferred_study_hours_per_day": 3.0,
        "timezone": "Asia/Kolkata"
    },
    "career_goal": {
        "role_title": "Software Developer",
        "target_company_type": "Product-based",
        "target_placement_date": (TODAY + timedelta(days=730)).isoformat(),
        "priority_rank": 1,
        "notes": "Targeting Tier-1 and Top Product firms for summer internship & campus placements."
    },
    "skills": [
        {"skill_name": "DSA", "category": "DSA", "current_proficiency": 1, "target_proficiency": 4, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "C/C++", "category": "Programming", "current_proficiency": 3, "target_proficiency": 4, "confidence_level": "High", "assessment_source": "Self Assessment"},
        {"skill_name": "Web Development", "category": "Development", "current_proficiency": 1, "target_proficiency": 3, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "DBMS", "category": "Core CS", "current_proficiency": 0, "target_proficiency": 4, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "Operating Systems", "category": "Core CS", "current_proficiency": 0, "target_proficiency": 3, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "OOP", "category": "Core CS", "current_proficiency": 1, "target_proficiency": 4, "confidence_level": "Medium", "assessment_source": "Self Assessment"},
        {"skill_name": "SQL", "category": "Core CS", "current_proficiency": 0, "target_proficiency": 4, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "Git/GitHub", "category": "Development", "current_proficiency": 1, "target_proficiency": 3, "confidence_level": "Low", "assessment_source": "Self Assessment"},
        {"skill_name": "Aptitude", "category": "Aptitude", "current_proficiency": 2, "target_proficiency": 3, "confidence_level": "Medium", "assessment_source": "Self Assessment"},
        {"skill_name": "Interview Preparation", "category": "Interview", "current_proficiency": 0, "target_proficiency": 4, "confidence_level": "Low", "assessment_source": "Self Assessment"}
    ],
    "academic_tasks": [
        {
            "task_id": "acad-task-001",
            "subject": "Programming in C",
            "task_title": "Pointers and Dynamic Memory Allocation Assignment",
            "task_type": "Assignment",
            "priority": "Critical",
            "difficulty": "Medium",
            "estimated_duration_minutes": 120,
            "remaining_duration_minutes": 60,
            "deadline": (NOW + timedelta(hours=18)).isoformat(),  # Due tomorrow morning!
            "completion_percentage": 50,
            "status": "In Progress"
        },
        {
            "task_id": "acad-task-002",
            "subject": "Data Structures Lab",
            "task_title": "Stack & Queue Infix to Postfix Lab Record Submission",
            "task_type": "Lab",
            "priority": "High",
            "difficulty": "Medium",
            "estimated_duration_minutes": 90,
            "remaining_duration_minutes": 75,
            "deadline": (NOW + timedelta(days=2, hours=10)).isoformat(),  # Due in ~58 hours
            "completion_percentage": 15,
            "status": "In Progress"
        },
        {
            "task_id": "acad-task-003",
            "subject": "Operating Systems",
            "task_title": "CPU Scheduling Algorithms Midterm Exam Prep",
            "task_type": "Exam",
            "priority": "Critical",
            "difficulty": "Hard",
            "estimated_duration_minutes": 240,
            "remaining_duration_minutes": 240,
            "deadline": (NOW + timedelta(days=6)).isoformat(),  # Next week
            "completion_percentage": 0,
            "status": "Not Started"
        }
    ],
    "schedule_blocks": [
        {"day_of_week": "Thursday", "start_time": "09:30", "end_time": "12:30", "activity_name": "Morning Theory Lectures (C & Maths)", "activity_type": "Lecture"},
        {"day_of_week": "Thursday", "start_time": "12:30", "end_time": "13:30", "activity_name": "Lunch & Campus Break", "activity_type": "Other"},
        {"day_of_week": "Thursday", "start_time": "13:30", "end_time": "16:30", "activity_name": "Data Structures Lab Practical", "activity_type": "Lab"},
        {"day_of_week": "Thursday", "start_time": "16:30", "end_time": "17:30", "activity_name": "Commute Back Home / Hostel", "activity_type": "Transit"}
    ],
    "today_availability": {
        "availability_date": TODAY.isoformat(),
        "available_start_time": "18:00",
        "available_end_time": "22:00",
        "available_duration_minutes": 150,  # 2.5 hours net study time
        "energy_level": "Medium",
        "preferred_activity": "Mixed",
        "notes": "College was tiring due to 3-hour afternoon lab, but determined to maintain streak."
    },
    "recent_progress": {
        "total_study_hours_last_7d": 9.5,
        "academic_minutes_last_7d": 380,
        "placement_minutes_last_7d": 190,
        "coding_problems_solved_last_7d": 6,
        "current_streak_days": 4,
        "longest_streak_days": 7
    }
}

# ============================================================================
# SCENARIO 2: MIDTERM CRUNCH (Exhausted, High Academic Load)
# ============================================================================
MIDTERM_CRUNCH_PAYLOAD: Dict[str, Any] = {
    **DEMO_STUDENT_PAYLOAD,
    "today_availability": {
        "availability_date": TODAY.isoformat(),
        "available_start_time": "19:00",
        "available_end_time": "22:00",
        "available_duration_minutes": 90,  # Only 1.5 hours
        "energy_level": "Low",
        "preferred_activity": "Academic Workload",
        "notes": "Midterms tomorrow morning, physically exhausted."
    }
}

# ============================================================================
# SCENARIO 3: WEEKEND SPRINT (High Energy, Placement Acceleration)
# ============================================================================
WEEKEND_SPRINT_PAYLOAD: Dict[str, Any] = {
    **DEMO_STUDENT_PAYLOAD,
    "today_availability": {
        "availability_date": TODAY.isoformat(),
        "available_start_time": "10:00",
        "available_end_time": "18:00",
        "available_duration_minutes": 300,  # 5 hours
        "energy_level": "High",
        "preferred_activity": "Placement Prep",
        "notes": "Saturday free day, ready to do deep DSA and mini-project."
    }
}

