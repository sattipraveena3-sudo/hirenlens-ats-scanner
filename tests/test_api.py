from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

RESUME = """Summary\nPython data engineer.\nSkills\nPython SQL Docker AWS\nExperience\n- Improved ETL throughput by 40%.\nProjects\nFastAPI service.\nEducation\nB.Tech"""
JOB = "We need a Python SQL data engineer with Docker, AWS, FastAPI and Kubernetes for ETL pipelines."


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_without_ai():
    response = client.post("/api/v1/analyze", json={"resume": RESUME, "job_description": JOB, "use_ai": False})
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "deterministic"
    assert body["match_score"] >= 0
    assert "python" in body["matched_skills"]


def test_validation_rejects_tiny_input():
    response = client.post("/api/v1/analyze", json={"resume": "tiny", "job_description": "too short", "use_ai": False})
    assert response.status_code == 422
