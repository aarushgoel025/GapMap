"""FastAPI router for Skill Matching and Heatmap Matrix."""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from shared.schemas import ExtractionResult, MatchResult, Profile, Skill
except ImportError:
    from app.shared.schemas import ExtractionResult, MatchResult, Profile, Skill

try:
    from db.store import list_jds, list_profiles, load_jd, load_profile
except ImportError:
    from app.db.store import list_jds, list_profiles, load_jd, load_profile

try:
    from skill_matching.embeddings import load_vocab_index
    from skill_matching.scoring import calculate_match
except ImportError:
    from app.skill_matching.embeddings import load_vocab_index
    from app.skill_matching.scoring import calculate_match

router = APIRouter(prefix="/api/match", tags=["skill_matching"])

# Preload embedding vocabulary on startup
load_vocab_index()


@router.get("/status")
def status():
    return {"module": "skill_matching", "status": "active"}


def _as_profile(p: Any) -> Profile:
    if isinstance(p, Profile):
        return p
    return Profile.model_validate(p)


def _as_jd(j: Any) -> ExtractionResult:
    if isinstance(j, ExtractionResult):
        return j
    return ExtractionResult.model_validate(j)


class MatchPayload(BaseModel):
    profile_id: Optional[str] = None
    jd_id: Optional[str] = None
    profile: Optional[Profile] = None
    jd_skills: Optional[list[Skill]] = None
    jd_source_file: Optional[str] = None


class MatrixCandidate(BaseModel):
    id: str
    name: str


class MatrixJD(BaseModel):
    id: str
    company: str
    role: str
    source_file: str


class MatrixResponse(BaseModel):
    resumes: list[MatrixCandidate]
    jds: list[MatrixJD]
    matrix: list[list[float]]


@router.post("", response_model=MatchResult)
@router.post("/match", response_model=MatchResult)
def match_skills_endpoint(payload: MatchPayload) -> MatchResult:
    """POST /api/match: Match candidate profile against JD skill requirements."""
    # Resolve profile
    profile = payload.profile
    if profile is None:
        if not payload.profile_id:
            raise HTTPException(status_code=400, detail="Must provide profile_id or profile object")
        raw_p = load_profile(payload.profile_id)
        if not raw_p:
            raise HTTPException(
                status_code=404, detail=f"Profile with id '{payload.profile_id}' not found"
            )
        profile = _as_profile(raw_p)

    # Resolve JD
    jd_skills = payload.jd_skills
    jd_source = payload.jd_source_file or "unknown_jd.pdf"

    if jd_skills is None:
        if not payload.jd_id:
            raise HTTPException(status_code=400, detail="Must provide jd_id or jd_skills list")
        raw_jd = load_jd(payload.jd_id)
        if not raw_jd:
            raise HTTPException(
                status_code=404, detail=f"JD with id '{payload.jd_id}' not found"
            )
        jd_doc = _as_jd(raw_jd)
        jd_skills = jd_doc.skills
        jd_source = jd_doc.source_file

    result = calculate_match(
        jd_skills=jd_skills,
        profile_skills=profile.skills,
        jd_source_file=jd_source,
    )
    return result


@router.get("/matrix", response_model=MatrixResponse)
def get_match_matrix() -> MatrixResponse:
    """GET /api/match/matrix: Returns a 4x6 grid of scores for all sample resumes against all JDs."""
    raw_profiles = list_profiles()
    raw_jds = list_jds()

    if not raw_profiles or not raw_jds:
        raise HTTPException(status_code=404, detail="Sample profiles or JDs not found in storage")

    profiles = [_as_profile(p) for p in raw_profiles]
    jds = [_as_jd(j) for j in raw_jds]

    resumes_meta = [
        MatrixCandidate(id=p.profile_id or p.name, name=p.name or "Candidate")
        for p in profiles
    ]
    jds_meta = [
        MatrixJD(
            id=j.source_file.replace(".pdf", ""),
            company=j.company,
            role=j.role,
            source_file=j.source_file,
        )
        for j in jds
    ]

    grid: list[list[float]] = []
    for p in profiles:
        row: list[float] = []
        for j in jds:
            res = calculate_match(
                jd_skills=j.skills,
                profile_skills=p.skills,
                jd_source_file=j.source_file,
            )
            row.append(res.match_score)
        grid.append(row)

    return MatrixResponse(resumes=resumes_meta, jds=jds_meta, matrix=grid)


@router.get("/samples")
def get_samples() -> dict[str, Any]:
    """Helper endpoint listing available sample profiles and JDs for UI selector."""
    raw_profiles = list_profiles()
    raw_jds = list_jds()
    profiles = [_as_profile(p) for p in raw_profiles]
    jds = [_as_jd(j) for j in raw_jds]
    return {
        "profiles": [{"id": p.profile_id or p.name, "name": p.name} for p in profiles],
        "jds": [
            {
                "id": j.source_file.replace(".pdf", ""),
                "company": j.company,
                "role": j.role,
                "source_file": j.source_file,
            }
            for j in jds
        ],
    }
