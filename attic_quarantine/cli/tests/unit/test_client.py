"""
Unit tests for client.py HTTP client functionality
Tests API communication, error handling, and response processing
"""

import json
from unittest.mock import Mock, patch

import pytest
import requests
import responses
from promptevolver_cli.client import ConvexClient, ConvexError
from promptevolver_cli.config import API_TIMEOUT, CONVEX_BASE_URL


class TestConvexClient:
    """Test ConvexClient HTTP communication"""

    def test_client_initialization(self):
        """Test client initialization with default and custom URLs"""
        # Test default URL
        client = ConvexClient()
        assert client.base_url == CONVEX_BASE_URL.rstrip("/")

        # Test custom URL
        custom_url = "https://custom-convex.example.com/"
        client = ConvexClient(custom_url)
        assert client.base_url == "https://custom-convex.example.com"

    @responses.activate
    def test_call_http_endpoint_get_success(self):
        """Test successful GET request"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/test",
            json={"status": "success", "data": {"result": "test"}},
            status=200,
        )

        result = client.call_http_endpoint("/test", "GET")
        assert result == {"result": "test"}
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://test.convex.cloud/test"

    @responses.activate
    def test_call_http_endpoint_post_success(self):
        """Test successful POST request"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/test",
            json={"status": "success", "data": {"result": "posted"}},
            status=200,
        )

        test_data = {"prompt": "test prompt"}
        result = client.call_http_endpoint("/test", "POST", test_data)

        assert result == {"result": "posted"}
        assert len(responses.calls) == 1

        # Verify request data
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == test_data

    @responses.activate
    def test_call_http_endpoint_error_response(self):
        """Test API error response handling"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/error",
            json={"status": "error", "error": "Invalid request"},
            status=400,
        )

        with pytest.raises(ConvexError) as exc_info:
            client.call_http_endpoint("/error", "POST", {"data": "test"})

        assert "Invalid request" in str(exc_info.value)

    @responses.activate
    def test_call_http_endpoint_http_error(self):
        """Test HTTP error handling"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/error",
            json={"error": "Server error"},
            status=500,
        )

        with pytest.raises(ConvexError) as exc_info:
            client.call_http_endpoint("/error", "GET")

        assert "API request failed" in str(exc_info.value)

    @responses.activate
    def test_call_http_endpoint_connection_error(self):
        """Test connection error handling"""
        client = ConvexClient("https://nonexistent.convex.cloud")

        with pytest.raises(ConvexError) as exc_info:
            client.call_http_endpoint("/test", "GET")

        assert "API request failed" in str(exc_info.value)

    @responses.activate
    def test_call_http_endpoint_timeout(self):
        """Test timeout handling"""
        client = ConvexClient("https://test.convex.cloud")

        def request_callback(request):
            import time

            time.sleep(API_TIMEOUT + 1)  # Sleep longer than timeout
            return (200, {}, json.dumps({"status": "success"}))

        responses.add_callback(responses.GET, "https://test.convex.cloud/slow", callback=request_callback)

        with pytest.raises(ConvexError) as exc_info:
            client.call_http_endpoint("/slow", "GET")

        assert "API request failed" in str(exc_info.value)

    @responses.activate
    def test_call_http_endpoint_fallback_response(self):
        """Test fallback response handling for non-standard format"""
        client = ConvexClient("https://test.convex.cloud")

        # Response without status field
        responses.add(
            responses.GET,
            "https://test.convex.cloud/fallback",
            json={"result": "direct_result", "message": "success"},
            status=200,
        )

        result = client.call_http_endpoint("/fallback", "GET")
        assert result == {"result": "direct_result", "message": "success"}


class TestHealthCheck:
    """Test health check functionality"""

    @responses.activate
    def test_check_health_success(self):
        """Test successful health check"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/health",
            json={
                "status": "success",
                "data": {"available": True, "model": "qwen3:4b", "uptime": 86400},
            },
            status=200,
        )

        result = client.check_health()

        assert result["available"] is True
        assert result["model"] == "qwen3:4b"
        assert result["uptime"] == 86400

    @responses.activate
    def test_check_health_failure(self):
        """Test health check failure"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/health",
            json={
                "status": "success",
                "data": {"available": False, "error": "Ollama service down"},
            },
            status=200,
        )

        result = client.check_health()

        assert result["available"] is False
        assert result["error"] == "Ollama service down"

    @responses.activate
    def test_check_health_connection_error(self):
        """Test health check with connection error"""
        client = ConvexClient("https://unreachable.convex.cloud")

        with pytest.raises(ConvexError):
            client.check_health()


