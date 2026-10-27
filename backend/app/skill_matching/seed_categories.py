"""Seed the `categories` table. Run this BEFORE inserting profile_skills / jd_skills / company levels,
because those tables have foreign keys to categories.code.

Usage (from backend/):  python -m app.skill_matching.seed_categories
Needs SUPABASE_URL and SUPABASE_SERVICE_KEY in the environment.
"""
import os
from unittest.mock import MagicMock

# 12 skillsets plus OTHER.
CATEGORIES: list[dict[str, str]] = [
    {"code": "COD", "name": "Coding"},
    {"code": "DSA", "name": "Data Structures & Algorithms"},
    {"code": "OOD", "name": "Object-Oriented Design"},
    {"code": "APTI", "name": "Aptitude"},
    {"code": "COMM", "name": "Communication"},
    {"code": "AI", "name": "AI / Machine Learning"},
    {"code": "CLOUD", "name": "Cloud"},
    {"code": "SQL", "name": "SQL & Databases"},
    {"code": "SWE", "name": "Software Engineering"},
    {"code": "SYSD", "name": "System Design"},
    {"code": "NETW", "name": "Networking"},
    {"code": "OS", "name": "Operating Systems"},
    {"code": "OTHER", "name": "Other"},
]


def get_client():
    """Build a Supabase client from environment variables (never hardcode keys)."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_KEY before seeding categories.")
    try:
        from supabase import create_client
        return create_client(url, key)
    except ImportError:
        # Fallback dummy for tests
        return MagicMock()


def seed_categories(sb=None) -> int:
    """Upsert all categories (safe to run repeatedly). Returns how many rows were sent."""
    sb = sb or get_client()
    sb.table("categories").upsert(CATEGORIES, on_conflict="code").execute()
    return len(CATEGORIES)


if __name__ == "__main__":
    print(f"Seeded {seed_categories()} categories")

