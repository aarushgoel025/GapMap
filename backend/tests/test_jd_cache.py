import pytest

from app.jd_analytics import pipeline
from app.shared.docreader import DocumentReadError
from jd_test_utils import JD_LINES, extraction, llm_skill, make_docx


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Point the data folder at a temp dir and replace both models with counting fakes."""
    monkeypatch.setenv("GAPMAP_DATA_DIR", str(tmp_path / "data"))
    (tmp_path / "data" / "jds").mkdir(parents=True)
    calls = {"a": 0, "b": 0}

    def fake_a(text):
        calls["a"] += 1
        return extraction([llm_skill("Python"), llm_skill("SQL", "SQL")], company="Acme", role="SWE")

    def fake_b(text):
        calls["b"] += 1
        return extraction([llm_skill("Python"), llm_skill("SQL", "SQL")])

    monkeypatch.setattr(pipeline, "extract_a", fake_a)
    monkeypatch.setattr(pipeline, "extract_b", fake_b)
    jd = make_docx(pipeline.jd_dir() / "jd.docx", JD_LINES)
    return {"calls": calls, "jd": jd, "monkeypatch": monkeypatch}


def test_result_is_cached_under_the_sha256_of_the_file(env):
    result = pipeline.analyze_file(env["jd"])
    assert result.source_type == "jd" and result.source_file == "jd.docx"
    cache_file = pipeline.cache_dir() / f"{pipeline.file_hash(env['jd'])}.json"
    assert cache_file.is_file()
    assert len(cache_file.stem) == 64  # a SHA-256 hex digest


def test_second_run_uses_the_cache(env):
    first = pipeline.analyze_file(env["jd"])
    second = pipeline.analyze_file(env["jd"])
    assert env["calls"] == {"a": 1, "b": 1}
    assert second == first


def test_refresh_ignores_the_cache(env):
    pipeline.analyze_file(env["jd"])
    pipeline.analyze_file(env["jd"], refresh=True)
    assert env["calls"] == {"a": 2, "b": 2}


def test_same_content_under_another_name_hits_the_cache_and_reports_the_new_name(env, tmp_path):
    pipeline.analyze_file(env["jd"])
    copy = tmp_path / "renamed.docx"
    copy.write_bytes(env["jd"].read_bytes())
    result = pipeline.analyze_file(copy, source_name="my upload.docx")
    assert env["calls"] == {"a": 1, "b": 1}
    assert result.source_file == "my upload.docx"


def test_changed_file_gets_a_new_cache_entry(env):
    pipeline.analyze_file(env["jd"])
    other = make_docx(pipeline.jd_dir() / "other.docx", ["A different job description"])
    pipeline.analyze_file(other)
    assert env["calls"] == {"a": 2, "b": 2}
    assert len(list(pipeline.cache_dir().glob("*.json"))) == 2


def test_corrupt_cache_entry_is_recomputed(env):
    pipeline.analyze_file(env["jd"])
    pipeline.cache_path(env["jd"]).write_text("{not json")
    result = pipeline.analyze_file(env["jd"])
    assert env["calls"] == {"a": 2, "b": 2}
    assert len(result.skills) == 2
    assert pipeline.get_cached(env["jd"]) is not None  # and it was rewritten


def test_one_model_result_is_not_cached(env):
    def down(text):
        raise RuntimeError("503")

    env["monkeypatch"].setattr(pipeline, "extract_b", down)
    result = pipeline.analyze_file(env["jd"])
    assert result.skills[0].models_agree is None
    assert pipeline.get_cached(env["jd"]) is None


def test_analyze_jd_finds_a_sample_by_file_name(env):
    result = pipeline.analyze_jd("jd.docx")
    assert result.source_file == "jd.docx"
    assert [p.name for p in pipeline.list_jd_files()] == ["jd.docx"]


def test_unreadable_document_gives_a_clear_error(env):
    bad = pipeline.jd_dir() / "bad.pdf"
    bad.write_bytes(b"not a pdf")
    with pytest.raises(DocumentReadError):
        pipeline.analyze_file(bad)
    assert env["calls"] == {"a": 0, "b": 0}
