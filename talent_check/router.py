from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.talent_check.company_loader import load_companies
from backend.app.talent_check.scoring import apply_level_changes, readiness
from db.store import load_profile
from shared.schemas import Profile

router = APIRouter(prefix="/api/talent-check", tags=["talent_check"])


class TalentCheckRequest(BaseModel):
    company: str = Field(min_length=1)
    profile_id: Optional[str] = None
    profile: Optional[Profile] = None


class WhatIfChange(BaseModel):
    category_code: str
    new_level: int = Field(ge=0, le=10)


class WhatIfRequest(TalentCheckRequest):
    changes: list[WhatIfChange] = Field(min_length=1)


def _get_profile(request: TalentCheckRequest) -> dict:
    if request.profile is not None:
        return request.profile.model_dump()

    if not request.profile_id:
        raise HTTPException(
            status_code=422,
            detail="Provide either profile or profile_id.",
        )

    profile = load_profile(request.profile_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Profile with id '{request.profile_id}' not found",
        )
    return profile


def _get_company_requirements(company: str) -> dict[str, int]:
    try:
        companies = load_companies()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    requirements = companies.get(company)
    if requirements is None:
        raise HTTPException(status_code=404, detail=f"Company not found: {company}")
    return requirements


def _format_result(company: str, profile: dict, requirements: dict[str, int]) -> dict:
    result = readiness(profile, requirements)
    total_missing = sum(max(0, gap["required_level"] - gap["candidate_level"]) for gap in result["skillset_gaps"])
    return {
        "company": company,
        "readiness_score": result["readiness_score"],
        "label": result["label"],
        "weeks_to_ready_estimate": 0 if result["label"] == "Ready" else total_missing,
        "skillset_gap": [
            {
                "category_code": gap["category_code"],
                "required_level": gap["required_level"],
                "candidate_level": gap["candidate_level"],
                "gap": gap["candidate_level"] < gap["required_level"],
                "contribution": gap["contribution"],
            }
            for gap in result["skillset_gaps"]
        ],
    }


@router.get("/status")
def status():
    return {"module": "talent_check", "status": "initialized"}


@router.get("/companies")
def get_companies():
    try:
        companies = load_companies()
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return [{"id": name, "name": name} for name in sorted(companies)]


@router.post("")
def run_talent_check(request: TalentCheckRequest):
    profile = _get_profile(request)
    requirements = _get_company_requirements(request.company)
    return _format_result(request.company, profile, requirements)


@router.post("/whatif")
def run_talent_check_whatif(request: WhatIfRequest):
    profile = _get_profile(request)
    requirements = _get_company_requirements(request.company)

    try:
        updated_profile = apply_level_changes(
            profile,
            [change.model_dump() for change in request.changes],
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _format_result(request.company, updated_profile, requirements)
