"""
Shared test fixtures and configuration for PromptEvolver CLI tests
"""

import json
import pytest
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch
from click.testing import CliRunner
import responses

from promptevolver_cli.main import cli
from promptevolver_cli.client import ConvexClient
from promptevolver_cli.config import CONVEX_BASE_URL, DEFAULT_CONFIG


@pytest.fixture
def cli_runner():
    """CLI runner for testing Click commands"""
    return CliRunner()


@pytest.fixture
def mock_convex_client():
    """Mock Convex client for testing without real API calls"""
    client = Mock(spec=ConvexClient)
    
    # Setup default successful responses
    client.check_health.return_value = {
        "available": True,
        "model": "qwen3:4b",
        "status": "healthy"
    }
    
    client.optimize_prompt.return_value = {
        "success": True,
        "result": {
            "best_prompt": "Optimized test prompt with improved clarity and structure",
            "quality_score": 85.5,
            "expert_profile": "Expert AI assistant specialized in prompt optimization",
            "improvements": [
                "Enhanced clarity and specificity",
                "Added structured approach",
                "Improved task guidance"
            ]
        }
    }
    
    return client


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing"""
    return [
        "Write a short story about a robot",
        "Explain quantum computing to a beginner",
        "Create a marketing plan for a new app",
        "Debug this Python code issue",
        "Write a professional email"
    ]


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        **DEFAULT_CONFIG,
        "domain": "general",
        "mode": "quick"
    }


@pytest.fixture
def temp_prompt_file():
    """Temporary file with test prompts"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test prompt line 1\n")
        f.write("Test prompt line 2\n")
        f.write("Test prompt line 3\n")
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_json_file():
    """Temporary JSON file with test prompts"""
    test_data = [
        {"prompt": "JSON test prompt 1"},
        {"prompt": "JSON test prompt 2"},
        {"text": "JSON test prompt 3"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_output_dir():
    """Temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_api_responses():
    """Mock HTTP responses for API testing"""
    with responses.RequestsMock() as rsps:
        # Health check endpoint
        rsps.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={
                "status": "success",
                "data": {
                    "available": True,
                    "model": "qwen3:4b",
                    "version": "1.0.0"
                }
            },
            status=200
        )
        
        # Optimize endpoint
        rsps.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success", 
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Optimized prompt response",
                        "quality_score": 88.0,
                        "expert_profile": "Test expert profile",
                        "improvements": ["Test improvement 1", "Test improvement 2"]
                    }
                }
            },
            status=200
        )
        
        # Error response for testing
        rsps.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/error-test",
            json={
                "status": "error",
                "error": "Test error message"
            },
            status=400
        )
        
        yield rsps


@pytest.fixture
def performance_metrics():
    """Performance metrics tracker for tests"""
    metrics = {
        "start_time": None,
        "end_time": None,
        "duration": None,
        "memory_usage": None,
        "api_calls": 0
    }
    
    def start_timing():
        metrics["start_time"] = time.time()
    
    def end_timing():
        metrics["end_time"] = time.time()
        if metrics["start_time"]:
            metrics["duration"] = metrics["end_time"] - metrics["start_time"]
    
    def increment_api_calls():
        metrics["api_calls"] += 1
    
    metrics["start_timing"] = start_timing
    metrics["end_timing"] = end_timing
    metrics["increment_api_calls"] = increment_api_calls
    
    return metrics


@pytest.fixture
def test_evidence_collector():
    """Collector for generating test evidence and reports"""
    evidence = {
        "test_results": [],
        "coverage_data": {},
        "performance_metrics": {},
        "quality_metrics": {},
        "errors": []
    }
    
    def add_result(test_name: str, result: Dict[str, Any]):
        evidence["test_results"].append({
            "test": test_name,
            "timestamp": time.time(),
            "result": result
        })
    
    def add_error(test_name: str, error: str):
        evidence["errors"].append({
            "test": test_name,
            "timestamp": time.time(),
            "error": error
        })
    
    def generate_summary() -> Dict[str, Any]:
        total_tests = len(evidence["test_results"])
        passed_tests = len([r for r in evidence["test_results"] if r["result"].get("passed", False)])
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_errors": len(evidence["errors"]),
            "timestamp": time.time()
        }
    
    evidence["add_result"] = add_result
    evidence["add_error"] = add_error
    evidence["generate_summary"] = generate_summary
    
    return evidence


# Test data fixtures
@pytest.fixture
def optimization_response_success():
    """Successful optimization response"""
    return {
        "success": True,
        "result": {
            "best_prompt": "You are an expert AI assistant. Please provide a comprehensive, well-structured response to the following request. Think step by step and ensure your answer is clear, accurate, and helpful.",
            "quality_score": 92.5,
            "expert_profile": "Expert AI Assistant specializing in clear, structured communication",
            "improvements": [
                "Added expert identity for better context",
                "Included step-by-step thinking instruction",
                "Enhanced clarity and structure requirements",
                "Improved specificity and guidance"
            ],
            "metadata": {
                "processing_time": 2.3,
                "iterations": 3,
                "domain": "general"
            }
        }
    }


@pytest.fixture  
def optimization_response_error():
    """Error optimization response"""
    return {
        "success": False,
        "error": "API rate limit exceeded. Please try again in 60 seconds.",
        "error_code": "RATE_LIMIT_EXCEEDED",
        "retry_after": 60
    }


@pytest.fixture
def health_response_healthy():
    """Healthy system response"""
    return {
        "available": True,
        "model": "qwen3:4b",
        "status": "healthy",
        "version": "1.0.0",
        "uptime": 86400,
        "last_check": time.time()
    }


@pytest.fixture
def health_response_unhealthy():
    """Unhealthy system response"""
    return {
        "available": False,
        "status": "unhealthy",
        "error": "Ollama service not responding",
        "last_error": "Connection timeout after 30 seconds",
        "last_check": time.time()
    }


# Utility fixtures
@pytest.fixture
def capture_cli_output():
    """Capture CLI output for testing"""
    outputs = []
    
    def capture(result):
        outputs.append({
            "exit_code": result.exit_code,
            "output": result.output,
            "exception": result.exception,
            "timestamp": time.time()
        })
        return outputs[-1]
    
    return capture


@pytest.fixture(autouse=True)
def test_environment_setup(monkeypatch):
    """Setup test environment variables"""
    # Set test-specific environment variables
    monkeypatch.setenv("CONVEX_URL", "https://test-convex-deployment.convex.cloud")
    monkeypatch.setenv("TEST_MODE", "true")
    
    # Ensure we don't accidentally use production endpoints
    monkeypatch.setenv("PYTEST_RUNNING", "true")


# Performance testing fixtures
@pytest.fixture
def performance_benchmarks():
    """Performance benchmarks for testing"""
    return {
        "cli_startup_time": 2.0,  # seconds
        "health_check_time": 5.0,  # seconds
        "optimization_time": 30.0,  # seconds
        "batch_processing_rate": 10.0,  # prompts per minute
        "memory_usage_limit": 100.0,  # MB
    }


@pytest.fixture
def quality_thresholds():
    """Quality thresholds for testing"""
    return {
        "min_code_coverage": 80.0,  # percentage
        "max_complexity": 10,  # cyclomatic complexity
        "max_line_length": 100,  # characters
        "min_test_success_rate": 95.0,  # percentage
        "max_error_rate": 5.0,  # percentage
    }