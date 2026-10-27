from fastapi import APIRouter

router = APIRouter(prefix="/api/talent-check", tags=["talent_check"])


@router.get("/status")
def status():
    return {"module": "talent_check", "status": "initialized"}
