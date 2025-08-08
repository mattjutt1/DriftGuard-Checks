"""Tests for DriftGuard API."""

import pytest
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


def test_register_prompt():
    """Test prompt registration."""
    prompt_data = {
        "name": "test_prompt",
        "version": "1.0.0",
        "template": "Generate a {type} for {topic}",
        "metadata": {"author": "test"},
    }

    response = client.post("/api/v1/prompts", json=prompt_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "registered"


def test_list_prompts():
    """Test listing prompts."""
    # Register a prompt first
    prompt_data = {
        "name": "list_test",
        "version": "1.0.0",
        "template": "Test template",
    }
    client.post("/api/v1/prompts", json=prompt_data)

    # List prompts
    response = client.get("/api/v1/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) > 0


def test_drift_check():
    """Test drift check submission."""
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


def test_set_budget():
    """Test budget setting."""
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


def test_get_metrics():
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_prompts" in data
    assert "total_drift_checks" in data
    assert "active_budgets" in data
