"""Skill matching package."""

def __getattr__(name: str):
    if name == "normalize_name":
        from app.skill_matching.normalize import normalize_name
        return normalize_name
    elif name == "match_skills":
        from app.skill_matching.matcher import match_skills
        return match_skills
    elif name == "calculate_match":
        from app.skill_matching.scoring import calculate_match
        return calculate_match
    elif name == "router":
        from app.skill_matching.router import router
        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["normalize_name", "match_skills", "calculate_match", "router"]
