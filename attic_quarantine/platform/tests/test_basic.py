"""Basic tests for DriftGuard API."""

import os

# Set offline mode before importing anything
os.environ["PROMPTOPS_MODE"] = "stub"
os.environ["DISABLE_NETWORK"] = "1"

from fastapi.testclient import TestClient
from driftguard.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DriftGuard"


def test_drift_check_stub():
    """Test drift check submission (stub endpoint)."""
    check_data = {
        "prompt_id": "test_prompt",
        "version": "1.0.0",
        "drift_score": 0.15,
        "timestamp": "2024-01-01T00:00:00",
        "details": {"method": "cosine_similarity"},
    }

    response = client.post("/api/v1/drift/check", json=check_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"
    assert "alert_triggered" in data


def test_set_budget_stub():
    """Test budget setting (stub endpoint)."""
    budget_data = {
        "prompt_id": "test_prompt",
        "max_cost_per_1k": 0.02,
        "max_latency_ms": 500,
        "alert_threshold": 0.8,
    }

    response = client.post("/api/v1/budgets", json=budget_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "budget_set"


def test_get_budget_not_found():
    """Test getting non-existent budget returns 404."""
    response = client.get("/api/v1/budgets/nonexistent")
    assert response.status_code == 404
