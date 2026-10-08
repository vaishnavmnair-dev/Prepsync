# PrepPilot (Bandwidth AI) - Backend Platform

### Problem Statement: Bridging the Gap Between College and Placement Preparation
B.Tech students preparing for internships and placements struggle to balance their academic workload with the continuous preparation required for their careers. Alongside lectures, assignments, labs and examinations, students need to develop skills such as DSA, core CS, development and aptitude, build projects, improve their resumes and prepare for interviews. Students often do not know what they should prioritize, how prepared they are, or how to fit placement preparation into their limited available time.

Existing tools such as calendars, to-do lists and learning platforms address these activities separately, but do not connect a student's academic workload, career goals, skill gaps, deadlines and available time. This leads to inconsistent preparation, poor prioritization, unrealistic schedules and increased mental load.

**PrepPilot (Bandwidth AI)** solves this as an AI-powered College & Placement Companion that understands a student's academic responsibilities and career goals, identifies preparation gaps, provides a personalized placement roadmap, and dynamically generates and adapts realistic daily and weekly plans around the student's actual workload, mental fatigue, and available time.

---

## 1. System Architecture

```
                  +----------------------------------------------+
                  |         Client Apps (Frontend / CLI)         |
                  +----------------------------------------------+
                                         |  HTTP / REST (JSON)
                                         v
+---------------------------------------------------------------------------------+
|                       FastAPI Application Server (Port 8000)                    |
|                                                                                 |
|  +--------------------+  +----------------------+  +-------------------------+  |
|  |   Authentication   |  |   Academic Workload  |  |    Career & Skills      |  |
|  | - Signup / Register|  | - Task CRUD          |  | - Goal Selection        |  |
|  | - Login / Signin   |  | - Deadlines & Urgency|  | - Skill Benchmarking    |  |
|  | - Logout / Bearer  |  | - Lab / Assignments  |  | - Gap Urgency Scoring   |  |
|  +--------------------+  +----------------------+  +-------------------------+  |
|                                                                                 |
|  +---------------------------------------------------------------------------+  |
|  |                         AI Intelligence Engine Bridge                     |  |
|  | - Skill Analyzer: Placement Readiness Index & Ranked Skill Gaps           |  |
|  | - Synergy Detector: Connects Academic Labs to Technical Interview Topics  |  |
|  | - Bandwidth Engine: Cognitive Fatigue-Aware Daily/Weekly Schedule Planner |  |
|  | - Adaptation Engine: Dynamic Rescheduling on Surprises & Fatigue Drops    |  |
|  | - LLM Advisor: Energy-Matched Micro-Drills & Strategic Mentorship         |  |
|  +---------------------------------------------------------------------------+  |
|                                         |                                       |
+-----------------------------------------|---------------------------------------+
                                          v
+---------------------------------------------------------------------------------+
|                         Relational Database Layer                               |
|                     (SQLite with WAL / PostgreSQL)                              |
|                                                                                 |
| - students              - student_career_goals       - student_skills           |
| - career_roles          - academic_tasks             - study_availability       |
| - daily_plans           - daily_plan_items           - placement_roadmaps       |
| - progress_logs         - student_streaks            - plan_adaptations         |
+---------------------------------------------------------------------------------+
```

---

## 2. Key Features

1. **Authentication & Session Security**
   - Cryptographic password hashing using `PBKDF2 HMAC SHA-256` with unique 16-byte random salts.
   - Bearer session token management (`/api/v1/auth/signup`, `/api/v1/auth/login`, `/api/v1/auth/logout`, `/api/v1/auth/me`).
   - Auto-provisioning of baseline career goals, curriculum skills, and streaks upon signup.

2. **Academic Triage vs. Placement Protection (The Bandwidth Engine)**
   - Computes student cognitive bandwidth from declared hours and energy (High, Medium, Low).
   - **Academic Triage Box**: Locks college homework/lab assignments with strict stop-times to prevent overtime and protect GPA.
   - **Protected MVPT (Minimum Viable Placement Task)**: Guarantees a non-negotiable 15-30 minute high-yield drill (DSA or Core CS) to protect the placement runway and maintain momentum.
   - **Rest Buffer**: Prevents burnout by enforcing recovery buffers based on mental exhaustion.

3. **Academic-Placement Synergy Detection**
   - Automatically inspects college lab records and assignments to find direct overlaps with technical interviews.
   - Examples:
     - *DBMS Lab Manual* $\rightarrow$ Connects to B+ Tree Indexing & 3NF/BCNF normalization asked by Tier-1 product companies.
     - *OS Concurrency Assignment* $\rightarrow$ Connects to Semaphore vs Mutex race condition interview questions.
     - *Computer Networks Lab* $\rightarrow$ Connects to TCP 3-Way Handshake & Subnetting drills.
   - Quantifies duplicate study time eliminated (e.g. 100+ minutes saved per week).

4. **Dynamic Rescheduling & Adaptation (Guilt-Free Engine)**
   - When sudden disruptions occur (surprise lab report, fatigue drop, lecture overrun):
     - Compresses or reschedules lower-priority tasks.
     - Adapts placement goals to bite-sized drills.
     - Generates guilt-free reassurance and preserves the student's preparation streak.

