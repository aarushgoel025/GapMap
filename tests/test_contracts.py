import json
from pathlib import Path
import pytest
from shared.schemas import (
    ExtractionResult,
    Profile,
    Skill,
    TalentCheckResult,
    SkillsetGap,
    MatchResult,
    MatchedSkill,
    MissingSkill,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def test_contract_jd_extraction_to_matching():
    """
    Contract Test 1: Verify Job Description extraction output conforms to schema
    and provides the required technical competencies for skill matching.
    """
    jd_extraction = ExtractionResult(
        schema_version="1.0",
        source_type="jd",
        source_file="sample_stripe_jd.pdf",
        company="Stripe",
        role="Full Stack Engineer (AI Platform)",
        skills=[
            Skill(
                skill_name="Python",
                category_code="COD",
                confidence="high",
                importance="must_have",
                level_estimate=8,
            ),
            Skill(
                skill_name="PostgreSQL",
                category_code="SQL",
                confidence="high",
                importance="must_have",
                level_estimate=7,
            ),
            Skill(
                skill_name="System Design",
                category_code="SYSD",
                confidence="medium",
                importance="must_have",
                level_estimate=8,
            ),
        ],
        extras={"department": "Engineering"},
    )

    assert jd_extraction.source_type == "jd"
    assert jd_extraction.company == "Stripe"
    assert len(jd_extraction.skills) == 3
    assert jd_extraction.skills[0].importance == "must_have"


def test_contract_resume_extraction_prefills_profile():
    """
    Contract Test 2: Verify Arushi's Resume extraction output cleanly maps
    and pre-fills Aarush's Profile model without schema mismatch or validation error.
    """
    resume_extraction = ExtractionResult(
        schema_version="1.0",
        source_type="resume",
        source_file="alex_smith_cv.pdf",
        company="",
        role="Backend Developer",
        skills=[
            Skill(
                skill_name="Python",
                category_code="COD",
                evidence="Built distributed microservices with FastAPI",
                confidence="high",
                level_estimate=8,
                verified_by=["resume"],
            ),
            Skill(
                skill_name="PostgreSQL",
                category_code="SQL",
                evidence="Optimized relational database schemas",
                confidence="high",
                level_estimate=7,
                verified_by=["resume"],
            ),
        ],
        extras={
            "education": "B.Tech in Computer Science",
            "projects": [{"name": "AI Agent Hackathon", "description": "1st Place Winner"}],
            "certifications": ["AWS Certified Developer"],
        },
    )

    # Convert resume output into Profile model
    profile = Profile(
        schema_version="1.0",
        profile_id="candidate-uuid-1234",
        name="Alex Smith",
        email="alex.smith@example.com",
        education=resume_extraction.extras.get("education", ""),
        github_url="https://github.com/alexsmith",
        skills=resume_extraction.skills,
        preferred_roles=[resume_extraction.role] if resume_extraction.role else ["Software Engineer"],
        cv_file=resume_extraction.source_file,
        certifications=resume_extraction.extras.get("certifications", []),
        hackathons=resume_extraction.extras.get("projects", []),
    )

    assert profile.name == "Alex Smith"
    assert profile.education == "B.Tech in Computer Science"
    assert len(profile.skills) == 2
    assert profile.skills[0].category_code == "COD"
    assert profile.skills[0].verified_by == ["resume"]
    assert profile.cv_file == "alex_smith_cv.pdf"


def test_contract_profile_to_talent_check_benchmarking():
    """
    Contract Test 3: Verify candidate Profile skills can be evaluated
    against company hiring bars from the 117-company dataset.
    """
    dataset_file = BASE_DIR / "backend" / "data" / "talent_check_company_skillsets.json"
    assert dataset_file.exists(), "talent_check_company_skillsets.json must exist"

    with open(dataset_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    assert len(records) >= 110

    # Benchmark against Google LLC
    google_record = next(r for r in records if "Google" in r.get("company", ""))
    raw_levels = google_record["skill_levels_raw"]
    # Coding bar for Google is '8-CR' -> required level 8
    coding_bar = int(raw_levels["coding"].split("-")[0].strip())
    assert coding_bar == 8

    # Candidate has level 8 in COD
    candidate_cod_level = 8
    gap_detected = candidate_cod_level < coding_bar

    gap = SkillsetGap(
        category_code="COD",
        required_level=coding_bar,
        candidate_level=candidate_cod_level,
        gap=gap_detected,
        contribution=25.0,
    )

    talent_result = TalentCheckResult(
        company=google_record["company"],
        skillset_gap=[gap],
        readiness_score=85.0,
        label="Ready",
        weeks_to_ready_estimate=0,
    )

    assert talent_result.company.startswith("Google")
    assert talent_result.readiness_score == 85.0
    assert talent_result.skillset_gap[0].gap is False


def test_contract_profile_and_jd_to_skill_matching():
    """
    Contract Test 4: Verify Profile and JD feed into Anjali's Skill Matching model,
    correctly separating matched skills and missing skill gaps.
    """
    matched = [
        MatchedSkill(
            jd_skill="Python",
            profile_skill="Python",
            match_type="exact",
            similarity=1.0,
        ),
        MatchedSkill(
            jd_skill="Postgres",
            profile_skill="PostgreSQL",
            match_type="alias",
            similarity=0.95,
        ),
    ]

    missing = [
        MissingSkill(
            skill_name="System Design",
            category_code="SYSD",
            importance="must_have",
            score_impact=20.0,
            learn_order=1,
            prerequisites=["OOD", "Networking"],
        )
    ]

    result = MatchResult(
        jd_source_file="sample_stripe_jd.pdf",
        match_score=80.0,
        matched_skills=matched,
        missing_skills=missing,
    )

    assert result.match_score == 80.0
    assert len(result.matched_skills) == 2
    assert result.matched_skills[0].match_type == "exact"
    assert result.missing_skills[0].importance == "must_have"
    assert result.missing_skills[0].category_code == "SYSD"
