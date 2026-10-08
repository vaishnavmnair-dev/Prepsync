# PrepPilot (AdaptiveStudy AI)
### Empathetic, Fatigue-Aware Study Companion & Placement Preparation Engine

> **Hackathon Track**: Problem Statement 4: Open Innovation (Student Pain Points)  
> **Target Audience**: College students preparing for tech placements and internships while managing academic coursework.  
> **Status**: Full-Stack Working Prototype (Live Backend + AI Engine + SQLite Database + Responsive Frontend)  
> **Test Coverage**: 218 / 218 Automated Tests Passing (100% Pass Rate)

---

## 1. Problem Definition

### Who has the problem?
Engineering and college students (across years 2, 3, and 4) preparing for summer internships, product-based companies, and campus placement drives while simultaneously managing heavy college coursework, lab records, assignments, and exams.

### What it costs them?
1. **Severe Decision Fatigue & Time Loss**: Students spend 30–50 minutes every evening simply deciding *what* to study among hundreds of LeetCode problems, lecture slides, and pending lab files. This friction drains their willpower before they even begin.
2. **Burnout from Unrealistic Scheduling**: Rigid study calendars assume infinite energy. When a student returns exhausted after an 8-hour college day, attempting a 3-hour hard DSA grind leads to procrastination, guilt, and abandoned preparation.
3. **Broken Preparation Streaks**: Surprise college submissions (e.g. emergency lab records or mid-semester quizzes) derail placement preparation entirely. Without intelligent rescheduling, students give up on consistency.
4. **Duplicated Effort**: Students fail to realize that their college courses (OS, DBMS, Computer Networks) overlap with interview rounds, wasting hours studying them as completely separate silos.

### Why existing tools fall short?
* **Generic To-Do Apps (Notion, Todoist, Google Calendar)**: Completely context-blind. They do not understand academic deadlines, coding difficulty, or cognitive energy. When life gets in the way, they punish students with overdue red badges instead of dynamically rebalancing.
* **Practice Portals (LeetCode, HackerRank, GeeksforGeeks)**: Excellent problem repositories, but provide zero daily pacing or schedule orchestration. They overwhelm students with 3,000+ problems without answering: *"What should I do in my 90 available minutes tonight?"*
* **Static Roadmap PDFs (Striver Sheet, NeetCode, Roadmap.sh)**: Fixed checklists that do not adapt when surprise assignments arrive or when a student is exhausted.

---

## 2. Evidence That Students Need It Solved

To validate that this struggle is widespread and pressing, we conducted a primary user survey and structured interviews with **8 college students** actively preparing for internships and campus placements.

The complete survey breakdown and qualitative interview transcripts are documented in [`evidence/survey_results.md`](evidence/survey_results.md).

### Key Survey Findings (Real Numbers)

| Metric / Survey Question | Response Count | Percentage | Key Takeaway |
| :--- | :---: | :---: | :--- |
| **Currently preparing for internships or placements** | 6 / 8 | **75.0%** | Broad active audience with immediate placement needs |
| **Difficult to know which skills they should improve** | 6 / 8 | **75.0%** | High uncertainty in prioritizing DSA vs Core CS vs Projects |
| **Do NOT have a clear, structured daily preparation plan** | 7 / 8 | **87.5%** | **Primary friction point**: Lack of daily actionable direction |
| **Struggle to decide what to study next each night** | 7 / 8 | **87.5%** | Decision paralysis drains willpower before studying starts |
| **Juggle multiple fragmented websites and tabs** | 5 / 8 | **62.5%** | Fragmented workflow across portals, sheets, and LMS portals |
| **Would adopt a tool with skill gaps + daily plans** | 6 / 8 | **75.0%** | **Direct validation**: 3 out of 4 students want this solution |
| **Rated the proposed tool 5 / 5 for usefulness** | 4 / 8 | **50.0%** | Half gave top marks, with all remaining rating 4/5 |

### Biggest Problems Reported by Students

```
Time Management (Balancing College & Placements): [37.5%]  ███████████████ (3 students)
Coding & DSA Execution Hesitation:               [25.0%]  ██████████ (2 students)
Lack of Structured, Personalized Guidance:       [25.0%]  ██████████ (2 students)
Information Overload / Other:                    [12.5%]  █████ (1 student)
```

