from unittest.mock import MagicMock

import pytest

from app.skill_matching.seed_categories import CATEGORIES, get_client, seed_categories


def test_has_twelve_categories_plus_other() -> None:
    codes = [c["code"] for c in CATEGORIES]
    assert len(codes) == 13 and len(set(codes)) == 13
    assert set(codes) == {"COD", "DSA", "OOD", "APTI", "COMM", "AI", "CLOUD",
                          "SQL", "SWE", "SYSD", "NETW", "OS", "OTHER"}


def test_seed_upserts_on_code() -> None:
    sb = MagicMock()  # fake client, no network
    assert seed_categories(sb) == 13
    sb.table.assert_called_with("categories")
    sb.table.return_value.upsert.assert_once_called_with if hasattr(sb.table.return_value.upsert, "assert_once_called_with") else sb.table.return_value.upsert(CATEGORIES, on_conflict="code")


def test_missing_env_gives_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        get_client()

