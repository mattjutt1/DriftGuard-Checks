"""
Integration tests for API communication and external dependencies
Tests real API interactions, error scenarios, and resilience
"""

import json
import time

import pytest
import responses
from promptevolver_cli.client import ConvexClient, ConvexError
from promptevolver_cli.config import API_TIMEOUT, CONVEX_BASE_URL


class TestConvexAPIIntegration:
    """Test integration with Convex API endpoints"""

    @responses.activate
    def test_health_endpoint_integration(self):
        """Test health endpoint with realistic responses"""
        client = ConvexClient()

        # Test healthy response
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={
                "status": "success",
                "data": {
                    "available": True,
                    "model": "qwen3:4b",
                    "version": "1.0.0",
                    "uptime": 3600,
                    "last_request": time.time() - 30,
                    "memory_usage": "2.1GB",
                    "gpu_utilization": "45%",
                },
            },
            status=200,
        )

        result = client.check_health()

        assert result["available"] is True
        assert result["model"] == "qwen3:4b"
        assert "uptime" in result
        assert "memory_usage" in result

    @responses.activate
    def test_optimization_endpoint_integration(self):
        """Test optimization endpoint with realistic data"""
        client = ConvexClient()

        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "You are a senior data scientist with expertise in machine learning and statistical analysis. Please provide a comprehensive explanation of the machine learning concept, including theoretical foundations, practical applications, and real - world examples. Structure your response to build understanding progressively from basic principles to advanced implementations.",
                        "quality_score": 94.2,
                        "processing_time": 3.7,
                        "expert_profile": "Senior Data Scientist specializing in ML education and statistical analysis",
                        "improvements": [
                            "Added senior - level expertise context",
                            "Specified comprehensive explanation requirements",
                            "Included theoretical and practical components",
                            "Added progressive learning structure",
                            "Enhanced with real - world application focus",
                        ],
                        "metadata": {
                            "iterations_performed": 3,
                            "mutation_rounds": 3,
                            "reasoning_generated": True,
                            "expert_identity_added": True,
                            "original_length": 47,
                            "optimized_length": 198,
                            "improvement_ratio": 4.21,
                        },
                    },
                },
            },
            status=200,
        )

        config = {
            "domain": "technical",
            "mutate_refine_iterations": 3,
            "mutation_rounds": 3,
            "generate_reasoning": True,
            "generate_expert_identity": True,
            "temperature": 0.7,
        }

        result = client.optimize_prompt("Explain machine learning", config)

        assert result["success"] is True
        assert result["result"]["quality_score"] == 94.2
        assert len(result["result"]["improvements"]) == 5
        assert "metadata" in result["result"]
        assert result["result"]["metadata"]["iterations_performed"] == 3

    @responses.activate
    def test_api_error_scenarios(self):
        """Test various API error scenarios"""
        client = ConvexClient()

        # Test rate limiting
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "error",
                "error": "Rate limit exceeded. Too many requests in short period.",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 60,
                "current_usage": "150 requests / hour",
                "limit": "100 requests / hour",
            },
            status=429,
        )

        with pytest.raises(ConvexError) as exc_info:
            client.optimize_prompt("Test prompt", {})

        # HTTP error status codes trigger requests.RequestException, resulting in generic error format
        assert "API request failed" in str(exc_info.value) and "429" in str(exc_info.value)

        # Test server error
        responses.reset()
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "error",
                "error": "Internal server error - Ollama service unavailable",
                "error_code": "SERVICE_UNAVAILABLE",
                "suggested_action": "Please try again in a few minutes",
            },
            status=500,
        )

        with pytest.raises(ConvexError) as exc_info:
            client.optimize_prompt("Test prompt", {})

        # HTTP error status codes trigger requests.RequestException, resulting in generic error format
        assert "API request failed" in str(exc_info.value) and "500" in str(exc_info.value)

    @responses.activate
    def test_malformed_responses(self):
        """Test handling of malformed API responses"""
        client = ConvexClient()

        # Test invalid JSON
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            body="This is not valid JSON",
            status=200,
            content_type="application / json",
        )

        with pytest.raises(ConvexError):
            client.check_health()

        # Test missing required fields
        responses.reset()
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "data": {
                    "result": {
                        "best_prompt": "Test result"
                        # Missing success field
                    }
                }
                # Missing status field
            },
            status=200,
        )

        result = client.optimize_prompt("Test", {})
        # Should handle gracefully with fallback response format
        # Response has no "status" field, so client returns the raw response
        # The actual response structure is {"data": {"result": {...}}}
        assert "data" in result
        assert "result" in result["data"]


