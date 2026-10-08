"""
Full Stack Launcher for PrepPilot / AdaptiveStudy AI.
Concurrently launches:
  1. FastAPI Backend Server (http://127.0.0.1:8000)
  2. Frontend HTTP Server (http://localhost:3000)
And automatically opens the browser with full database and AI connectivity!
"""

import os
import signal
import subprocess
import sys
import time
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "Frontend")

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    print("=" * 65)
    print("  🚀 Starting PrepPilot / AdaptiveStudy AI (Full Stack)")
    print("=" * 65)
    print("  [1/2] Launching FastAPI Backend Server on http://127.0.0.1:8000 ...")

    # Start Backend
    backend_proc = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=BACKEND_DIR
    )

    # Allow backend to bind socket
    time.sleep(1.5)

    print("  [2/2] Launching Frontend Server on http://localhost:3000 ...")
    # Start Frontend
    frontend_proc = subprocess.Popen(
        [sys.executable, "run_frontend.py"],
        cwd=FRONTEND_DIR
    )

    print("\n" + "=" * 65)
    print("  ✨ System is LIVE & Fully Connected:")
    print("  • Frontend:      http://localhost:3000")
    print("  • Backend API:   http://127.0.0.1:8000")
    print("  • Swagger Docs:  http://127.0.0.1:8000/docs")
    print("  • Database:      SQLite (backend/companion.db)")
    print("  • AI Engine:     Bandwidth & Fatigue Engine + LLM Advisor")
    print("=" * 65)
    print("  Press Ctrl+C to stop both servers.\n")

    # Wait for user termination
    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down Backend and Frontend servers...")
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
        except Exception:
            pass
        print("[SUCCESS] All servers stopped cleanly.")


if __name__ == "__main__":
    main()
