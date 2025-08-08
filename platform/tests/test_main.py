"""Tests for DriftGuard API."""

import os
import pytest
from fastapi.testclient import TestClient

# Set offline mode before importing the app
os.environ["PROMPTOPS_MODE"] = "stub"
os.environ["DISABLE_NETWORK"] = "1"

from driftguard.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_root_endpoint(override_db_dependency):
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "DriftGuard"


@pytest.mark.asyncio
async def test_register_prompt(override_db_dependency):
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


@pytest.mark.asyncio
async def test_register_duplicate_prompt(override_db_dependency):
    """Test registering duplicate prompt version returns 409."""
    prompt_data = {
        "name": "duplicate_test",
        "version": "1.0.0",
        "template": "Test template",
        "metadata": {},
    }

    # First registration should succeed
    response1 = client.post("/api/v1/prompts", json=prompt_data)
    assert response1.status_code == 201

    # Second registration should fail with 409
    response2 = client.post("/api/v1/prompts", json=prompt_data)
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_list_prompts(override_db_dependency):
    """Test listing prompts."""
    # Register a prompt first
    prompt_data = {
        "name": "list_test",
        "version": "1.0.0",
        "template": "Test template",
        "metadata": {},
    }
    client.post("/api/v1/prompts", json=prompt_data)

    # List prompts
    response = client.get("/api/v1/prompts")
    assert response.status_code == 200
    data = response.json()
    assert "prompts" in data
    assert len(data["prompts"]) > 0


@pytest.mark.asyncio
async def test_get_prompt_not_found(override_db_dependency):
    """Test getting non-existent prompt returns 404."""
    response = client.get("/api/v1/prompts/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_drift_check(override_db_dependency):
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


@pytest.mark.asyncio
async def test_set_budget(override_db_dependency):
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


@pytest.mark.asyncio
async def test_get_metrics(override_db_dependency):
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_prompts" in data
    assert "total_organizations" in data
