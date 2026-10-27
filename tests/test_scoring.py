
from backend.app.talent_check.scoring import candidate_level, readiness


def test_candidate_level_uses_confidence_weights():
    profile = {
        "skills": [
            {
                "skill_name": "Python",
                "category_code": "COD",
                "confidence": "high",
                "verified_by": [],
                "stuffing_flag": False,
            },
            {
                "skill_name": "SQL",
                "category_code": "SQL",
                "confidence": "medium",
                "verified_by": [],
                "stuffing_flag": False,
            },
        ]
    }

    assert candidate_level(profile, "COD") == 2
    assert candidate_level(profile, "SQL") == 2


def test_candidate_level_never_exceeds_ten():
    profile = {
        "skills": [
            {
                "skill_name": f"Skill {i}",
                "category_code": "COD",
                "confidence": "high",
                "verified_by": ["resume", "github"],
                "stuffing_flag": False,
            }
            for i in range(20)
        ]
    }

    assert candidate_level(profile, "COD") == 10


def test_readiness_is_one_hundred_when_all_levels_are_met():
    profile = {
        "skills": [
            {
                "skill_name": "Python",
                "category_code": "COD",
                "confidence": "high",
                "level_estimate": 10,
                "verified_by": [],
                "stuffing_flag": False,
            },
            {
                "skill_name": "SQL",
                "category_code": "SQL",
                "confidence": "high",
                "level_estimate": 10,
                "verified_by": [],
                "stuffing_flag": False,
            },
        ]
    }

    result = readiness(profile, {"COD": 5, "SQL": 5})

    assert result["readiness_score"] == 100
    assert result["label"] == "Ready"


def test_readiness_stays_between_zero_and_one_hundred():
    profile = {"skills": []}

    result = readiness(profile, {"COD": 5, "SQL": 7})

    assert 0 <= result["readiness_score"] <= 100
    assert result["label"] == "Not yet"


def test_adding_skill_never_decreases_score():
    profile = {
        "skills": [
            {
                "skill_name": "Python",
                "category_code": "COD",
                "confidence": "high",
            }
        ]
    }

    requirements = {"COD": 8}

    before = readiness(profile, requirements)["readiness_score"]

    profile["skills"].append({
        "skill_name": "Java",
        "category_code": "COD",
        "confidence": "high",
    })

    after = readiness(profile, requirements)["readiness_score"]

    assert after >= before


def test_different_companies_produce_different_scores():
    profile = {
        "skills": [
            {
                "skill_name": "Python",
                "category_code": "COD",
                "confidence": "high",
            }
        ]
    }

    company_a = {"COD": 2}
    company_b = {"COD": 8}

    score_a = readiness(profile, company_a)["readiness_score"]
    score_b = readiness(profile, company_b)["readiness_score"]

    assert score_a != score_b


from backend.app.talent_check.scoring import apply_level_changes


def test_whatif_does_not_modify_original_profile():
    profile = {
        "skills": [
            {
                "skill_name": "SQL",
                "category_code": "SQL",
                "confidence": "high",
                "level_estimate": 5,
                "verified_by": [],
                "stuffing_flag": False,
            }
        ]
    }

    updated = apply_level_changes(
        profile,
        [{"category_code": "SQL", "new_level": 8}],
    )

    assert profile["skills"][0]["level_estimate"] == 5
    assert updated["skills"][0]["level_estimate"] == 8


def test_whatif_rejects_unknown_category():
    profile = {"skills": []}

    try:
        apply_level_changes(
            profile,
            [{"category_code": "UNKNOWN", "new_level": 5}],
        )
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for unknown category"