### Real Student Quotes

> *"After 7 hours of college lectures and lab files, I sit at my desk at 7 PM wanting to prepare for placements, but I spend 40 minutes just deciding whether to do DSA, OS, or finish my lab record. By then, my brain is tired and I end up doing nothing."*  
> — **3rd Year B.Tech CSE Student (Tier-2 Engineering College)**

> *"Existing to-do apps like Notion or Todoist are dumb. If I get an emergency assignment from college, Notion just keeps showing overdue red badges. It doesn't tell me what placement topic I can swap without ruining my streak."*  
> — **Final Year Information Technology Student**

> *"When a task on my list says 'Finish 2 C programs on pointers', it feels so huge that I end up scrolling Instagram instead. If an app broke that down into 10-minute micro-steps with starter tips, I would start immediately."*  
> — **Pre-final Year Student preparing for Summer Internships**

---

## 3. Working Prototype: PrepPilot (AdaptiveStudy AI)

PrepPilot is a full-stack, AI-powered study companion specifically architected to solve student placement friction through empathetic, fatigue-aware orchestration.

### Core Architectural Capabilities

1. **Cognitive Bandwidth & Fatigue Engine**:
   - Balances college assignments and placement prep within the student's actual study window (e.g. 6:00 PM – 11:00 PM).
   - Inserts mandatory **15-minute refresh breaks** after every 60–75 minutes of continuous study to prevent burnout.
   - Places demanding tasks (*Hard Coding / Math*) early when energy is peak, and lighter tasks (*Revision / Slides*) later.
2. **Smart 5-Minute AI Task Breakdown Engine**:
   - Breaks intimidating tasks into actionable 5- to 15-minute micro-steps tailored specifically to the task's domain (Coding, Lab Records, Calculus, Slides, Reports).
   - Provides an **Instant Starter Kickstart tip** to eliminate procrastination within the first 60 seconds.
   - Includes an interactive **Step Progress Bar** and audio chime feedback upon milestone completion.
   - Features **"Add Steps to Queue"**, allowing students to convert high-level commitments into bite-sized sub-tasks in their live study queue.
3. **Academic-Placement Synergy Detector**:
   - Scans academic workload and identifies direct overlaps with company interview topics (e.g. *Operating Systems Process Scheduling* directly covers Cisco & Goldman Sachs technical rounds).
   - Calculates hours saved and eliminates duplicated preparation.
4. **Dynamic Plan Adaptation & "Running Late" Resilience**:
   - If a student gets delayed by 20–40 minutes, a single click shifts the timeline forward without guilt.
   - Tasks overflowing the study window are smoothly marked as *"Shifted to Tomorrow"* rather than marked as failures.
5. **Multi-User Session Isolation & SQLite Database Persistence**:
   - Secure student authentication (Bearer tokens) backed by SQLite (`backend/companion.db`).
   - Clean guest mode on logout with zero leftover personal data on screen.
   - Comprehensive multi-tenant data isolation: all tasks, streaks, and profile details are safely restored upon re-login.

---

## 4. How PrepPilot Differs From Tools Students Already Use

| Capability / Feature | Generic To-Do Apps (Notion / Todoist) | Practice Portals (LeetCode / GFG) | Static Roadmap Sheets (Striver / NeetCode) | **PrepPilot (Our Solution)** |
| :--- | :---: | :---: | :---: | :---: |
| **Aware of College Workload & Deadlines** | ❌ No | ❌ No | ❌ No | **✅ Yes (Unified Academic & Placement Queue)** |
| **Fatigue & Burnout Safeguards** | ❌ Punishes with red badges | ❌ None | ❌ None | **✅ Auto-injects refresh breaks & caps study window** |
| **Cognitive Task Ordering** | ❌ Alphabetical / Manual | ❌ Static list | ❌ Rigid sequence | **✅ Hard topics placed at peak energy times** |
| **5-Minute Task Deconstruction** | ❌ Manual text only | ❌ None | ❌ None | **✅ AI micro-steps with starter tips & queue splitting** |
| **Curriculum Synergy Detection** | ❌ No | ❌ No | ❌ No | **✅ Identifies overlap between coursework & interviews** |
| **Adaptive "Running Late" Rescheduling** | ❌ Fixed calendar dates | ❌ None | ❌ None | **✅ 1-Click +20m offset without guilt or failure** |
| **Multi-Resource Consolidation** | ⚠️ High setup friction | ❌ Siloed to coding only | ❌ Siloed to DSA only | **✅ Consolidates DSA, Core CS, and coursework** |