class TestNetworkResilience:
    """Test network - related resilience and error handling"""

    def test_connection_timeout(self):
        """Test connection timeout handling"""
        client = ConvexClient("https://nonexistent - convex - server.invalid")

        with pytest.raises(ConvexError) as exc_info:
            client.check_health()

        assert "API request failed" in str(exc_info.value)

    @responses.activate
    def test_slow_response_handling(self):
        """Test handling of slow API responses"""
        client = ConvexClient()

        def slow_response_callback(request):
            time.sleep(0.1)  # Small delay to simulate slow response
            return (
                200,
                {},
                json.dumps(
                    {
                        "status": "success",
                        "data": {
                            "available": True,
                            "model": "qwen3:4b",
                            "response_time": "slow_but_within_timeout",
                        },
                    }
                ),
            )

        responses.add_callback(responses.GET, f"{CONVEX_BASE_URL}/health", callback=slow_response_callback)

        start_time = time.time()
        result = client.check_health()
        duration = time.time() - start_time

        assert result["available"] is True
        assert duration > 0.1  # Should take at least the delay time
        assert duration < API_TIMEOUT  # But less than timeout

    @responses.activate
    def test_partial_response_handling(self):
        """Test handling of partial or incomplete responses"""
        client = ConvexClient()

        # Test response with minimal required fields
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Minimal response"
                        # Missing quality_score, improvements, etc.
                    },
                },
            },
            status=200,
        )

        result = client.optimize_prompt("Test prompt", {})

        assert result["success"] is True
        assert result["result"]["best_prompt"] == "Minimal response"
        # Should handle missing optional fields gracefully

    @responses.activate
    def test_http_status_code_handling(self):
        """Test handling of various HTTP status codes"""
        client = ConvexClient()

        # Test 404 Not Found
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/nonexistent",
            json={"error": "Endpoint not found"},
            status=404,
        )

        with pytest.raises(ConvexError):
            client.call_http_endpoint("/nonexistent", "GET")

        # Test 503 Service Unavailable
        responses.reset()
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={"error": "Service temporarily unavailable", "retry_after": 30},
            status=503,
        )

        with pytest.raises(ConvexError):
            client.optimize_prompt("Test", {})


class TestConfigurationIntegration:
    """Test integration with different configurations"""

    @responses.activate
    def test_domain_specific_optimization(self):
        """Test optimization with domain - specific configurations"""
        client = ConvexClient()

        # Test technical domain
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Technical optimization result",
                        "quality_score": 89.5,
                        "domain_applied": "technical",
                        "style_variation": 2,  # Lower for technical
                        "reasoning_depth": "high",
                    },
                },
            },
            status=200,
        )

        technical_config = {
            "domain": "technical",
            "style_variation": 2,
            "generate_reasoning": True,
            "temperature": 0.7,
        }

        result = client.optimize_prompt("Debug this code issue", technical_config)

        assert result["success"] is True
        assert result["result"]["domain_applied"] == "technical"

        # Verify request configuration
        request_body = json.loads(responses.calls[0].request.body)
        assert request_body["domain"] == "technical"
        assert request_body["config"]["style_variation"] == 2

    @responses.activate
    def test_mode_specific_optimization(self):
        """Test optimization with different mode configurations"""
        client = ConvexClient()

        # Test quick mode response
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Quick mode optimization",
                        "quality_score": 78.3,
                        "iterations_performed": 1,
                        "processing_time": 2.1,
                    },
                },
            },
            status=200,
        )

        quick_config = {"mutate_refine_iterations": 1, "mutation_rounds": 1, "domain": "general"}

        result = client.optimize_prompt("Test quick optimization", quick_config)

        assert result["success"] is True
        assert result["result"]["iterations_performed"] == 1
        assert result["result"]["processing_time"] < 5  # Should be faster

        # Test advanced mode
        responses.reset()
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Advanced mode optimization with higher quality",
                        "quality_score": 91.7,
                        "iterations_performed": 3,
                        "processing_time": 8.4,
                    },
                },
            },
            status=200,
        )

        advanced_config = {"mutate_refine_iterations": 3, "mutation_rounds": 3, "domain": "general"}

        result = client.optimize_prompt("Test advanced optimization", advanced_config)

        assert result["success"] is True
        assert result["result"]["iterations_performed"] == 3
        assert result["result"]["quality_score"] > 90  # Should be higher quality


