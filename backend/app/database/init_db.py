"""Database Schema Definition, Migration, and Seed Data Initialization."""

import hashlib
import json
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone
from app.config import settings
from app.database.connection import get_db_connection


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Generates PBKDF2 HMAC SHA-256 hash and salt for password security."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()
    return pw_hash, salt


def init_database():
    """Initializes SQLite tables matching the normalized relational architecture."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Students / Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            college_name TEXT NOT NULL,
            degree TEXT NOT NULL DEFAULT 'B.Tech',
            branch TEXT NOT NULL DEFAULT 'Computer Science',
            current_year INTEGER NOT NULL DEFAULT 3,
            current_semester INTEGER NOT NULL DEFAULT 5,
            graduation_year INTEGER NOT NULL DEFAULT 2026,
            preferred_study_hours_per_day REAL NOT NULL DEFAULT 3.0,
            daily_available_prep_minutes INTEGER NOT NULL DEFAULT 150,
            timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
            token_session TEXT,
            token_expires_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        # 2. Career Roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_roles (
            role_id TEXT PRIMARY KEY,
            role_title TEXT NOT NULL UNIQUE,
            industry_domain TEXT NOT NULL DEFAULT 'Information Technology',
            description TEXT,
            average_prep_duration_months INTEGER DEFAULT 6
        );
        """)

        # 3. Student Career Goals
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_career_goals (
            goal_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            target_company_type TEXT NOT NULL DEFAULT 'Product-based',
            target_placement_date TEXT NOT NULL,
            priority_rank INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # 4. Skills Catalog
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id TEXT PRIMARY KEY,
            skill_name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            description TEXT
        );
        """)

        # 5. Student Skills
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_skills (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            category TEXT NOT NULL,
            current_proficiency INTEGER NOT NULL DEFAULT 0,
            target_proficiency INTEGER NOT NULL DEFAULT 4,
            confidence_level TEXT NOT NULL DEFAULT 'Medium',
            assessment_source TEXT NOT NULL DEFAULT 'Self Assessment',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            UNIQUE(student_id, skill_name)
        );
        """)

        # 6. Academic Tasks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_tasks (
            task_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            task_title TEXT NOT NULL,
            task_type TEXT NOT NULL DEFAULT 'Assignment',
            priority TEXT NOT NULL DEFAULT 'Medium',
            difficulty TEXT NOT NULL DEFAULT 'Medium',
            estimated_duration_minutes INTEGER NOT NULL DEFAULT 60,
            remaining_duration_minutes INTEGER NOT NULL DEFAULT 60,
            deadline TEXT NOT NULL,
            completion_percentage INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Not Started',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # 7. Today's Study Availability
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_availability (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            availability_date TEXT NOT NULL,
            available_start_time TEXT NOT NULL DEFAULT '17:30',
            available_end_time TEXT NOT NULL DEFAULT '22:30',
            available_duration_minutes INTEGER NOT NULL DEFAULT 150,
            energy_level TEXT NOT NULL DEFAULT 'Medium',
            preferred_activity TEXT NOT NULL DEFAULT 'Mixed',
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            UNIQUE(student_id, availability_date)
        );
        """)

        # 8. Daily Plans
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_plans (
            plan_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            plan_date TEXT NOT NULL,
            total_available_minutes INTEGER NOT NULL,
            total_planned_minutes INTEGER NOT NULL,
            academic_workload_minutes INTEGER NOT NULL,
            placement_prep_minutes INTEGER NOT NULL,
            buffer_rest_minutes INTEGER NOT NULL,
            burnout_risk_score REAL NOT NULL,
            feasibility_rating TEXT NOT NULL,
            triage_headline TEXT NOT NULL,
            ai_strategic_summary TEXT NOT NULL,
            plan_status TEXT NOT NULL DEFAULT 'Generated',
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            UNIQUE(student_id, plan_date)
        );
        """)

        # 9. Daily Plan Items
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_plan_items (
            plan_item_id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            item_order INTEGER NOT NULL,
            task_category TEXT NOT NULL,
            task_id TEXT,
            title TEXT NOT NULL,
            subject_or_skill TEXT NOT NULL,
            scheduled_start_time TEXT NOT NULL,
            scheduled_end_time TEXT NOT NULL,
            planned_duration_minutes INTEGER NOT NULL,
            priority_score REAL NOT NULL,
            energy_requirement TEXT NOT NULL,
            ai_reasoning TEXT NOT NULL,
            is_mvpt INTEGER NOT NULL DEFAULT 0,
            synergy_tip TEXT,
            status TEXT NOT NULL DEFAULT 'Scheduled',
            FOREIGN KEY (plan_id) REFERENCES daily_plans(plan_id) ON DELETE CASCADE
        );
        """)

        # 10. Placement Roadmaps
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS placement_roadmaps (
            roadmap_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            target_company_type TEXT NOT NULL,
            total_estimated_duration_weeks INTEGER NOT NULL,
            phases_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # 11. Progress Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            log_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            task_category TEXT NOT NULL,
            task_title TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            problems_solved INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # 12. Student Streaks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_streaks (
            student_id TEXT PRIMARY KEY,
            current_streak_days INTEGER NOT NULL DEFAULT 0,
            longest_streak_days INTEGER NOT NULL DEFAULT 0,
            last_active_date TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # 13. Plan Adaptations History
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS plan_adaptations (
            adaptation_id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            trigger_event TEXT NOT NULL,
            adaptation_summary TEXT NOT NULL,
            tasks_compressed TEXT,
            tasks_deferred TEXT,
            guilt_free_reassurance TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES daily_plans(plan_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        """)

        # Create Indexes for Query Performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_email ON students(email);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_academic_tasks_student ON academic_tasks(student_id, deadline);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_skills_student ON student_skills(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_plans_student ON daily_plans(student_id, plan_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON daily_plan_items(plan_id);")

        conn.commit()


