import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
 
from app.jd_analytics import pipeline
from app.jd_analytics.router import router
from app.shared.schemas import ExtractionResult
from jd_test_utils import JD_LINES, extraction, llm_skill, make_docx
 
DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
 
 
@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("GAPMAP_DATA_DIR", str(tmp_path / "data"))
    (tmp_path / "data" / "jds").mkdir(parents=True)
    calls = {"n": 0}
 
    def fake(text):
        calls["n"] += 1
        return extraction([llm_skill("Python"), llm_skill("SQL", "SQL")])
 
    monkeypatch.setattr(pipeline, "extract_a", fake)
    monkeypatch.setattr(pipeline, "extract_b", fake)
    make_docx(pipeline.jd_dir() / "google_swe.docx", JD_LINES)
    (pipeline.jd_dir() / "notes.txt").write_text("not a JD")  # must not be listed
 
    app = FastAPI()
    app.include_router(router)
    return {"client": TestClient(app), "calls": calls, "monkeypatch": monkeypatch, "tmp": tmp_path}
 
 
def test_list_jds_shows_only_pdf_and_docx_and_cache_state(env):
    client = env["client"]
    assert client.get("/api/jds").json() == {"files": [{"filename": "google_swe.docx", "cached": False}]}
    client.post("/api/jd/analyze", data={"sample": "google_swe.docx"})
    assert client.get("/api/jds").json()["files"][0]["cached"] is True
 
 
def test_analyze_sample_returns_a_valid_extraction_result(env):
    response = env["client"].post("/api/jd/analyze", data={"sample": "google_swe.docx"})
    assert response.status_code == 200
    result = ExtractionResult.model_validate(response.json())
    assert result.source_type == "jd" and result.source_file == "google_swe.docx"
    assert {s.skill_name for s in result.skills} == {"Python", "SQL"}
 
 
def test_analyze_upload_reports_the_uploaded_file_name(env):
    path = make_docx(env["tmp"] / "mine.docx", JD_LINES)
    response = env["client"].post("/api/jd/analyze", files={"file": ("my_jd.docx", path.read_bytes(), DOCX_TYPE)})
    assert response.status_code == 200
    assert response.json()["source_file"] == "my_jd.docx"
 
 
def test_cache_is_used_and_refresh_bypasses_it(env):
    client = env["client"]
    client.post("/api/jd/analyze", data={"sample": "google_swe.docx"})
    client.post("/api/jd/analyze", data={"sample": "google_swe.docx"})
    assert env["calls"]["n"] == 2  # one run = two model calls; the second request hit the cache
    client.post("/api/jd/analyze?refresh=true", data={"sample": "google_swe.docx"})
    assert env["calls"]["n"] == 4
 
 
def test_must_send_exactly_one_input(env):
    client = env["client"]
    assert client.post("/api/jd/analyze").status_code == 400
    both = client.post("/api/jd/analyze", data={"sample": "google_swe.docx"},
                       files={"file": ("a.docx", b"x", DOCX_TYPE)})
    assert both.status_code == 400
 
 
def test_unknown_sample_is_404_with_a_hint(env):
    response = env["client"].post("/api/jd/analyze", data={"sample": "missing.pdf"})
    assert response.status_code == 404
    assert "GET /api/jds" in response.json()["detail"]
 
 
def test_sample_name_cannot_escape_the_folder(env):
    response = env["client"].post("/api/jd/analyze", data={"sample": "../secret.pdf"})
    assert response.status_code == 400
 
 
def test_bad_uploads_are_rejected(env):
    client = env["client"]
    assert client.post("/api/jd/analyze", files={"file": ("a.txt", b"hello", "text/plain")}).status_code == 400
    assert client.post("/api/jd/analyze", files={"file": ("a.docx", b"", DOCX_TYPE)}).status_code == 400
 
 
def test_unreadable_upload_is_422(env):
    response = env["client"].post("/api/jd/analyze", files={"file": ("a.pdf", b"not a pdf", "application/pdf")})
    assert response.status_code == 422
    assert "Could not read" in response.json()["detail"]
 
 
def test_both_models_down_is_502(env):
    def down(text):
        raise RuntimeError("503 unavailable")
 
    env["monkeypatch"].setattr(pipeline, "extract_a", down)
    env["monkeypatch"].setattr(pipeline, "extract_b", down)
    response = env["client"].post("/api/jd/analyze", data={"sample": "google_swe.docx"})
    assert response.status_code == 502
    assert "Both models failed" in response.json()["detail"]
 
 
def test_spaces_around_the_sample_name_are_ignored(env):
    response = env["client"].post("/api/jd/analyze", data={"sample": "   google_swe.docx  "})
    assert response.status_code == 200
    assert response.json()["source_file"] == "google_swe.docx"
 
