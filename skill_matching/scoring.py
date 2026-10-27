"""Scoring engine: computes match score, score impacts, prerequisites, and learning order."""
import json
from pathlib import Path
from typing import Optional

from app.shared.schemas import MatchedSkill, MatchResult, MissingSkill, Skill
from app.skill_matching.config import (
    MISSING_THRESHOLD,
    PREREQS_PATH,
    WEIGHT_MUST_HAVE,
    WEIGHT_NICE_TO_HAVE,
    WEIGHT_UNKNOWN,
)
from app.skill_matching.matcher import get_aliases, match_skills
from app.skill_matching.normalize import normalize_name

_PREREQS: Optional[dict[str, list[str]]] = None


def get_prereqs() -> dict[str, list[str]]:
    """Load and cache prerequisites dictionary."""
    global _PREREQS
    if _PREREQS is None:
        if PREREQS_PATH.exists():
            with open(PREREQS_PATH, "r", encoding="utf-8") as f:
                _PREREQS = json.load(f)
        else:
            _PREREQS = {}
    return _PREREQS


def get_skill_weight(skill: Skill) -> float:
    """Return importance weight: must_have = 2, nice_to_have = 1, unknown = 1."""
    if skill.importance == "must_have":
        return WEIGHT_MUST_HAVE
    elif skill.importance == "nice_to_have":
        return WEIGHT_NICE_TO_HAVE
    return WEIGHT_UNKNOWN


def calculate_match(
    jd_skills: list[Skill],
    profile_skills: list[Skill],
    jd_source_file: str = "jd_unknown.pdf",
    semantic_threshold: float = 0.75,
) -> MatchResult:
    """Calculates MatchResult including match_score, matched_skills, and ordered missing_skills."""
    if not jd_skills:
        return MatchResult(
            jd_source_file=jd_source_file,
            match_score=0.0,
            matched_skills=[],
            missing_skills=[],
        )

    matched_pairs = match_skills(
        jd_skills=jd_skills,
        profile_skills=profile_skills,
        semantic_threshold=semantic_threshold,
    )

    total_weight = sum(get_skill_weight(s) for s in jd_skills)
    weighted_credit_sum = 0.0

    matched_skills: list[MatchedSkill] = []
    raw_missing: list[tuple[Skill, float, float]] = []  # (skill, weight, score_impact)

    for jd_skill, match_item in matched_pairs:
        w = get_skill_weight(jd_skill)
        c = match_item.credit
        weighted_credit_sum += w * c

        if c >= MISSING_THRESHOLD and match_item.matched_skill:
            matched_skills.append(match_item.matched_skill)
        else:
            score_impact = round(100.0 * w / total_weight, 2) if total_weight > 0 else 0.0
            raw_missing.append((jd_skill, w, score_impact))

    match_score = (
        round(100.0 * weighted_credit_sum / total_weight, 1) if total_weight > 0 else 0.0
    )

    # Process missing skills: prerequisites and learning order
    prereqs_db = get_prereqs()
    aliases = get_aliases()

    # Pre-collect normalized profile skills to skip already acquired prerequisites
    profile_known = set()
    for p in profile_skills:
        norm = normalize_name(p.skill_name)
        profile_known.add(norm)
        profile_known.add(aliases.get(norm, norm))

    # Map missing skills with filtered prerequisites
    prepared_missing: list[dict] = []
    missing_names_set = set()
    for skill, w, impact in raw_missing:
        norm_name = normalize_name(skill.skill_name)
        canon_name = aliases.get(norm_name, norm_name)
        missing_names_set.add(norm_name)
        missing_names_set.add(canon_name)

        # Lookup prereqs
        declared_prereqs = prereqs_db.get(norm_name, []) or prereqs_db.get(canon_name, [])
        # Skip ones candidate already possesses
        unmet_prereqs = [
            pr
            for pr in declared_prereqs
            if normalize_name(pr) not in profile_known
            and aliases.get(normalize_name(pr), normalize_name(pr)) not in profile_known
        ]

        prepared_missing.append({
            "skill": skill,
            "norm": norm_name,
            "canon": canon_name,
            "weight": w,
            "score_impact": impact,
            "prerequisites": unmet_prereqs,
        })

    # Determine learn_order: prerequisites first, then score_impact descending.
    # A missing skill that is needed as a prerequisite by other missing skills must come first.
    # Compute dependency depth for each missing skill.
    def get_dep_depth(item: dict, visited: set) -> int:
        depth = 0
        norm = item["norm"]
        canon = item["canon"]
        for other in prepared_missing:
            other_norm = other["norm"]
            if other_norm in visited:
                continue
            # If other requires this item, this item is a prereq (should be earlier)
            other_prereqs = [normalize_name(p) for p in other["prerequisites"]]
            if norm in other_prereqs or canon in other_prereqs:
                depth -= 1
        # If this item requires other missing skills, it must come after them
        for pr in item["prerequisites"]:
            pr_norm = normalize_name(pr)
            if pr_norm in missing_names_set:
                depth += 1
        return depth

    # Sort missing skills: lower depth (prerequisites) first, then score_impact descending (-impact), then name
    sorted_missing = sorted(
        prepared_missing,
        key=lambda x: (get_dep_depth(x, set()), -x["score_impact"], x["skill"].skill_name),
    )

    final_missing_skills: list[MissingSkill] = []
    for rank, item in enumerate(sorted_missing, start=1):
        s = item["skill"]
        final_missing_skills.append(
            MissingSkill(
                skill_name=s.skill_name,
                category_code=s.category_code,
                importance=s.importance or "nice_to_have",
                score_impact=item["score_impact"],
                learn_order=rank,
                prerequisites=item["prerequisites"],
            )
        )

    return MatchResult(
        jd_source_file=jd_source_file,
        match_score=match_score,
        matched_skills=matched_skills,
        missing_skills=final_missing_skills,
    )