def seed_database():
    """Seeds reference data and the Demo Student account with realistic college workload."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Seed Standard Career Roles
        roles = [
            ("role-1", "Software Developer", "IT / Product", "Full cycle software development with DSA & Core CS focus.", 6),
            ("role-2", "AI / ML Engineer", "Artificial Intelligence", "Machine learning, neural networks, MLOps and mathematical modeling.", 8),
            ("role-3", "Backend Developer", "Cloud & Web", "APIs, microservices, databases, caching and high scalability.", 6),
            ("role-4", "Full Stack Developer", "Web Technologies", "Modern frontend frameworks combined with scalable backend architectures.", 6),
            ("role-5", "Data Analyst", "Analytics", "SQL, Python, statistical insights and data visualization.", 4),
            ("role-6", "Cybersecurity Analyst", "Security & Networks", "Network protocols, vulnerability scanning, secure design and cryptography.", 6)
        ]
        cursor.executemany("""
        INSERT OR IGNORE INTO career_roles (role_id, role_title, industry_domain, description, average_prep_duration_months)
        VALUES (?, ?, ?, ?, ?)
        """, roles)

        # Check if Demo Student exists
        cursor.execute("SELECT student_id FROM students WHERE email = ?", (settings.DEMO_EMAIL,))
        existing = cursor.fetchone()

        now_iso = datetime.now(timezone.utc).isoformat()
        today_iso = date.today().isoformat()

        if not existing:
            demo_id = "11111111-1111-1111-1111-111111111111"
            pw_hash, salt = hash_password(settings.DEMO_PASSWORD)

            cursor.execute("""
            INSERT INTO students (
                student_id, full_name, email, password_hash, salt, college_name, degree, branch,
                current_year, current_semester, graduation_year, preferred_study_hours_per_day,
                daily_available_prep_minutes, timezone, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                demo_id, "Aarav Sharma", settings.DEMO_EMAIL, pw_hash, salt,
                "National Institute of Technology", "B.Tech", "Computer Science",
                3, 5, 2026, 3.0, 150, "Asia/Kolkata", now_iso, now_iso
            ))

            # Career Goal
            target_date = (date.today() + timedelta(days=240)).isoformat()
            cursor.execute("""
            INSERT INTO student_career_goals (
                goal_id, student_id, role_title, target_company_type, target_placement_date, priority_rank, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), demo_id, "Software Developer", "FAANG / Tier-1", target_date, 1, "Active", now_iso))

            # Demo Student Skills
            demo_skills = [
                ("DSA", "DSA", 2, 5, "Medium"),
                ("C/C++", "Programming", 3, 3, "High"),
                ("Python", "Programming", 3, 4, "High"),
                ("SQL & DBMS", "Core CS", 2, 4, "Medium"),
                ("Operating Systems", "Core CS", 2, 3, "Medium"),
                ("Computer Networks", "Core CS", 1, 3, "Low"),
                ("System Design", "Development", 1, 3, "Low"),
                ("Web Development", "Development", 3, 4, "High"),
                ("Quantitative Aptitude", "Aptitude", 2, 4, "Medium"),
            ]
            for sname, scat, cur, tgt, conf in demo_skills:
                cursor.execute("""
                INSERT INTO student_skills (
                    id, student_id, skill_name, category, current_proficiency, target_proficiency, confidence_level, assessment_source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), demo_id, sname, scat, cur, tgt, conf, "Self Assessment", now_iso, now_iso))

            # Academic Tasks (Assignments, Lab records due)
            tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
            two_days = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
            five_days = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()

            demo_tasks = [
                (
                    "task-acad-001", demo_id, "DBMS", "DBMS Lab Manual (20 Queries & Schema Diagrams)",
                    "Lab", "Critical", "Medium", 60, 60, tomorrow, 20, "In Progress", now_iso, now_iso
                ),
                (
                    "task-acad-002", demo_id, "Operating Systems", "OS Process Synchronization & Semaphore Assignment",
                    "Assignment", "High", "Hard", 90, 90, two_days, 0, "Not Started", now_iso, now_iso
                ),
                (
                    "task-acad-003", demo_id, "Computer Networks", "Wireshark Packet Analysis Lab Experiment Report",
                    "Lab", "Medium", "Medium", 45, 45, five_days, 0, "Not Started", now_iso, now_iso
                )
            ]
            cursor.executemany("""
            INSERT INTO academic_tasks (
                task_id, student_id, subject, task_title, task_type, priority, difficulty,
                estimated_duration_minutes, remaining_duration_minutes, deadline, completion_percentage, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, demo_tasks)

            # Study Availability for Today
            cursor.execute("""
            INSERT INTO study_availability (
                id, student_id, availability_date, available_start_time, available_end_time, available_duration_minutes, energy_level, preferred_activity, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), demo_id, today_iso, "17:30", "22:30", 150, "Medium", "Mixed", now_iso))

            # Student Streak
            cursor.execute("""
            INSERT INTO student_streaks (student_id, current_streak_days, longest_streak_days, last_active_date, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (demo_id, 14, 21, today_iso, now_iso))

        conn.commit()


def setup_database():
    """Full initialization pipeline for application boot."""
    init_database()
    seed_database()
