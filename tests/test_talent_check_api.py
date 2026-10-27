from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _profile():
    return {
        "name": "Test Candidate",
        "email": "candidate@example.invalid",
        "skills": [],
    }


def test_companies_endpoint_returns_company_options():
    response = client.get("/api/talent-check/companies")

    assert response.status_code == 200
    companies = response.json()
    assert companies
    assert all(company["id"] == company["name"] for company in companies)


def test_talent_check_returns_frontend_result_shape():
    companies = client.get("/api/talent-check/companies").json()

    response = client.post(
        "/api/talent-check",
        json={"company": companies[0]["name"], "profile": _profile()},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["company"] == companies[0]["name"]
    assert 0 <= result["readiness_score"] <= 100
    assert isinstance(result["skillset_gap"], list)
    assert {"category_code", "required_level", "candidate_level", "gap"} <= set(
        result["skillset_gap"][0]
    )


def test_whatif_changes_readiness_without_saving_profile():
    company = client.get("/api/talent-check/companies").json()[0]["name"]
    profile = _profile()
    initial = client.post(
        "/api/talent-check",
        json={"company": company, "profile": profile},
    ).json()
    required_skill = next(
        gap for gap in initial["skillset_gap"] if gap["required_level"] > 0
    )

    response = client.post(
        "/api/talent-check/whatif",
        json={
            "company": company,
            "profile": profile,
            "changes": [
                {
                    "category_code": required_skill["category_code"],
                    "new_level": required_skill["required_level"],
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["readiness_score"] > initial["readiness_score"]
    assert profile["skills"] == []


def test_talent_check_rejects_unknown_company():
    response = client.post(
        "/api/talent-check",
        json={"company": "Unknown Company", "profile": _profile()},
    )

    assert response.status_code == 404
