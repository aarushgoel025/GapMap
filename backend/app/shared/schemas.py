# LOCAL COPY of the section 7 contract (schema_version 1.0), added only so this
# module can run and be tested on its own. The real file is owned by Aarush:
# replace this copy with his version and do not commit this one.
from typing import Literal, Optional
from pydantic import BaseModel, Field

CategoryCode = Literal['COD', 'DSA', 'OOD', 'APTI', 'COMM', 'AI', 'CLOUD', 'SQL',
                       'SWE', 'SYSD', 'NETW', 'OS', 'OTHER']
Confidence = Literal['high', 'medium', 'low']


class Skill(BaseModel):
    skill_name: str
    category_code: CategoryCode
    evidence: str = ''  # short quote or reason (from the brief)
    confidence: Confidence = 'medium'  # (from the brief)
    # our extras, all optional
    importance: Optional[Literal['must_have', 'nice_to_have']] = None  # JD skills only
    level_estimate: Optional[int] = Field(default=None, ge=1, le=10)
    source_section: Optional[str] = None  # skills / projects / experience / github
    verified_by: list[str] = []  # for example ['resume', 'github']
    stuffing_flag: bool = False
    models_agree: Optional[bool] = None  # Gemini and Mistral result


class ExtractionResult(BaseModel):
    schema_version: str = '1.0'
    source_type: Literal['jd', 'resume']
    source_file: str
    company: str = ''
    role: str = ''
    skills: list[Skill]
    extras: dict = {}  # resumes: education, projects, experience, certifications


class Profile(BaseModel):
    schema_version: str = '1.0'
    profile_id: Optional[str] = None
    name: str = ''
    email: str = ''
    education: str = ''
    github_url: str = ''
    skills: list[Skill] = []
    hackathons: list[dict] = []
    internships: list[dict] = []
    certifications: list[str] = []
    preferred_roles: list[str] = []
    cv_file: str = ''


class SkillsetGap(BaseModel):
    category_code: CategoryCode
    required_level: int  # 1-10, from the company snapshot
    candidate_level: int  # 1-10, calculated
    gap: bool
    contribution: float = 0.0  # points this skillset adds to the readiness score


class TalentCheckResult(BaseModel):
    company: str
    skillset_gap: list[SkillsetGap]
    readiness_score: float  # 0-100
    label: str = ''  # Ready / Almost there / Not yet
    weeks_to_ready_estimate: Optional[int] = None


class MatchedSkill(BaseModel):
    jd_skill: str
    profile_skill: str
    match_type: Literal['exact', 'alias', 'semantic']
    similarity: float = 1.0


class MissingSkill(BaseModel):
    skill_name: str
    category_code: CategoryCode
    importance: str = 'nice_to_have'
    score_impact: float = 0.0  # points gained if the candidate learns it
    learn_order: int = 0  # 1 = learn first
    prerequisites: list[str] = []


class MatchResult(BaseModel):
    jd_source_file: str
    match_score: float  # 0-100
    matched_skills: list[MatchedSkill]
    missing_skills: list[MissingSkill]
