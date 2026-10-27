import json
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
import db.store as store


@pytest.fixture(autouse=True)
def setup_json_fallback_store(tmp_path, monkeypatch):
    """
    Ensure all tests run against an isolated temporary directory using the JSON fallback,
    with Supabase client explicitly disabled.
    """
    test_profiles_dir = tmp_path / "profiles"
    test_runs_dir = tmp_path / "runs"
    test_jds_dir = tmp_path / "jds"

    test_profiles_dir.mkdir(parents=True, exist_ok=True)
    test_runs_dir.mkdir(parents=True, exist_ok=True)
    test_jds_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(store, "_supabase_client", None)
    monkeypatch.setattr(store, "PROFILES_DIR", test_profiles_dir)
    monkeypatch.setattr(store, "RUNS_DIR", test_runs_dir)
    monkeypatch.setattr(store, "JDS_DIR", test_jds_dir)

    yield {
        "profiles_dir": test_profiles_dir,
        "runs_dir": test_runs_dir,
        "jds_dir": test_jds_dir,
    }


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_create_profile_success(client, setup_json_fallback_store):
    """Test POST /api/profile creates a profile and writes audit log using JSON fallback."""
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "education": "B.Tech Computer Science",
        "github_url": "https://github.com/janedoe",
        "skills": [
            {
                "skill_name": "Python",
                "category_code": "COD",
                "evidence": "Built backend REST services with FastAPI",
                "confidence": "high",
                "level_estimate": 8,
            },
            {
                "skill_name": "PostgreSQL",
                "category_code": "SQL",
                "evidence": "Managed production database schemas",
                "confidence": "medium",
                "level_estimate": 7,
            },
        ],
        "preferred_roles": ["Backend Developer", "Full Stack Engineer"],
    }

    response = client.post("/api/profile", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane.doe@example.com"
    assert len(data["skills"]) == 2
    assert "profile_id" in data
    profile_id = data["profile_id"]

    # Verify JSON file was written to disk
    profiles_dir = setup_json_fallback_store["profiles_dir"]
    saved_file = profiles_dir / f"{profile_id}.json"
    assert saved_file.exists()

    with open(saved_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    assert file_data["profile_id"] == profile_id
    assert file_data["name"] == "Jane Doe"

    # Verify audit log was recorded in runs/audit_log.json
    runs_dir = setup_json_fallback_store["runs_dir"]
    audit_file = runs_dir / "audit_log.json"
    assert audit_file.exists()

    with open(audit_file, "r", encoding="utf-8") as f:
        audit_entries = json.load(f)
    assert len(audit_entries) >= 1
    latest_audit = audit_entries[-1]
    assert latest_audit["action"] == "create_profile"
    assert latest_audit["entity_id"] == profile_id


def test_get_profile_by_id(client):
    """Test GET /api/profile/{id} retrieves existing profile."""
    create_payload = {
        "name": "Alex Smith",
        "email": "alex@example.com",
        "skills": [
            {
                "skill_name": "Docker",
                "category_code": "CLOUD",
                "evidence": "Containerized microservices",
                "confidence": "high",
            }
        ],
    }
    create_resp = client.post("/api/profile", json=create_payload)
    assert create_resp.status_code == 201
    profile_id = create_resp.json()["profile_id"]

    get_resp = client.get(f"/api/profile/{profile_id}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["profile_id"] == profile_id
    assert retrieved["name"] == "Alex Smith"
    assert retrieved["skills"][0]["category_code"] == "CLOUD"


def test_get_profile_not_found(client):
    """Test GET /api/profile/{id} returns 404 with standard {detail: message}."""
    resp = client.get("/api/profile/non-existent-id-000")
    assert resp.status_code == 404
    data = resp.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_update_profile(client, setup_json_fallback_store):
    """Test PUT /api/profile/{id} updates existing profile and creates audit entry."""
    create_payload = {
        "name": "Sam Taylor",
        "email": "sam@example.com",
        "education": "B.Sc Computing",
    }
    create_resp = client.post("/api/profile", json=create_payload)
    profile_id = create_resp.json()["profile_id"]

    update_payload = {
        "name": "Sam Taylor, MSc",
        "email": "sam.taylor@example.com",
        "education": "M.Sc Artificial Intelligence",
        "skills": [
            {
                "skill_name": "PyTorch",
                "category_code": "AI",
                "evidence": "Trained transformer models",
                "confidence": "high",
            }
        ],
    }
    put_resp = client.put(f"/api/profile/{profile_id}", json=update_payload)
    assert put_resp.status_code == 200
    updated = put_resp.json()
    assert updated["profile_id"] == profile_id
    assert updated["name"] == "Sam Taylor, MSc"
    assert updated["education"] == "M.Sc Artificial Intelligence"
    assert len(updated["skills"]) == 1

    # Verify audit log recorded update_profile
    runs_dir = setup_json_fallback_store["runs_dir"]
    audit_file = runs_dir / "audit_log.json"
    with open(audit_file, "r", encoding="utf-8") as f:
        audit_entries = json.load(f)

    actions = [entry["action"] for entry in audit_entries]
    assert "update_profile" in actions


def test_update_profile_not_found(client):
    """Test PUT /api/profile/{id} returns 404 for unknown profile ID."""
    update_payload = {"name": "Ghost", "email": "ghost@example.com"}
    resp = client.put("/api/profile/ghost-id-404", json=update_payload)
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_validation_error_format(client):
    """Test that invalid payload returns 422 formatted as {detail: message}."""
    # 'INVALID' is not a valid CategoryCode
    invalid_payload = {
        "name": "Invalid User",
        "skills": [{"skill_name": "Bad Skill", "category_code": "INVALID"}],
    }
    resp = client.post("/api/profile", json=invalid_payload)
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data
    assert isinstance(data["detail"], str)


def test_global_error_handler(client):
    """Test uncaught server exceptions return 500 formatted as {detail: message}."""
    resp = client.get("/test-error")
    assert resp.status_code == 500
    data = resp.json()
    assert "detail" in data
    assert data["detail"] == "Intentional test server error"


def test_cors_headers(client):
    """Test CORS headers for http://localhost:5173."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
    }
    resp = client.options("/api/profile", headers=headers)
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_teammate_routers_mounted(client):
    """Verify empty/placeholder routers for other modules are mounted."""
    modules = ["jd", "resume", "talent-check", "skill-matching"]
    for mod in modules:
        resp = client.get(f"/api/{mod}/status")
        assert resp.status_code == 200
        assert resp.json().get("status") == "initialized"