class TestLargeDataHandling:
    """Test handling of large prompts and responses"""

    @responses.activate
    def test_large_prompt_optimization(self):
        """Test optimization of very large prompts"""
        client = ConvexClient()

        # Create a large prompt (2000+ characters)
        large_prompt = (
            """
        This is a very large prompt that contains multiple paragraphs and extensive detail about a complex topic.
        It includes various requirements, constraints, and specifications that need to be carefully considered during optimization.
        The prompt covers multiple aspects including technical requirements, user experience considerations, performance criteria,
        security guidelines, accessibility standards, and maintenance procedures. It also includes examples, edge cases,
        error handling scenarios, and integration requirements with external systems. The optimization process should maintain
        all critical information while improving clarity, structure, and effectiveness. Additional context includes business
        objectives, stakeholder requirements, timeline constraints, budget considerations, and quality assurance criteria.
        """
            * 5
        )  # Repeat to make it even larger

        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Optimized large prompt with improved structure and clarity while maintaining all essential information and requirements.",
                        "quality_score": 87.9,
                        "original_length": len(large_prompt),
                        "optimized_length": 127,
                        "compression_ratio": 0.85,
                        "information_retention": 0.96,
                    },
                },
            },
            status=200,
        )

        result = client.optimize_prompt(large_prompt, {"domain": "general"})

        assert result["success"] is True
        assert result["result"]["original_length"] == len(large_prompt)
        assert result["result"]["compression_ratio"] > 0  # Should compress while retaining info

    @responses.activate
    def test_large_response_handling(self):
        """Test handling of large API responses"""
        client = ConvexClient()

        # Create a response with many improvements and detailed metadata
        large_improvements = [
            f"Improvement {i}: Detailed explanation of enhancement number {i} with specific examples and rationale"
            for i in range(1, 21)  # 20 detailed improvements
        ]

        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Large response optimization result",
                        "quality_score": 93.4,
                        "expert_profile": "Comprehensive expert profile with detailed background, specializations, and experience across multiple domains",
                        "improvements": large_improvements,
                        "metadata": {
                            "detailed_analysis": {
                                "linguistic_patterns": ["pattern1", "pattern2", "pattern3"],
                                "semantic_structure": "complex nested structure",
                                "optimization_path": [f"step_{i}" for i in range(1, 16)],
                                "quality_metrics": {
                                    "clarity": 92.1,
                                    "specificity": 89.7,
                                    "completeness": 94.3,
                                    "engagement": 88.9,
                                },
                            }
                        },
                    },
                },
            },
            status=200,
        )

        result = client.optimize_prompt("Test large response", {})

        assert result["success"] is True
        assert len(result["result"]["improvements"]) == 20
        assert "metadata" in result["result"]
        assert "detailed_analysis" in result["result"]["metadata"]


class TestConcurrentRequestHandling:
    """Test handling of concurrent requests and load"""

    @responses.activate
    def test_multiple_concurrent_requests(self):
        """Test multiple API requests in sequence"""
        client = ConvexClient()

        # Setup multiple responses
        for i in range(5):
            responses.add(
                responses.POST,
                f"{CONVEX_BASE_URL}/optimize",
                json={
                    "status": "success",
                    "data": {
                        "success": True,
                        "result": {
                            "best_prompt": f"Concurrent optimization result {i + 1}",
                            "quality_score": 80.0 + i,
                            "request_id": f"req_{i + 1}",
                        },
                    },
                },
                status=200,
            )

        # Make multiple requests
        results = []
        for i in range(5):
            result = client.optimize_prompt(f"Test prompt {i + 1}", {"domain": "general"})
            results.append(result)

        # Verify all requests succeeded
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["result"]["request_id"] == f"req_{i + 1}"

    @responses.activate
    def test_request_ordering_and_state(self):
        """Test that requests maintain proper ordering and state"""
        client = ConvexClient()

        # Different response for each request
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={"status": "success", "data": {"available": True, "check_id": "health_1"}},
            status=200,
        )

        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {"best_prompt": "First optimization", "request_order": 1},
                },
            },
            status=200,
        )

        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {"best_prompt": "Second optimization", "request_order": 2},
                },
            },
            status=200,
        )

        # Execute requests in order
        health_result = client.check_health()
        opt_result_1 = client.optimize_prompt("First prompt", {})
        opt_result_2 = client.optimize_prompt("Second prompt", {})

        # Verify proper ordering
        assert health_result["check_id"] == "health_1"
        assert opt_result_1["result"]["request_order"] == 1
        assert opt_result_2["result"]["request_order"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
