from fastapi import APIRouter

router = APIRouter(prefix="/api/jd", tags=["jd_analytics"])


@router.get("/status")
def status():
    return {"module": "jd_analytics", "status": "initialized"}
