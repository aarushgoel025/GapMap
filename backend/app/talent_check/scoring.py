
from .config import (
    CATEGORIES,
    CONFIDENCE_WEIGHTS,
    MULTI_SOURCE_BONUS,
    STUFFING_PENALTY,
    LEVEL_MULTIPLIER,
    MAX_LEVEL,
    READY_THRESHOLD,
    ALMOST_READY_THRESHOLD,
)


def candidate_level(profile: dict, category: str) -> int:
    """Calculate a candidate's level for one skill category."""

    total_weight = 0.0
    estimated_level = 0

    for skill in profile.get("skills", []):
        if skill.get("category_code") != category:
            continue

        confidence = skill.get("confidence", "medium")
        weight = CONFIDENCE_WEIGHTS.get(confidence, 0.0)

        verified_by = skill.get("verified_by", [])
        if len(verified_by) > 1:
            weight *= MULTI_SOURCE_BONUS

        if skill.get("stuffing_flag", False):
            weight *= STUFFING_PENALTY

        total_weight += weight

        estimate = skill.get("level_estimate")
        if confidence == "high" and isinstance(estimate, int):
            estimated_level = max(estimated_level, estimate)

    calculated = min(MAX_LEVEL, round(LEVEL_MULTIPLIER * total_weight))
    return max(calculated, estimated_level)


def readiness(profile: dict, company_requirements: dict) -> dict:
    """Compare candidate levels with a company's numeric requirements."""

    gaps = []
    total_required = sum(company_requirements.values())
    total_matched = 0

    for category, required in company_requirements.items():
        current = candidate_level(profile, category)
        matched = min(current, required)
        total_matched += matched

        gaps.append({
            "category_code": category,
            "category_name": CATEGORIES.get(category, category),
            "required_level": required,
            "candidate_level": current,
            "gap": max(0, required - current),
            "contribution": (
                100 * matched / total_required if total_required else 0
            ),
        })

    score = 100 * total_matched / total_required if total_required else 0

    if score >= READY_THRESHOLD:
        label = "Ready"
    elif score >= ALMOST_READY_THRESHOLD:
        label = "Almost there"
    else:
        label = "Not yet"

    return {
        "readiness_score": round(score, 2),
        "label": label,
        "skillset_gaps": gaps,
    }



def apply_level_changes(profile: dict, changes: list[dict]) -> dict:
    """Simulate skill-level changes without modifying the original profile."""

    import copy

    updated_profile = copy.deepcopy(profile)
    skills = updated_profile.setdefault("skills", [])

    for change in changes:
        category = change["category_code"]
        new_level = change["new_level"]

        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")

        if (
            not isinstance(new_level, int)
            or isinstance(new_level, bool)
            or not 0 <= new_level <= MAX_LEVEL
        ):
            raise ValueError("new_level must be an integer between 0 and 10")

        # Preserve the other categories and replace only this category
        # with a simulated skill at the requested level.
        skills[:] = [
            skill for skill in skills
            if skill.get("category_code") != category
        ]

        skills.append({
            "skill_name": f"Simulated {category}",
            "category_code": category,
            "confidence": "high",
            "level_estimate": new_level,
            "verified_by": [],
            "stuffing_flag": False,
        })

    return updated_profile
