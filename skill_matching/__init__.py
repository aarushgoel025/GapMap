"""Skill matching proxy package."""

def __getattr__(name: str):
    import app.skill_matching as _sm
    return getattr(_sm, name)

__all__ = ["normalize_name", "match_skills", "calculate_match", "router"]
