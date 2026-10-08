"""
Automated Test Suite for Bandwidth AI (PrepPilot Engine).
Tests all algorithms, constraints, cognitive modeling, synergy detection,
scheduling edge cases, and adaptation logic.
"""

from datetime import date, datetime, timedelta, timezone
import unittest

from core.models import (
    AcademicTask,
    AdaptationTrigger,
    CareerGoal,
    CompanyTier,
    EnergyLevel,
    FullAIPlanningContext,
    PlanAdaptationRequest,
    StudentProfile,
    StudentSkillItem,
    StudyAvailability,
    TaskCategory,
)
from core.skill_analyzer import SkillAnalyzer
from core.synergy_detector import SynergyDetector
from core.roadmap_generator import PlacementRoadmapGenerator
from core.bandwidth_engine import BandwidthEngine
from core.adaptation_engine import AdaptationEngine
from core.llm_advisor import LLMAdvisor
from core.db_connector import DatabaseAdapter
from data.sample_inputs import DEMO_STUDENT_PAYLOAD, MIDTERM_CRUNCH_PAYLOAD


class TestBandwidthAIEngine(unittest.TestCase):

    def setUp(self):
        self.context = FullAIPlanningContext(**DEMO_STUDENT_PAYLOAD)

    def test_skill_gap_analysis(self):
        """Test skill gap calculations and readiness percentage."""
        gaps, summary = SkillAnalyzer.analyze_gaps(self.context.skills, self.context.career_goal)

        self.assertGreater(len(gaps), 0)
        self.assertGreater(summary.overall_readiness_percentage, 0.0)
        self.assertLessEqual(summary.overall_readiness_percentage, 100.0)
        self.assertEqual(summary.role_title, "Software Developer")

        # Top gap should have highest urgency score
        for i in range(len(gaps) - 1):
            self.assertGreaterEqual(gaps[i].gap_urgency_score, gaps[i+1].gap_urgency_score)

        # C/C++ was level 3, required is 3 -> gap should be 0 and status "Ready"
        cpp_item = next((g for g in gaps if g.skill_name == "C/C++"), None)
        self.assertIsNotNone(cpp_item)
        self.assertEqual(cpp_item.skill_gap, 0)
        self.assertEqual(cpp_item.status, "Ready")

    def test_tier_modifications(self):
        """Test that FAANG tier boosts DSA required proficiency."""
        faang_goal = CareerGoal(
            role_title="Software Developer",
            target_company_type=CompanyTier.FAANG_TIER1,
            target_placement_date=date.today() + timedelta(days=365)
        )
        gaps, summary = SkillAnalyzer.analyze_gaps(self.context.skills, faang_goal)
        dsa_item = next(g for g in gaps if g.skill_name == "DSA")
        # Base DSA requirement was 4, FAANG tier boosts by +1 -> required 5
        self.assertEqual(dsa_item.required_proficiency, 5)

    def test_synergy_detection(self):
        """Test academic tasks mapping to placement skills with duplicate study time eliminated."""
        synergies = SynergyDetector.detect_synergies(self.context.academic_tasks)
        self.assertGreaterEqual(len(synergies), 2)

        skills_found = [s.relevant_placement_skill for s in synergies]
        self.assertIn("C/C++", skills_found)
        self.assertIn("DSA", skills_found)
        self.assertIn("Operating Systems", skills_found)

        total_saved = sum(s.time_saved_minutes for s in synergies)
        self.assertGreater(total_saved, 100)

    def test_roadmap_generation(self):
        """Test placement roadmap phase structuring and milestones."""
        gaps, _ = SkillAnalyzer.analyze_gaps(self.context.skills, self.context.career_goal)
        roadmap = PlacementRoadmapGenerator.generate_roadmap(
            self.context.student, self.context.career_goal, gaps
        )
        self.assertEqual(len(roadmap["phases"]), 4)
        self.assertEqual(roadmap["phases"][0]["phase_number"], 1)
        self.assertEqual(roadmap["phases"][0]["status"], "In Progress")
        self.assertGreater(roadmap["total_estimated_duration_weeks"], 15)

    def test_bandwidth_daily_scheduling(self):
        """Test that daily plan strictly respects study window and protects MVPT."""
        plan = BandwidthEngine.generate_daily_plan(self.context)

        # Total planned must not exceed available bandwidth
        self.assertLessEqual(plan.total_planned_minutes, plan.total_available_minutes)
        # Academic load must be non-zero
        self.assertGreater(plan.academic_workload_minutes, 0)
        # Placement prep must be non-zero (MVPT protected!)
        self.assertGreater(plan.placement_prep_minutes, 0)
        # Check MVPT flag
        mvpt_items = [item for item in plan.items if item.is_mvpt]
        self.assertEqual(len(mvpt_items), 1)

    def test_energy_level_adaptation(self):
        """Test that low energy scales down MVPT to 20 minutes."""
        low_energy_context = FullAIPlanningContext(**MIDTERM_CRUNCH_PAYLOAD)
        plan = BandwidthEngine.generate_daily_plan(low_energy_context)

        mvpt_item = next(item for item in plan.items if item.is_mvpt)
        self.assertEqual(mvpt_item.planned_duration_minutes, 20)
        self.assertEqual(mvpt_item.energy_requirement, EnergyLevel.LOW)

    def test_adaptation_on_surprise_assignment(self):
        """Test real-time adaptation when sudden college assignment arrives."""
        initial_plan = BandwidthEngine.generate_daily_plan(self.context)
        req = PlanAdaptationRequest(
            current_plan=initial_plan,
            trigger_event=AdaptationTrigger.SURPRISE_ASSIGNMENT,
            details={"title": "Surprise Lab Report", "subject": "Maths"},
            additional_academic_minutes=45
        )
        response = AdaptationEngine.adapt_plan(req)

        self.assertTrue(response.mvpt_adjusted)
        # Ensure streak protector MVPT exists in updated plan
        mvpt_in_adapted = next((item for item in response.updated_plan.items if item.is_mvpt), None)
        self.assertIsNotNone(mvpt_in_adapted)
        self.assertEqual(mvpt_in_adapted.planned_duration_minutes, 15)
        self.assertIn("15 min", response.tasks_compressed[0])

    def test_database_adapter_and_sql_export(self):
        """Test parsing of mock PostgreSQL payload and SQL INSERT generation."""
        mock_pg_payload = {
            "student": {
                "student_id": "11111111-1111-1111-1111-111111111111",
                "full_name": "Demo Student",
                "college_name": "Apex",
                "degree": "B.Tech",
                "branch": "CSE",
                "current_year": 1,
                "current_semester": 1,
                "graduation_year": 2030,
                "daily_available_prep_minutes": 150,
                "preferred_study_hours_per_day": 3.0,
                "timezone": "Asia/Kolkata"
            },
            "career_goal": {
                "primary_goal": "Software Developer",
                "target_company_type": "Product-based",
                "target_placement_date": (date.today() + timedelta(days=300)).isoformat(),
                "priority_rank": 1
            },
            "today_availability": {
                "available_start_time": "18:00:00",
                "available_end_time": "21:00:00",
                "available_duration_minutes": 150,
                "energy_level": "Medium",
                "preferred_activity": "Mixed"
            },
            "priority_skill_gaps": [
                {"skill_name": "DSA", "skill_category": "DSA", "current_proficiency": 1, "required_proficiency": 4, "confidence_level": "Medium"}
            ],
            "academic_deadlines": [
                {
                    "task_id": "11111111-2222-3333-4444-555555555555",
                    "subject": "C Programming",
                    "task_title": "Pointer Lab",
                    "remaining_duration_minutes": 60,
                    "deadline": (datetime.now(timezone.utc) + timedelta(hours=10)).isoformat(),
                    "declared_priority": "Critical"
                }
            ],
            "recent_progress": {
                "total_study_hours_last_7d": 8.0,
                "current_streak_days": 4
            }
        }

        context = DatabaseAdapter.parse_postgres_payload(mock_pg_payload)
        self.assertEqual(context.student.full_name, "Demo Student")
        self.assertEqual(context.career_goal.role_title, "Software Developer")

        plan = BandwidthEngine.generate_daily_plan(context)
        sql = DatabaseAdapter.export_plan_to_sql_inserts(plan, context.student.student_id)
        self.assertIn("INSERT INTO daily_plans", sql)
        self.assertIn("INSERT INTO daily_plan_items", sql)


if __name__ == "__main__":
    unittest.main()

