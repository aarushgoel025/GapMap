"""Three-layer skill matching engine: Exact -> Alias -> Semantic."""
import json
from dataclasses import dataclass
from typing import Optional

from app.shared.schemas import MatchedSkill, Skill
from app.skill_matching.config import (
    ALIAS_CREDIT,
    ALIASES_PATH,
    EXACT_CREDIT,
    SEMANTIC_MULTIPLIER,
    SEMANTIC_THRESHOLD,
)
from app.skill_matching.embeddings import embed_texts
from app.skill_matching.normalize import normalize_name

_ALIASES: Optional[dict[str, str]] = None


def get_aliases() -> dict[str, str]:
    """Load and cache aliases lookup dictionary."""
    global _ALIASES
    if _ALIASES is None:
        if ALIASES_PATH.exists():
            with open(ALIASES_PATH, "r", encoding="utf-8") as f:
                _ALIASES = json.load(f)
        else:
            _ALIASES = {}
    return _ALIASES


@dataclass
class MatchResultItem:
    matched_skill: Optional[MatchedSkill]
    credit: float


def match_single_skill(
    jd_skill: Skill,
    profile_skills: list[Skill],
    semantic_threshold: float = SEMANTIC_THRESHOLD,
) -> MatchResultItem:
    """Matches a single JD skill against candidate profile skills across 3 layers.
    Returns (MatchedSkill, credit). If credit < 0.5, considered missing.
    """
    if not profile_skills:
        return MatchResultItem(matched_skill=None, credit=0.0)

    j_norm = normalize_name(jd_skill.skill_name)
    aliases = get_aliases()
    j_canon = aliases.get(j_norm, j_norm)

    # Layer 1: Exact Match (Credit 1.0)
    for p in profile_skills:
        p_norm = normalize_name(p.skill_name)
        if j_norm == p_norm:
            return MatchResultItem(
                matched_skill=MatchedSkill(
                    jd_skill=jd_skill.skill_name,
                    profile_skill=p.skill_name,
                    match_type="exact",
                    similarity=1.0,
                ),
                credit=EXACT_CREDIT,
            )

    # Layer 2: Alias / Family Match (Credit 0.9)
    for p in profile_skills:
        p_norm = normalize_name(p.skill_name)
        p_canon = aliases.get(p_norm, p_norm)
        if (
            (j_canon == p_canon and j_canon != j_norm)
            or aliases.get(j_norm) == p_norm
            or aliases.get(p_norm) == j_norm
            or (j_canon == p_norm)
            or (p_canon == j_norm)
        ):
            return MatchResultItem(
                matched_skill=MatchedSkill(
                    jd_skill=jd_skill.skill_name,
                    profile_skill=p.skill_name,
                    match_type="alias",
                    similarity=0.9,
                ),
                credit=ALIAS_CREDIT,
            )

    # Layer 3: Semantic Match using Embeddings (Credit 0.8 * similarity)
    # Include category context when available
    jd_text = f"{jd_skill.category_code} {jd_skill.skill_name}".strip()
    profile_texts = [f"{p.category_code} {p.skill_name}".strip() for p in profile_skills]

    jd_embed = embed_texts([jd_text])[0]
    p_embeds = embed_texts(profile_texts)

    sims = p_embeds @ jd_embed
    best_idx = int(sims.argmax())
    best_sim = float(sims[best_idx])

    if best_sim >= semantic_threshold:
        best_p = profile_skills[best_idx]
        credit = round(SEMANTIC_MULTIPLIER * best_sim, 4)
        return MatchResultItem(
            matched_skill=MatchedSkill(
                jd_skill=jd_skill.skill_name,
                profile_skill=best_p.skill_name,
                match_type="semantic",
                similarity=round(best_sim, 4),
            ),
            credit=credit,
        )

    return MatchResultItem(matched_skill=None, credit=0.0)


def match_skills(
    jd_skills: list[Skill],
    profile_skills: list[Skill],
    semantic_threshold: float = SEMANTIC_THRESHOLD,
) -> list[tuple[Skill, MatchResultItem]]:
    """Evaluates each JD skill against the profile skills, returning pairs of (jd_skill, MatchResultItem)."""
    results: list[tuple[Skill, MatchResultItem]] = []
    for jd_skill in jd_skills:
        res = match_single_skill(jd_skill, profile_skills, semantic_threshold=semantic_threshold)
        results.append((jd_skill, res))
    return results

