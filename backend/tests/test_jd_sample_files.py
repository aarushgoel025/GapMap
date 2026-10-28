"""Runs JD Analytics on every sample JD in backend/data/jds (uses the cache).

The first run needs GEMINI_/MISTRAL_ keys in .env and fills backend/data/cache.
After that these tests are instant and need no network.
"""
import os

import pytest

from app.jd_analytics.pipeline import analyze_jd, get_cached, jd_dir, list_jd_files
from app.shared.schemas import ExtractionResult

CATEGORIES = ['COD', 'DSA', 'OOD', 'APTI', 'COMM', 'AI', 'CLOUD', 'SQL', 'SWE', 'SYSD', 'NETW', 'OS', 'OTHER']
JD_FILES = [p.name for p in list_jd_files()]  # every .pdf and .docx found in the folder


@pytest.mark.skipif(not JD_FILES, reason="no sample JDs found in backend/data/jds")
@pytest.mark.parametrize("jd_file", JD_FILES)
def test_jd_output_is_valid(jd_file):
    has_keys = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("MISTRAL_API_KEY"))
    if get_cached(jd_dir() / jd_file) is None and not has_keys:
        pytest.skip("not cached yet and no API keys: run once with keys to fill backend/data/cache")

    result = analyze_jd(jd_file)  # uses the cache

    assert isinstance(result, ExtractionResult)
    assert result.source_type == "jd"
    assert len(result.skills) >= 8
    assert all(s.category_code in CATEGORIES for s in result.skills)
    assert all(s.importance in ("must_have", "nice_to_have") for s in result.skills)
    names = [" ".join(s.skill_name.lower().split()) for s in result.skills]
    assert all(names) and len(names) == len(set(names))  # no empty or duplicate skill names
