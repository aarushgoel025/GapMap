from fastapi import APIRouter

router = APIRouter(prefix="/api/skill-matching", tags=["skill_matching"])


@router.get("/status")
def status():
    return {"module": "skill_matching", "status": "initialized"}