5. **Personalized 4-Phase Placement Roadmap**
   - Synthesizes chronological milestones based on the student's target tier (Product SDE, FAANG, Startup) and graduation timeline:
     - Phase 1: Core DSA Foundations & Syntax
     - Phase 2: Advanced Data Structures & Essential CS Fundamentals (DBMS, OS, CN)
     - Phase 3: System Design & Project Architecture
     - Phase 4: Full Mock Interviews & Company-Specific Sprints

6. **Unified Student Dashboard**
   - A single high-speed endpoint (`/api/v1/dashboard/summary`) returning the complete profile, target dream role, placement readiness percentage, active skill gaps, synergies detected, today's schedule, urgent college deadlines, and streak counter.

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `pydantic`

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Start the Backend Server
```bash
python run.py
```
The server will boot on `http://127.0.0.1:8000`.

- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Interactive Reference**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Root Status Probe**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Run the Automated Test Suite
```bash
python test_backend.py
```
Executes complete automated validation across all database models, auth flows, AI algorithms, and endpoints.

---

## 4. Default Seed Demo Account

The database initializes automatically with a seeded Demo Student profile matching a real-world college crunch scenario:

| Field | Value |
| :--- | :--- |
| **Email** | `demo@preppilot.com` |
| **Password** | `password123` |
| **Name** | Aarav Sharma |
| **Institution** | National Institute of Technology (NIT) |
| **Degree & Branch**| B.Tech Computer Science (3rd Year, 5th Semester) |
| **Dream Goal** | Software Developer (FAANG / Tier-1) |
| **Active Streak** | 14 Days |
| **Academic Commitments** | DBMS Lab Manual (Critical), OS Semaphore Assignment (High), Computer Networks Report |

---

## 5. API Reference Summary

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/signup` | Register new student, sets up profile, baseline skills, streak & issues Bearer token |
| `POST` | `/api/v1/auth/login` | Authenticate student with email & password, returns session token |
| `POST` | `/api/v1/auth/logout` | Invalidate active session token |
| `GET` | `/api/v1/auth/me` | Fetch authenticated student profile, active goal, and streak |

### Profile & Availability (`/api/v1/profile`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/profile` | Get student academic details and bandwidth configuration |
| `PUT` | `/api/v1/profile` | Update college details, daily available minutes, or study hours |
| `POST` | `/api/v1/profile/availability` | Declare today's study window and cognitive energy level |

### Career & Skills (`/api/v1/career`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/career/roles` | List standard industry career tracks |
| `GET` | `/api/v1/career/goal` | Get student's target role and company tier |
| `POST` | `/api/v1/career/goal` | Set or update target career aspiration |
| `GET` | `/api/v1/career/skills` | List student's skills and proficiency ratings (0-5) |
| `POST` | `/api/v1/career/skills` | Upsert student skill proficiency |

### Academic Workload (`/api/v1/academic`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/academic/tasks` | List academic commitments, lab records, assignments, and exams |
| `POST` | `/api/v1/academic/tasks` | Create new academic task with deadline and estimated duration |
| `PUT` | `/api/v1/academic/tasks/{task_id}` | Update task status, remaining minutes, or completion percentage |
| `DELETE` | `/api/v1/academic/tasks/{task_id}`| Remove completed or cancelled academic task |

### AI Intelligence & Synergies (`/api/v1/ai`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ai/skills-analysis` | Calculate placement readiness index & prioritized skill gaps |
| `GET` | `/api/v1/ai/synergies` | Detect academic-interview synergies and quantify hours saved |

### Placement Roadmap (`/api/v1/roadmap`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/roadmap/generate` | Synthesize and persist personalized 4-phase preparation roadmap |
| `GET` | `/api/v1/roadmap` | Retrieve student's current placement roadmap |

### Dynamic Planning (`/api/v1/plan`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/plan/daily/generate` | Generate fatigue-aware schedule (Academic Triage + Protected MVPT) |
| `GET` | `/api/v1/plan/daily/today` | Retrieve today's active schedule and item time-boxes |
| `POST` | `/api/v1/plan/weekly/generate` | Generate 7-day adaptive schedule balancing college days and weekend sprints |
| `POST` | `/api/v1/plan/adapt` | Dynamically adapt schedule on surprise disruptions (guilt-free) |
| `PUT` | `/api/v1/plan/items/{item_id}/status` | Mark plan item status (Completed status auto-advances streak!) |

### AI Placement Coach (`/api/v1/coach`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/coach/micro-drill` | Generate 15-30 minute interview drill matched to energy level |
| `GET` | `/api/v1/coach/guidance` | Strategic guidance balancing current semester load and placements |

### Progress & Streaks (`/api/v1/progress`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/progress/log` | Log completed study/coding session, advances streak counter |
| `GET` | `/api/v1/progress/streak` | Get current streak, record streak, and 7-day velocity stats |
| `GET` | `/api/v1/progress/history` | List past completed study logs |

### Dashboard Overview (`/api/v1/dashboard`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard/summary` | Consolidated aggregate of profile, readiness, gaps, synergies, today's schedule, deadlines, and streak |

