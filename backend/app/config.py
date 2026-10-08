"""Application Configuration Settings."""

import os
import sys
from pathlib import Path

# Ensure AI module is in Python sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
AI_DIR = BASE_DIR.parent / "AI"
if str(AI_DIR) not in sys.path and AI_DIR.exists():
    sys.path.insert(0, str(AI_DIR))

class Settings:
    PROJECT_NAME: str = "Bandwidth AI (PrepPilot) - Placement Companion"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "AI-Powered College & Placement Companion that understands a student's "
        "academic responsibilities and career goals, identifies preparation gaps, "
        "provides a personalized placement roadmap, and dynamically generates and adapts "
        "realistic daily and weekly plans around actual workload and mental fatigue."
    )
    API_V1_PREFIX: str = "/api/v1"
    
    # Database configuration
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")  # "sqlite" or "postgres"
    DATABASE_FILE: Path = BASE_DIR / "companion.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE.as_posix()}")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "preppilot-ideathon-super-secret-key-2026")
    SESSION_TOKEN_EXPIRE_HOURS: int = 72

    # Default Demo Account
    DEMO_EMAIL: str = "demo@preppilot.com"
    DEMO_PASSWORD: str = "password123"

settings = Settings()
