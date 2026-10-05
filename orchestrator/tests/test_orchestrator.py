"""Tests — 2026 best practice: async-first, coverage gated."""

import pytest
from fastapi.testclient import TestClient
from orchestrator.main import app, HealthResponse
from orchestrator.config import AppConfig
from orchestrator.validators import (
    validate_workflow_name,
    validate_step_id,
    validate_payload,
    ValidationError,
)
from orchestrator.engine.circuit_breaker import CircuitBreaker, CircuitState
from orchestrator.models.workflow import WorkflowStep, SystemType


client = TestClient(app)


class TestHealth:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert "checks" in data


class TestWorkflowCRUD:
    def test_create_workflow(self):
        resp = client.post(
            "/workflows",
            json={
                "name": "Test WF",
                "steps": [
                    {
                        "id": "s1",
                        "system": "abap_cloud",
                        "action": "execute_rap",
                        "payload": {"bo": "ZR_Travel"},
                    }
                ],
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test WF"
        assert data["workflow_id"].startswith("wf-")
        assert len(data["steps"]) == 1

    def test_create_workflow_no_steps(self):
        resp = client.post(
            "/workflows",
            json={"name": "Bad", "steps": []},
        )
        assert resp.status_code == 422

    def test_get_workflow(self):
        create = client.post(
            "/workflows",
            json={
                "name": "Retrieve",
                "steps": [{"id": "s1", "system": "hana", "action": "query", "payload": {}}],
            },
        )
        wf_id = create.json()["workflow_id"]
        get = client.get(f"/workflows/{wf_id}")
        assert get.status_code == 200
        assert get.json()["workflow_id"] == wf_id

    def test_get_missing(self):
        resp = client.get("/workflows/nonexistent")
        assert resp.status_code == 404


class TestValidators:
    def test_valid_name(self):
        validate_workflow_name("my-workflow")

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            validate_workflow_name("")

    def test_valid_step_id(self):
        validate_step_id("step-1")

    def test_invalid_step_id_raises(self):
        with pytest.raises(ValidationError):
            validate_step_id("step/invalid")

    def test_valid_payload(self):
        validate_payload({"key": "val"})

    def test_large_payload_raises(self):
        with pytest.raises(ValidationError):
            validate_payload({"big": "x" * 200_000})


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED

    def test_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_half_open_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        import time as _t
        _t.sleep(0.05)
        assert cb.state == CircuitState.HALF_OPEN

    def test_resets_on_success(self):
        cb = CircuitBreaker()
        cb.record_failure()
        cb.record_success()
        assert cb.state == CircuitState.CLOSED


class TestConfig:
    def test_defaults(self):
        cfg = AppConfig()
        assert cfg.max_retries == 3
        assert cfg.port == 8000
        assert cfg.circuit_failure_threshold == 5
