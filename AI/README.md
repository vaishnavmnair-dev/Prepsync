# 🧠 Bandwidth AI (PrepPilot Engine)
> **The Workload-Aware, Cognitive-Adaptive AI Engine Bridging College Workload and Placement Preparation**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal.svg)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Status-Tested%20%26%20Verified-success.svg)](https://github.com)
[![Ideathon Prototype](https://img.shields.io/badge/Prototype-Production--Ready-orange.svg)](https://github.com)

---

## 📌 1. The Problem: "Placement Paralysis"
Engineering students face a relentless conflict:
- **Daily Academic Workload:** Surprise assignments, 3-hour lab records, viva prep, midterms, and attendance quotas.
- **Placement Imperative:** Long-term consistency required for Data Structures & Algorithms (DSA), Core CS (OS, DBMS, Networks, OOP), Full-Stack projects, Aptitude, and Mock Interviews.

### Why Traditional Tools Fail:
| Existing Tool | Why It Breaks for Students |
| :--- | :--- |
| **Notion / Calendars** | Treat human energy like a robot. Blindly schedule 6 hours after a grueling college day, leading to broken schedules on Day 2. |
| **ChatGPT** | Passive prompt answers. Has no visibility into actual academic deadlines, cognitive fatigue, or streak continuity. |
| **LeetCode / Learning Apps** | Disconnected from college exams. When students enter midterm week, they drop prep entirely and lose months of muscle memory. |

**Bandwidth AI** closes this gap by synchronizing academic compliance, career goals, cognitive fatigue, and available time into a realistic, adaptive execution system.

---

## ⚡ 2. Core Mathematical & Algorithmic Models

### A. Skill Gap & Urgency Scoring
For each target career role (Software Developer, Backend, Frontend, AI/ML, Data Analyst):

$$\text{Skill Gap} = \max(0, \text{Required Proficiency}_{\text{tier}} - \text{Current Proficiency})$$

$$\text{Gap Urgency Score} = \text{Skill Gap} \times \text{Weight Score} \times \text{Tier Multiplier}$$

*Where $\text{Tier Multiplier}$ reflects target company standards (e.g., $1.25$ for FAANG/Tier-1, $1.15$ for Unicorn Startups).*

### B. Overall Placement Readiness Index
$$\text{Readiness Index (\%)} = \left(\frac{\sum \min(\text{Current}_i, \text{Required}_i) \times \text{Weight}_i}{\sum \text{Required}_i \times \text{Weight}_i}\right) \times 100$$

### C. The Bandwidth Triage & Minimum Viable Placement Task (MVPT)
Rather than forcing an unachievable to-do list, the engine applies **Academic Triage**:
1. **Urgency $\le 24$h (Critical):** Guaranteed time-box allocation to safeguard college internal marks and attendance.
2. **Urgency $\le 48$h (High):** Preemptive chunking if bandwidth remains.
3. **Protected MVPT (Minimum Viable Placement Task):** Non-negotiable placement chunk ($15$ to $50$ mins) scaled to student's energy level:
   - **Low Energy (Fatigued):** $15\text{–}20$ min conceptual drill or flashcard revision.
   - **Medium Energy:** $30\text{–}35$ min problem solving or core CS drill.
   - **High Energy:** $50\text{–}60$ min deep DSA or full-stack feature.
4. **Guilt-Free Dynamic Adaptation:** When surprise assignments or fatigue strike, MVPT scales down to 15 minutes, preserving the streak with **zero guilt**.

### D. Academic-Placement Synergy Detector
Detects where college coursework overlaps with placement rounds (e.g., C pointer assignments $\leftrightarrow$ memory management interviews; OS scheduling labs $\leftrightarrow$ system concurrency questions). This eliminates duplicate prep time and gives students "double credit" for their college effort.

---

## 🚀 3. Quick Start & Execution

### Running the Interactive CLI Demo
```powershell
# Run the canonical Ideathon Demo Student scenario (matches database seed)
python cli.py --scenario demo

# Run Midterm Crunch scenario (low energy, heavy academic deadlines)
python cli.py --scenario midterm

# Run Weekend Placement Sprint (high energy, 5 hours bandwidth)
python cli.py --scenario weekend
```

### Running Automated Test Suite
```powershell
python test_ai_engine.py
```
*(All unit tests verify math equations, scheduling budgets, edge cases, and dynamic adaptations).*

### Starting the FastAPI REST Server
```powershell
python -m uvicorn api.server:app --reload --port 8000
```
Swagger UI will be available at: `http://127.0.0.1:8000/docs`

---

## 🌐 4. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/profile/analyze` | Evaluates skill gaps and computes Readiness Index (%) |
| `POST` | `/api/v1/roadmap/generate` | Generates personalized 4-phase placement roadmap |
| `POST` | `/api/v1/synergy/detect` | Identifies academic homework $\leftrightarrow$ placement overlaps |
| `POST` | `/api/v1/plan/daily` | Synthesizes realistic daily schedule with triage & MVPT |
| `POST` | `/api/v1/plan/weekly` | Generates 7-day balanced horizon |
| `POST` | `/api/v1/plan/adapt` | Real-time guilt-free rescheduling on surprise tasks/fatigue |
| `POST` | `/api/v1/coach/micro-drill` | Returns daily 15-min interview question with hints & solution |
| `POST` | `/api/v1/db/context-plan` | Accepts raw JSON from PostgreSQL `05_ai_planning_context.sql` & outputs SQL inserts |
| `GET` | `/api/v1/demo` | Complete end-to-end simulated demo flow |

---

## 🗄️ 5. PostgreSQL Database Integration
The AI Engine is built to natively sync with the PostgreSQL schema in `../database/`:
1. It ingests the JSON compiled by `05_ai_planning_context.sql` (`fn_get_ai_daily_plan_context`).
2. It outputs syntactically valid `INSERT INTO daily_plans` and `INSERT INTO daily_plan_items` SQL queries via `DatabaseAdapter.export_plan_to_sql_inserts()`.

---

## 🏆 6. Ideathon Judge Highlights
- **Human Feasibility First:** Never schedules 8 hours into a 3-hour window.
- **Zero-Guilt Architecture:** Eliminates punishing red overdue marks; protects mental stamina.
- **Synergy Detector:** Turns boring college homework into active placement assets.
- **Offline & Hackathon Ready:** Works 100% out-of-the-box with deterministic smart heuristics, with optional LLM enrichment when API keys are available.

