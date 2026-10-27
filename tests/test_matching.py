"""Comprehensive tests for Skill Matching module."""
from unittest.mock import MagicMock
import pytest

from app.shared.schemas import Skill, Profile, ExtractionResult, MatchedSkill, MatchResult
from app.skill_matching.matcher import match_single_skill, match_skills
from app.skill_matching.scoring import calculate_match, get_skill_weight
from app.skill_matching.router import get_match_matrix


def test_exact_match_example():
    """Exact match: Node.js equals nodejs, giving credit 1.0 and match_type 'exact'."""
    jd_skill = Skill(skill_name="Node.js", category_code="SWE", importance="must_have")
    profile_skills = [
        Skill(skill_name="nodejs", category_code="SWE", confidence="high"),
        Skill(skill_name="Python", category_code="COD", confidence="high"),
    ]
    res = match_single_skill(jd_skill, profile_skills)
    assert res.matched_skill is not None
    assert res.matched_skill.match_type == "exact"
    assert res.credit == 1.0
    assert res.matched_skill.similarity == 1.0


def test_alias_match_example():
    """Alias match: k8s matches kubernetes, postgres matches postgresql (credit 0.9, match_type 'alias')."""
    jd_skill_k8s = Skill(skill_name="kubernetes", category_code="CLOUD", importance="must_have")
    profile_skills = [
        Skill(skill_name="k8s", category_code="CLOUD", confidence="high"),
        Skill(skill_name="postgres", category_code="SQL", confidence="high"),
    ]
    res_k8s = match_single_skill(jd_skill_k8s, profile_skills)
    assert res_k8s.matched_skill is not None
    assert res_k8s.matched_skill.match_type == "alias"
    assert res_k8s.credit == 0.9

    jd_skill_pg = Skill(skill_name="PostgreSQL", category_code="SQL", importance="nice_to_have")
    res_pg = match_single_skill(jd_skill_pg, profile_skills)
    assert res_pg.matched_skill is not None
    assert res_pg.matched_skill.match_type == "alias"
    assert res_pg.credit == 0.9


def test_semantic_match_example():
    """Semantic match: semantically similar skill above threshold matches with credit 0.8 * similarity."""
    jd_skill = Skill(skill_name="Natural Language Processing", category_code="AI", importance="must_have")
    profile_skills = [
        Skill(skill_name="Natural Language", category_code="AI", confidence="high"),
        Skill(skill_name="HTML", category_code="SWE", confidence="low"),
    ]
    res = match_single_skill(jd_skill, profile_skills, semantic_threshold=0.75)
    assert res.matched_skill is not None
    assert res.matched_skill.match_type == "semantic"
    assert res.credit == pytest.approx(0.8 * res.matched_skill.similarity, rel=1e-3)
    assert res.matched_skill.similarity >= 0.75


def test_full_match_scores_100():
    """A profile possessing all JD skills exactly scores 100."""
    jd_skills = [
        Skill(skill_name="Python", category_code="COD", importance="must_have"),
        Skill(skill_name="FastAPI", category_code="SWE", importance="must_have"),
        Skill(skill_name="Docker", category_code="CLOUD", importance="nice_to_have"),
    ]
    profile_skills = [
        Skill(skill_name="python", category_code="COD"),
        Skill(skill_name="fastapi", category_code="SWE"),
        Skill(skill_name="docker", category_code="CLOUD"),
    ]
    result = calculate_match(jd_skills, profile_skills, "full_match.pdf")
    assert result.match_score == 100.0
    assert len(result.matched_skills) == 3
    assert len(result.missing_skills) == 0


def test_empty_profile_scores_0():
    """An empty candidate profile scores 0 against any JD skills."""
    jd_skills = [
        Skill(skill_name="Python", category_code="COD", importance="must_have"),
        Skill(skill_name="FastAPI", category_code="SWE", importance="nice_to_have"),
    ]
    profile_skills = []
    result = calculate_match(jd_skills, profile_skills, "test_jd.pdf")
    assert result.match_score == 0.0
    assert len(result.matched_skills) == 0
    assert len(result.missing_skills) == 2


def test_scoring_weights():
    """Weights are must_have=2, nice_to_have=1, unknown=1."""
    must_have = Skill(skill_name="A", category_code="COD", importance="must_have")
    nice_to_have = Skill(skill_name="B", category_code="COD", importance="nice_to_have")
    unknown = Skill(skill_name="C", category_code="COD", importance=None)

    assert get_skill_weight(must_have) == 2.0
    assert get_skill_weight(nice_to_have) == 1.0
    assert get_skill_weight(unknown) == 1.0


def test_missing_skills_score_impact_and_prerequisites():
    """Missing skills must have score_impact, prerequisites from prereqs.json (skipping known), and learn_order."""
    jd_skills = [
        Skill(skill_name="kubernetes", category_code="CLOUD", importance="must_have"),  # weight 2
        Skill(skill_name="docker", category_code="CLOUD", importance="nice_to_have"),    # weight 1
    ]
    # Profile has linux
    profile_skills = [
        Skill(skill_name="linux", category_code="OS"),
    ]
    # Total weight: 2 + 1 = 3
    # Both are missing.
    result = calculate_match(jd_skills, profile_skills, "jd.pdf")
    assert len(result.missing_skills) == 2

    # Impact should sum to 100
    impacts = [m.score_impact for m in result.missing_skills]
    assert pytest.approx(sum(impacts), abs=0.1) == 100.0

    # Prereq check:
    # kubernetes needs docker.
    # docker needs linux, but candidate already has linux! So docker's unmet prereqs should be empty.
    # kubernetes needs docker, which candidate does NOT have, so docker should be in kubernetes prereqs.
    k8s_missing = next(m for m in result.missing_skills if m.skill_name == "kubernetes")
    docker_missing = next(m for m in result.missing_skills if m.skill_name == "docker")

    assert "docker" in k8s_missing.prerequisites
    assert "linux" not in docker_missing.prerequisites  # Skipped because candidate already has linux!

    # Learn order: docker is a prerequisite for kubernetes, so docker must be learned before kubernetes!
    assert docker_missing.learn_order < k8s_missing.learn_order


def test_matrix_is_not_constant():
    """GET /api/match/matrix returns 4x6 grid that is not constant across candidates and JDs."""
    res = get_match_matrix()
    matrix = res.matrix
    assert len(matrix) == 4
    assert len(matrix[0]) == 6

    # Flatten all scores
    scores = [score for row in matrix for score in row]
    assert len(set(scores)) > 1, "Matrix scores must not be constant!"

    # Sanity checks from brief:
    # 1. Entry-level support candidate (row 2: Rohan Verma) should do best on Oracle database role
    support_row = next(i for i, r in enumerate(res.resumes) if "support" in r.id.lower() or "rohan" in r.name.lower())
    oracle_db_col = next(j for j, jd in enumerate(res.jds) if "oracle_database" in jd.id.lower())
    assert matrix[support_row][oracle_db_col] == max(matrix[support_row])

    # 2. Data-leaning analyst (Priya Patel) should score higher on data roles than pure SWE roles
    data_row = next(i for i, r in enumerate(res.resumes) if "data" in r.id.lower() or "priya" in r.name.lower())
    data_col = next(j for j, jd in enumerate(res.jds) if "data" in jd.id.lower())
    swe_col = next(j for j, jd in enumerate(res.jds) if "software_engineer" in jd.id.lower())
    assert matrix[data_row][data_col] > matrix[data_row][swe_col]
