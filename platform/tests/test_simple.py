"""Simple tests for DriftGuard API without async complexity."""

import os
from fastapi.testclient import TestClient

# Set offline mode before importing the app
os.environ["PROMPTOPS_MODE"] = "stub"
os.environ["DISABLE_NETWORK"] = "1"

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


def test_register_duplicate_prompt_fails():
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
