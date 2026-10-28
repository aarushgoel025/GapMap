"""FastAPI router proxy for Skill Matching and Heatmap Matrix."""
from app.skill_matching.router import router, get_match_matrix, match_skills_endpoint, get_samples, status

__all__ = ["router", "get_match_matrix", "match_skills_endpoint", "get_samples", "status"]
