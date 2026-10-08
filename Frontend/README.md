# AdaptiveStudy AI - Realistic Student Study Planner

A modern, empathetic, and realistic student schedule generator and study companion.

## Features

1. **Empathetic Study Window Management**:
   - Customizable study windows (e.g. 6:00 PM – 11:00 PM) with real-time total duration calculation.
   - Handles midnight spans and night study sessions smoothly.
   - Syncs start and end times across all tabs in real-time.

2. **Cognitive Bandwidth & Burnout Protection**:
   - Automatically prioritizes high-focus deep work (⚡ Hard Coding / Math) when mental alertness is highest.
   - Follows with written assignments / lab records (✍️ Medium) and light revision (📖 Light).
   - Injects mandatory **15-minute breaks after every 60 minutes** of continuous study.
   - Automatically detects time overruns and safely marks overflowing tasks as **"Shifted to Tomorrow"** with a no-overload guarantee.

3. **Natural Language AI Task Extractor**:
   - Parses messy, multi-sentence student homework notes into individual tasks.
   - Example: *"Finish 2 C programs on pointers, submit Chemistry lab record, read 10 slides of DBMS, solve 3 calculus integrals"*.
   - Intelligently classifies subjects, estimated durations, and priority types.

4. **5-Minute Micro-Steps AI Task Breakdown**:
   - One-click **"Break Down"** button on each task opens the step-by-step modal.
   - Provides an **Instant Starter** tip to overcome procrastination in under 2 minutes.
   - Generates actionable 5-minute micro-steps with interactive checkboxes.
   - Completing all micro-steps marks the parent task complete!

5. **Focus Sprint Pomodoro Timer**:
   - 25-minute sprint timer with Play / Pause / Resume and Reset controls.
   - Synthesizes pleasant two-tone audio chime on completion using Web Audio API.

6. **Dynamic Running Late Controls**:
   - **"+20 min Late"** button dynamically delays the entire timetable by 20 minutes with zero guilt.
   - Quick reset button to restore the original on-time plan.

7. **Dual-Mode Desktop & Mobile Phone Preview**:
   - Realistic smartphone preview with notch, live clock, 5G indicator, and mobile bottom dock.
   - Full wide desktop view with desktop dock navigation.

8. **Velocity & Performance Analytics**:
   - Real-time study type distribution (% deep work vs lab files vs revision).
   - Tasks completed progress and predicted semester SGPA tracking.
   - Interactive daily hours logged bar chart.

9. **Student Account & Session Management**:
   - 1-Click Demo Student Sign In (`Aarav Sharma`).
   - Custom course / degree tracks (Computer Science B.Tech, Core Engineering, Placements, GATE).
   - Full persistence via `localStorage` with offline resilience and optional backend integration (`http://127.0.0.1:8000`).

---

## How to Run

### Start the Frontend
```bash
cd Frontend
python run_frontend.py
```
Open **[http://localhost:3000](http://localhost:3000)** in your browser.

*(Alternatively, simply open `Frontend/index.html` directly in any web browser!)*

---

## Running Automated Tests

### Node.js Frontend Test Suite (126 Tests):
```bash
node tests/test_frontend.js
```

### Python Frontend Test Suite:
```bash
python tests/test_frontend.py
```

### Python Backend Test Suite:
```bash
python backend/test_backend.py
```

### AI Engine Test Suite:
```bash
python AI/test_ai_engine.py
```
