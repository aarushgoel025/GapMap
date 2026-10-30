import os
import sys
from pathlib import Path

# Ensure project root is in sys.path so modules like shared, db, profile can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers from all modules
from profile.router import router as profile_router
from jd_analytics.router import router as jd_router
from resume_parsing.router import router as resume_router, list_sample_resumes
from talent_check.router import router as talent_check_router, get_companies
from app.skill_matching.router import router as skill_matching_router

app = FastAPI(
    title="GapMap API",
    description="GapMap backend API for skill matching, resume parsing, JD analytics, and talent verification.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS Configuration (Production & Development friendly)
# ---------------------------------------------------------------------------
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
allowed_origins = [
    origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
]
if not allowed_origins:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# If CORS_ORIGINS is "*", allow all origins (allow_credentials=False for wildcard standard)
if allowed_origins == ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https:\/\/.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------------------------------------------------------
# Global Error Handlers (returning {detail: message})
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException and return standard {detail: message} structure."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with standard {detail: message} structure."""
    errors = exc.errors()
    error_msgs = []
    for err in errors:
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        error_msgs.append(f"{loc}: {msg}" if loc else msg)
    detail_message = "; ".join(error_msgs)
    return JSONResponse(
        status_code=422,
        content={"detail": detail_message},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions and return {detail: message}."""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Include Routers
# ---------------------------------------------------------------------------
app.include_router(profile_router)
app.include_router(jd_router)
app.include_router(resume_router)
app.include_router(talent_check_router)
app.include_router(skill_matching_router)

legacy_matching_router = APIRouter(prefix="/api/skill-matching", tags=["skill_matching"])

@legacy_matching_router.get("/status")
def legacy_matching_status():
    return {"module": "skill_matching", "status": "initialized"}

app.include_router(legacy_matching_router)


# ---------------------------------------------------------------------------
# Direct /api Aliases from Specification Table
# ---------------------------------------------------------------------------
@app.get("/api/companies", tags=["talent_check"])
def api_companies():
    """Alias for GET /api/companies (contract table section 7 & 14)."""
    return get_companies()


@app.get("/api/resumes", tags=["resume_parsing"])
def api_resumes():
    """Alias for GET /api/resumes (contract table section 7 & 12)."""
    return list_sample_resumes()


# ---------------------------------------------------------------------------
# Base & Diagnostic Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "app": "GapMap"}


@app.get("/test-error")
def test_error_endpoint():
    """Diagnostic endpoint to verify global error handling returns {detail: message}."""
    raise RuntimeError("Intentional test server error")
