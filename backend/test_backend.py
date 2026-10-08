"""Comprehensive End-to-End Test Suite for PrepPilot Backend."""

import asyncio
import json
from typing import Any, Dict, Optional
import unittest

from app.main import app
from app.database.init_db import setup_database


class ASGIClient:
    """Zero-dependency ASGI Test Client that interacts directly with FastAPI app."""

    def __init__(self, application):
        self.app = application

    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        token: Optional[str] = None
    ) -> tuple[int, Dict[str, Any]]:
        body = json.dumps(json_data).encode("utf-8") if json_data is not None else b""
        req_headers = []
        if headers:
            for k, v in headers.items():
                req_headers.append((k.lower().encode("utf-8"), v.encode("utf-8")))

        if json_data is not None:
            req_headers.append((b"content-type", b"application/json"))
        if token:
            req_headers.append((b"authorization", f"Bearer {token}".encode("utf-8")))

        scope = {
            "type": "http",
            "method": method.upper(),
            "path": path,
            "headers": req_headers,
            "query_string": b""
        }

        response_status = 500
        response_body = bytearray()

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_status, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        await self.app(scope, receive, send)

        try:
            parsed = json.loads(response_body.decode("utf-8")) if response_body else {}
        except Exception:
            parsed = {"raw": response_body.decode("utf-8", errors="ignore")}

        return response_status, parsed

    def get(self, path: str, token: Optional[str] = None):
        return asyncio.run(self.request("GET", path, token=token))

    def post(self, path: str, json_data: Optional[Dict[str, Any]] = None, token: Optional[str] = None):
        return asyncio.run(self.request("POST", path, json_data=json_data, token=token))

    def put(self, path: str, json_data: Optional[Dict[str, Any]] = None, token: Optional[str] = None):
        return asyncio.run(self.request("PUT", path, json_data=json_data, token=token))

    def delete(self, path: str, token: Optional[str] = None):
        return asyncio.run(self.request("DELETE", path, token=token))


class TestPrepPilotBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize and seed database
        setup_database()
        cls.client = ASGIClient(app)

    def test_01_root_and_health(self):
        """Test system root and health endpoints."""
        status_code, body = self.client.get("/")
        self.assertEqual(status_code, 200)
        self.assertEqual(body["status"], "online")
        self.assertIn("endpoints", body)

        status_code, body = self.client.get("/health")
        self.assertEqual(status_code, 200)
        self.assertEqual(body["status"], "healthy")

    def test_02_auth_login_demo(self):
        """Test login with seeded demo account."""
        status_code, body = self.client.post("/api/v1/auth/login", {
            "email": "demo@preppilot.com",
            "password": "password123"
        })
        self.assertEqual(status_code, 200)
        self.assertIn("token", body)
        self.assertEqual(body["student"]["full_name"], "Aarav Sharma")
        demo_token = body["token"]

        # Test auth/me with valid token
        status_code, me_body = self.client.get("/api/v1/auth/me", token=demo_token)
        self.assertEqual(status_code, 200)
        self.assertEqual(me_body["student"]["email"], "demo@preppilot.com")
        self.assertIsNotNone(me_body["career_goal"])

    def test_03_auth_signup_new_student(self):
        """Test student registration workflow."""
        import random
        rand_id = random.randint(1000, 9999)
        test_email = f"student_{rand_id}@nit.edu"

        status_code, body = self.client.post("/api/v1/auth/signup", {
            "email": test_email,
            "password": "securePassWord1!",
            "full_name": "Priya Patel",
            "college_name": "NIT Surathkal",
            "degree": "B.Tech",
            "branch": "Artificial Intelligence & Data Science",
            "current_year": 3,
            "current_semester": 5,
            "graduation_year": 2026,
            "daily_available_prep_minutes": 180,
            "preferred_study_hours_per_day": 3.5,
            "target_role": "AI / ML Engineer",
            "target_company_type": "FAANG / Tier-1"
        })
        self.assertEqual(status_code, 201)
        self.assertIn("token", body)
        token = body["token"]

        # Verify profile retrieved
        status_code, profile_body = self.client.get("/api/v1/profile", token=token)
        self.assertEqual(status_code, 200)
        self.assertEqual(profile_body["student"]["full_name"], "Priya Patel")

    def test_04_full_student_journey(self):
        """Test full student lifecycle: login, setup, triage, AI planning, adaptation, and logout."""
        # 1. Login
        status_code, auth_res = self.client.post("/api/v1/auth/login", {
            "email": "demo@preppilot.com",
            "password": "password123"
        })
        self.assertEqual(status_code, 200)
        token = auth_res["token"]

        # 2. Update Availability for Today (e.g. 150 mins, Medium energy)
        status_code, avail_res = self.client.post("/api/v1/profile/availability", {
            "available_start_time": "18:00",
            "available_end_time": "21:30",
            "available_duration_minutes": 150,
            "energy_level": "Medium",
            "preferred_activity": "Mixed"
        }, token=token)
        self.assertEqual(status_code, 200)
        self.assertEqual(avail_res["status"], "success")

        # 3. Add a new Academic Task
        status_code, task_res = self.client.post("/api/v1/academic/tasks", {
            "subject": "Compiler Design",
            "task_title": "Lexical Analyzer Flex Specification Assignment",
            "task_type": "Assignment",
            "priority": "High",
            "difficulty": "Medium",
            "estimated_duration_minutes": 60,
            "deadline": "2026-10-12T18:00:00Z"
        }, token=token)
        self.assertEqual(status_code, 201)
        created_task_id = task_res["task"]["task_id"]

        # 4. List Academic Tasks
        status_code, tasks_list = self.client.get("/api/v1/academic/tasks", token=token)
        self.assertEqual(status_code, 200)
        self.assertGreaterEqual(len(tasks_list), 4)

        # 5. Run AI Skill Gap Analysis
        status_code, gaps_res = self.client.get("/api/v1/ai/skills-analysis", token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("readiness_summary", gaps_res)
        self.assertIn("skill_gaps", gaps_res)
        self.assertGreater(gaps_res["readiness_summary"]["overall_readiness_percentage"], 0)

        # 6. Detect Academic Synergies
        status_code, syn_res = self.client.get("/api/v1/ai/synergies", token=token)
        self.assertEqual(status_code, 200)
        self.assertGreaterEqual(syn_res["synergies_detected_count"], 1)
        self.assertGreater(syn_res["total_time_saved_minutes"], 0)

        # 7. Generate Placement Roadmap
        status_code, rmap_res = self.client.post("/api/v1/roadmap/generate", token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("roadmap", rmap_res)
        self.assertEqual(len(rmap_res["roadmap"]["phases"]), 4)

        # 8. Generate Daily Plan (Bandwidth Engine)
        status_code, daily_plan = self.client.post("/api/v1/plan/daily/generate", {
            "energy_level": "Medium",
            "available_minutes": 150
        }, token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("items", daily_plan)
        self.assertLessEqual(daily_plan["total_planned_minutes"], 150)
        self.assertGreater(daily_plan["academic_workload_minutes"], 0)
        self.assertGreater(daily_plan["placement_prep_minutes"], 0)

        # 9. Get Today's Plan from Database
        status_code, today_plan = self.client.get("/api/v1/plan/daily/today", token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("items", today_plan)
        self.assertGreater(len(today_plan["items"]), 0)

        # 10. Adapt Plan Dynamically (Surprise Assignment Arrives)
        status_code, adapt_res = self.client.post("/api/v1/plan/adapt", {
            "trigger_event": "Surprise Academic Assignment",
            "details": {"title": "Emergency DBMS Normalization Quiz", "subject": "DBMS"},
            "additional_academic_minutes": 45
        }, token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("guilt_free_reassurance", adapt_res)
        self.assertIn("adaptation_summary", adapt_res)

        # 11. Request AI Micro-Drill
        status_code, drill_res = self.client.post("/api/v1/coach/micro-drill", {
            "skill_name": "DSA",
            "energy_level": "Low"
        }, token=token)
        self.assertEqual(status_code, 200)
        self.assertIn("drill", drill_res)

        # 12. Log Progress & Verify Streak
        status_code, prog_res = self.client.post("/api/v1/progress/log", {
            "task_category": "Placement",
            "task_title": "15-minute DSA Two-Pointers drill",
            "duration_minutes": 15,
            "problems_solved": 1,
            "notes": "Verified streak protection"
        }, token=token)
        self.assertEqual(status_code, 201)
        self.assertIn("streak", prog_res)

        # 13. Fetch Unified Dashboard Summary
        status_code, dash_res = self.client.get("/api/v1/dashboard/summary", token=token)
        self.assertEqual(status_code, 200)
        self.assertEqual(dash_res["student"]["full_name"], "Aarav Sharma")
        self.assertIsNotNone(dash_res["readiness_summary"])
        self.assertGreaterEqual(dash_res["synergies"]["count"], 1)

        # 14. Logout
        status_code, logout_res = self.client.post("/api/v1/auth/logout", token=token)
        self.assertEqual(status_code, 200)

        # 15. Verify that invalidated token cannot access protected endpoints
        status_code, denied_res = self.client.get("/api/v1/auth/me", token=token)
        self.assertEqual(status_code, 401)

        # Clean up created task
        # Re-login to clean up
        _, re_auth = self.client.post("/api/v1/auth/login", {
            "email": "demo@preppilot.com",
            "password": "password123"
        })
        self.client.delete(f"/api/v1/academic/tasks/{created_task_id}", token=re_auth["token"])


if __name__ == "__main__":
    unittest.main()
