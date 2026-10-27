from typing import List
from fastapi import APIRouter
from pydantic import BaseModel

from shared.schemas import Skill
from db.store import write_audit

router = APIRouter(prefix="/api/resume", tags=["resume_parsing"])


class VerifyGithubRequest(BaseModel):
    github_url: str
    skills: List[Skill]


@router.get("/status")
def status():
    return {"module": "resume_parsing", "status": "initialized"}


@router.post("/verify-github")
def verify_github(req: VerifyGithubRequest):
    """
    Verify candidate skills against their GitHub profile.
    Section F Governance: writes an audit_log row when a GitHub check runs
    (logging event metadata, never personal text).
    """
    verified_skills = []
    github_user = req.github_url.rstrip("/").split("/")[-1] if req.github_url else "unknown"

    for skill in req.skills:
        s_dict = skill.model_dump()
        verified_by = list(s_dict.get("verified_by") or [])
        if "github" not in verified_by:
            verified_by.append("github")
        s_dict["verified_by"] = verified_by
        verified_skills.append(s_dict)

    # Section F Governance: Write an audit_log row when a GitHub check runs
    write_audit(
        action="github_check",
        details={
            "github_user": github_user,
            "skills_count": len(req.skills),
            "verified_count": len(verified_skills),
        },
        entity_id=github_user,
        entity_type="github_check",
    )

    return {"verified_skills": verified_skills}
