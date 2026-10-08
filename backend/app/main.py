"""Main FastAPI Application Entry Point for Bandwidth AI (PrepPilot)."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.init_db import setup_database

# Routers
from app.auth.router import router as auth_router
from app.api.profile import router as profile_router
from app.api.career import router as career_router
from app.api.academic import router as academic_router
from app.api.ai_analysis import router as ai_analysis_router
from app.api.roadmap import router as roadmap_router
from app.api.planning import router as planning_router
from app.api.coach import router as coach_router
from app.api.progress import router as progress_router
from app.api.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database schema and default seed data upon application startup."""
    setup_database()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers under /api/v1 prefix
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(career_router, prefix=settings.API_V1_PREFIX)
app.include_router(academic_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_analysis_router, prefix=settings.API_V1_PREFIX)
app.include_router(roadmap_router, prefix=settings.API_V1_PREFIX)
app.include_router(planning_router, prefix=settings.API_V1_PREFIX)
app.include_router(coach_router, prefix=settings.API_V1_PREFIX)
app.include_router(progress_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["System"])
def root():
    """System status and root overview."""
    return {
        "engine": "Bandwidth AI (PrepPilot)",
        "mission": "Bridging the Gap Between College Workload and Placement Preparation",
        "status": "online",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "demo_credentials": {
            "email": settings.DEMO_EMAIL,
            "password": settings.DEMO_PASSWORD
        },
        "endpoints": {
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "dashboard": f"{settings.API_V1_PREFIX}/dashboard/summary",
            "skills_analysis": f"{settings.API_V1_PREFIX}/ai/skills-analysis",
            "synergies": f"{settings.API_V1_PREFIX}/ai/synergies",
            "daily_plan": f"{settings.API_V1_PREFIX}/plan/daily/today",
            "adapt_plan": f"{settings.API_V1_PREFIX}/plan/adapt",
            "roadmap": f"{settings.API_V1_PREFIX}/roadmap",
            "coach": f"{settings.API_V1_PREFIX}/coach/micro-drill"
        }
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check probe."""
    return {"status": "healthy", "service": "PrepPilot Backend"}
