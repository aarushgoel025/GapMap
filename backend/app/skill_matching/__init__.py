try:
    from app.skill_matching.matcher import match_skills
    from app.skill_matching.normalize import normalize_name
    from app.skill_matching.scoring import calculate_match
    from app.skill_matching.router import router
except ImportError:
    from skill_matching.matcher import match_skills
    from skill_matching.normalize import normalize_name
    from skill_matching.scoring import calculate_match
    from skill_matching.router import router

__all__ = ["normalize_name", "match_skills", "calculate_match", "router"]