---

## 5. Signs That Students Would Use It

1. **75% Immediate Adoption Intent**: In our validation survey, 6 out of 8 students confirmed they would immediately use a tool that diagnoses skill gaps and provides daily adaptable pacing.
2. **High Usefulness Rating**: 50% of surveyed students rated the tool **5/5** for usefulness, with the remainder rating it 4/5.
3. **Direct Demand for Task Breakdown**: Students specifically requested breaking large, intimidating coding topics into bite-sized micro-goals with starters to combat procrastination.
4. **Relief from Overdue Anxiety**: Qualitative interviews showed strong enthusiasm for our "guilt-free" rebalancing model, contrasting sharply with the stressful overdue notifications of traditional tools.

---

## 6. The Short Pitch: Why Students Will Use PrepPilot

> *"Most college students don't fail at placement prep because they lack intelligence—they fail because they are overwhelmed, fatigued, and spend half their energy just figuring out what to study after a tiring day of college.*  
>  
> *PrepPilot removes that mental friction completely. It acts as an empathetic co-pilot that balances your college assignments with your placement goals, breaks daunting coding tasks into 5-minute easy steps, and dynamically adapts when life gets in the way. With PrepPilot, you never stare blankly at your screen wondering what to study next."*

---

## 7. System Architecture & Tech Stack

```
[ Frontend: HTML5 / Tailwind CSS / Vanilla JS ]
                     │
                     ▼  REST APIs (JSON)
[ Backend: FastAPI (Python 3.14) ]
   ├── Authentication & Security (PBKDF2 / Session Tokens)
   ├── Academic Deadlines & Queue Router
   └── AI Bridge & Intelligence Router
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
[ AI Engine: Bandwidth & Fatigue ]   [ Relational Database: SQLite3 ]
  • Cognitive Load Balancer          • students
  • Synergy Detection Matrix         • academic_tasks
  • Smart Task Decomposer            • daily_plans & streak logs
  • LLM Advisor (Gemini Flash)
```

* **Frontend**: Pure HTML5, modern Tailwind CSS, Lucide icons, responsive phone-frame preview mode.
* **Backend**: FastAPI, Pydantic v2 schemas, zero-dependency ASGI architecture.
* **AI Engine**: Fatigue & Bandwidth Optimizer, Heuristic Domain Decomposer, and optional Google Gemini 1.5 Flash LLM enrichment.
* **Database**: SQLite3 (`backend/companion.db`) with full transactional persistence.

---

## 8. Quick Start Guide

### Prerequisites
* Python 3.10+ (Tested on Python 3.12, 3.13, 3.14)
* Node.js 18+ (for automated frontend test runner)

### Option 1: 1-Click Launch (Recommended)
Double-click `run_all.bat` or run:
```powershell
python run_all.py
```
This concurrently starts:
* **FastAPI Backend Server**: `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`)
* **Frontend Web Application**: `http://localhost:3000`

### Option 2: Run Automated Test Suites
Run all 218 test cases across the frontend, session lifecycle, task breakdown, backend, and AI engine:
```powershell
# 1. Frontend Algorithm & Markup Tests (126 tests)
node tests/test_frontend.js

# 2. User Session Lifecycle & Persistence Tests (47 tests)
node tests/test_frontend_session.js

# 3. Smart Task Breakdown Engine Tests (24 tests)
node tests/test_breakdown.js

# 4. Frontend Python Markup Integrity (9 tests)
python -m unittest tests/test_frontend.py

# 5. Backend FastAPI & SQLite Database E2E Tests (4 tests)
$env:PYTHONPATH="backend"; python -m unittest backend/test_backend.py

# 6. AI Bandwidth & Fatigue Engine Tests (8 tests)
$env:PYTHONPATH="AI"; python -m unittest AI/test_ai_engine.py
```

**Result**: All 218 tests pass with 0 errors.
