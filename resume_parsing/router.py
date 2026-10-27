from fastapi import APIRouter

router = APIRouter(prefix="/api/resume", tags=["resume_parsing"])


@router.get("/status")
def status():
    return {"module": "resume_parsing", "status": "initialized"}