class TestOptimizePrompt:
    """Test prompt optimization functionality"""

    @responses.activate
    def test_optimize_prompt_success(self):
        """Test successful prompt optimization"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Optimized prompt text",
                        "quality_score": 88.5,
                        "expert_profile": "AI Expert",
                        "improvements": ["Better clarity", "Added structure"],
                    },
                },
            },
            status=200,
        )

        config = {"domain": "technical", "mutate_refine_iterations": 3, "generate_reasoning": True}

        result = client.optimize_prompt("Original prompt", config)

        assert result["success"] is True
        assert result["result"]["best_prompt"] == "Optimized prompt text"
        assert result["result"]["quality_score"] == 88.5
        assert len(result["result"]["improvements"]) == 2

        # Verify request data
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["prompt"] == "Original prompt"
        assert request_body["domain"] == "technical"
        assert request_body["config"] == config

    @responses.activate
    def test_optimize_prompt_failure(self):
        """Test prompt optimization failure"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={"status": "success", "data": {"success": False, "error": "Rate limit exceeded"}},
            status=200,
        )

        config = {"domain": "general"}
        result = client.optimize_prompt("Test prompt", config)

        assert result["success"] is False
        assert result["error"] == "Rate limit exceeded"

    @responses.activate
    def test_optimize_prompt_api_error(self):
        """Test prompt optimization with API error"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={"status": "error", "error": "Invalid prompt format"},
            status=400,
        )

        with pytest.raises(ConvexError) as exc_info:
            client.optimize_prompt("", {})

        assert "Invalid prompt format" in str(exc_info.value)

    @responses.activate
    def test_optimize_prompt_minimal_config(self):
        """Test optimization with minimal configuration"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {"best_prompt": "Minimal optimization", "quality_score": 75.0},
                },
            },
            status=200,
        )

        result = client.optimize_prompt("Simple prompt", {})

        assert result["success"] is True
        assert result["result"]["quality_score"] == 75.0

        # Verify minimal request structure
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["prompt"] == "Simple prompt"
        assert request_body["domain"] == "general"  # Default value
        assert request_body["config"] == {}


class TestSessionMethods:
    """Test session-based methods (currently disabled)"""

    def test_quick_optimize_not_implemented(self):
        """Test that quick_optimize raises appropriate error"""
        client = ConvexClient()

        with pytest.raises(ConvexError) as exc_info:
            client.quick_optimize("session_123")

        assert "requires authenticated session" in str(exc_info.value)

    def test_advanced_optimize_not_implemented(self):
        """Test that advanced_optimize raises appropriate error"""
        client = ConvexClient()

        with pytest.raises(ConvexError) as exc_info:
            client.advanced_optimize("session_123")

        assert "requires authenticated session" in str(exc_info.value)


class TestRequestHeaders:
    """Test HTTP request headers and formatting"""

    @responses.activate
    def test_correct_headers_sent(self):
        """Test that correct headers are sent with requests"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/test",
            json={"status": "success", "data": {}},
            status=200,
        )

        client.call_http_endpoint("/test", "POST", {"data": "test"})

        request = responses.calls[0].request
        assert request.headers["Content-Type"] == "application/json"

    @responses.activate
    def test_json_encoding(self):
        """Test JSON encoding of request data"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.POST,
            "https://test.convex.cloud/test",
            json={"status": "success", "data": {}},
            status=200,
        )

        test_data = {
            "string": "test",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }

        client.call_http_endpoint("/test", "POST", test_data)

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body == test_data


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_convex_error_exception(self):
        """Test ConvexError exception properties"""
        error_msg = "Test error message"
        error = ConvexError(error_msg)

        assert str(error) == error_msg
        assert isinstance(error, Exception)

    @responses.activate
    def test_malformed_json_response(self):
        """Test handling of malformed JSON response"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/malformed",
            body="This is not JSON",
            status=200,
            content_type="application/json",
        )

        with pytest.raises(ConvexError):
            client.call_http_endpoint("/malformed", "GET")

    @responses.activate
    def test_empty_response(self):
        """Test handling of empty response"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/empty",
            body="",
            status=200,
            content_type="application/json",
        )

        with pytest.raises(ConvexError):
            client.call_http_endpoint("/empty", "GET")

    @responses.activate
    def test_missing_status_field(self):
        """Test response without status field"""
        client = ConvexClient("https://test.convex.cloud")

        responses.add(
            responses.GET,
            "https://test.convex.cloud/no-status",
            json={"message": "No status field"},
            status=200,
        )

        result = client.call_http_endpoint("/no-status", "GET")
        assert result == {"message": "No status field"}


class TestPerformanceAndReliability:
    """Test performance and reliability aspects"""

    @responses.activate
    def test_large_request_handling(self):
        """Test handling of large request payloads"""
        client = ConvexClient("https://test.convex.cloud")

        # Create large prompt (5000 characters)
        large_prompt = "A" * 5000
        large_config = {"domain": "general", "large_data": ["item" + str(i) for i in range(100)]}

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={
                "status": "success",
                "data": {"success": True, "result": {"best_prompt": "Handled large request"}},
            },
            status=200,
        )

        result = client.optimize_prompt(large_prompt, large_config)
        assert result["success"] is True

    @responses.activate
    def test_unicode_handling(self):
        """Test Unicode character handling"""
        client = ConvexClient("https://test.convex.cloud")

        unicode_data = {
            "prompt": "Test with Unicode: 你好 🌍 Здравствуй",
            "config": {"domain": "international"},
        }

        responses.add(
            responses.POST,
            "https://test.convex.cloud/optimize",
            json={
                "status": "success",
                "data": {"success": True, "result": {"best_prompt": unicode_data["prompt"]}},
            },
            status=200,
        )

        result = client.optimize_prompt(unicode_data["prompt"], unicode_data["config"])
        assert result["success"] is True

    @patch("promptevolver_cli.client.requests.post")
    @patch("promptevolver_cli.client.requests.get")
    def test_timeout_configuration(self, mock_get, mock_post):
        """Test that timeout is properly configured"""
        client = ConvexClient("https://test.convex.cloud")

        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success", "data": {}}
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        # Test GET request
        client.call_http_endpoint("/test", "GET")
        mock_get.assert_called_once()
        assert mock_get.call_args[1]["timeout"] == API_TIMEOUT

        # Test POST request
        client.call_http_endpoint("/test", "POST", {})
        mock_post.assert_called_once()
        assert mock_post.call_args[1]["timeout"] == API_TIMEOUT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
