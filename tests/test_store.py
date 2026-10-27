import json
import pytest
import db.store as store


@pytest.fixture(autouse=True)
def setup_test_dirs(tmp_path, monkeypatch):
    test_profiles = tmp_path / "profiles"
    test_runs = tmp_path / "runs"
    test_jds = tmp_path / "jds"
    for d in (test_profiles, test_runs, test_jds):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(store, "_supabase_client", None)
    monkeypatch.setattr(store, "PROFILES_DIR", test_profiles)
    monkeypatch.setattr(store, "RUNS_DIR", test_runs)
    monkeypatch.setattr(store, "JDS_DIR", test_jds)

    yield {
        "profiles": test_profiles,
        "runs": test_runs,
        "jds": test_jds,
    }


def test_profile_store_fallback(setup_test_dirs):
    # Save profile
    p = {"name": "Test User", "email": "test@test.com"}
    saved = store.save_profile(p)
    assert "profile_id" in saved
    pid = saved["profile_id"]

    # Load profile
    loaded = store.load_profile(pid)
    assert loaded is not None
    assert loaded["name"] == "Test User"

    # List profiles
    profs = store.list_profiles()
    assert len(profs) == 1
    assert profs[0]["profile_id"] == pid

    # Load non-existent
    assert store.load_profile("unknown") is None


def test_jd_store_fallback(setup_test_dirs):
    jd_payload = {"company": "Acme Corp", "role": "Backend Engineer"}
    saved = store.save_jd(jd_payload, jd_id="jd-123")
    assert saved["jd_id"] == "jd-123"

    loaded = store.load_jd("jd-123")
    assert loaded is not None
    assert loaded["company"] == "Acme Corp"
    assert store.load_jd("non-existent") is None


def test_run_store_fallback(setup_test_dirs):
    run_payload = {"status": "completed", "score": 88.5}
    saved = store.save_run(run_payload, run_id="run-456")
    assert saved["run_id"] == "run-456"

    run_file = setup_test_dirs["runs"] / "run-456.json"
    assert run_file.exists()


def test_audit_store_fallback(setup_test_dirs):
    entry = store.write_audit(
        action="user_login",
        details={"ip": "127.0.0.1"},
        entity_id="user-1",
        entity_type="user",
    )
    assert entry["action"] == "user_login"
    assert "audit_id" in entry
    assert "timestamp" in entry

    # Verify audit_log.json exists and has entry
    log_file = setup_test_dirs["runs"] / "audit_log.json"
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["action"] == "user_login"
