from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_workflow():
    response = client.post(
        "/workflows",
        json={
            "name": "Test Workflow",
            "steps": [
                {
                    "id": "step-1",
                    "system": "abap_cloud",
                    "action": "execute_rap",
                    "payload": {"bo": "ZR_Travel"},
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert data["workflow_id"].startswith("wf-")
    assert len(data["steps"]) == 1


def test_get_workflow():
    create_resp = client.post(
        "/workflows",
        json={
            "name": "Retrieve Test",
            "steps": [],
        },
    )
    wf_id = create_resp.json()["workflow_id"]
    get_resp = client.get(f"/workflows/{wf_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["workflow_id"] == wf_id


def test_get_missing_workflow():
    response = client.get("/workflows/nonexistent")
    assert response.status_code == 404