"""
Integration tests for CLI workflows and end-to-end functionality
Tests complete user journeys and real API interactions
"""

import json
import tempfile
import time
from pathlib import Path

import pytest
import responses
from click.testing import CliRunner
from promptevolver_cli.config import CONVEX_BASE_URL
from promptevolver_cli.main import cli
from tests.fixtures.sample_prompts import BATCH_TEST_DATA, SAMPLE_PROMPTS


class TestCompleteWorkflows:
    """Test complete user workflows from start to finish"""

    @responses.activate
    def test_health_check_to_optimization_workflow(self, cli_runner):
        """Test complete workflow: health check then optimization"""
        # Setup API responses
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={
                "status": "success",
                "data": {"available": True, "model": "qwen3:4b", "version": "1.0.0"},
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
                    "result": {
                        "best_prompt": "You are an expert storyteller. Please write a compelling short story about a robot discovering emotions. Structure your story with a clear beginning, middle, and end, focusing on the robot's emotional journey and character development.",
                        "quality_score": 92.3,
                        "expert_profile": "Expert Creative Writer specializing in science fiction and character development",
                        "improvements": [
                            "Added expert identity for storytelling context",
                            "Specified story structure requirements",
                            "Enhanced focus on emotional journey and character development",
                            "Clarified genre and thematic elements",
                        ],
                    },
                },
            },
            status=200,
        )

        # Step 1: Health check
        health_result = cli_runner.invoke(cli, ["health"])
        assert health_result.exit_code == 0
        assert "Service Available" in health_result.output
        assert "qwen3:4b" in health_result.output

        # Step 2: Optimization
        opt_result = cli_runner.invoke(
            cli,
            [
                "optimize",
                "Write a short story about a robot",
                "--mode",
                "advanced",
                "--domain",
                "creative",
            ],
        )
        assert opt_result.exit_code == 0
        assert "Optimization Complete" in opt_result.output
        assert "expert storyteller" in opt_result.output.lower()
        assert "92.3" in opt_result.output

    @responses.activate
    def test_file_based_optimization_workflow(self, cli_runner):
        """Test workflow using file input and output"""
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Explain machine learning to a beginner\n")
            f.write("Create a marketing strategy for a tech startup\n")
            f.write("Debug a performance issue in a web application")
            input_file = Path(f.name)

        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "optimization_results.json"

            try:
                # Setup API response
                responses.add(
                    responses.POST,
                    f"{CONVEX_BASE_URL}/optimize",
                    json={
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "You are an expert educator specializing in making complex technical concepts accessible. Please explain machine learning to a complete beginner using simple language, practical examples, and analogies. Structure your explanation to build understanding progressively from basic concepts to practical applications.",
                                "quality_score": 89.7,
                                "expert_profile": "Expert Technical Educator",
                                "improvements": [
                                    "Added educator expertise context",
                                    "Specified teaching approach for beginners",
                                    "Included progressive learning structure",
                                    "Emphasized practical examples and analogies",
                                ],
                            },
                        },
                    },
                    status=200,
                )

                # Run optimization with file input
                result = cli_runner.invoke(
                    cli,
                    [
                        "optimize",
                        "--file",
                        str(input_file),
                        "--output",
                        str(output_file),
                        "--domain",
                        "technical",
                        "--mode",
                        "advanced",
                    ],
                )

                assert result.exit_code == 0
                assert "Optimization Complete" in result.output
                assert output_file.exists()

                # Verify output file content
                with open(output_file) as f:
                    data = json.load(f)
                    assert "original_prompt" in data
                    assert "optimized_prompt" in data
                    assert "quality_score" in data
                    assert data["quality_score"] == 89.7
                    assert data["domain"] == "technical"
                    assert data["mode"] == "advanced"

            finally:
                # Cleanup
                if input_file.exists():
                    input_file.unlink()

    @responses.activate
    def test_batch_processing_workflow(self, cli_runner):
        """Test complete batch processing workflow"""
        # Create batch input file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for prompt in BATCH_TEST_DATA["small_batch"]:
                f.write(f"{prompt}\n")
            batch_file = Path(f.name)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "batch_results.json"

            try:
                # Setup API responses for batch processing
                responses.add(
                    responses.POST,
                    f"{CONVEX_BASE_URL}/optimize",
                    json={
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "Batch processed prompt optimization",
                                "quality_score": 83.5,
                                "improvements": ["Batch improvement 1", "Batch improvement 2"],
                            },
                        },
                    },
                    status=200,
                )

                # Run batch processing
                result = cli_runner.invoke(
                    cli,
                    [
                        "batch",
                        str(batch_file),
                        "--output",
                        str(output_file),
                        "--format",
                        "json",
                        "--mode",
                        "quick",
                        "--domain",
                        "business",
                    ],
                )

                assert result.exit_code == 0
                assert "Batch Optimization Complete" in result.output
                assert output_file.exists()

                # Verify batch output
                with open(output_file) as f:
                    data = json.load(f)
                    assert "metadata" in data
                    assert "results" in data
                    assert data["metadata"]["total_results"] == len(BATCH_TEST_DATA["small_batch"])
                    assert len(data["results"]) > 0

                    # Check individual results
                    for result_item in data["results"]:
                        assert "original_prompt" in result_item
                        assert "success" in result_item
                        if result_item["success"]:
                            assert "optimized_prompt" in result_item
                            assert "quality_score" in result_item

            finally:
                if batch_file.exists():
                    batch_file.unlink()


class TestErrorRecoveryWorkflows:
    """Test error handling and recovery in complete workflows"""

    @responses.activate
    def test_health_check_failure_to_retry_workflow(self, cli_runner):
        """Test workflow when health check fails initially then succeeds"""
        # First health check fails
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={
                "status": "success",
                "data": {"available": False, "error": "Ollama service temporarily unavailable"},
            },
            status=200,
        )

        # Second health check succeeds
        responses.add(
            responses.GET,
            f"{CONVEX_BASE_URL}/health",
            json={"status": "success", "data": {"available": True, "model": "qwen3:4b"}},
            status=200,
        )

        # First health check shows failure
        result1 = cli_runner.invoke(cli, ["health"])
        assert result1.exit_code == 0
        assert "Service Unavailable" in result1.output
        assert "temporarily unavailable" in result1.output

        # Second health check shows recovery
        result2 = cli_runner.invoke(cli, ["health"])
        assert result2.exit_code == 0
        assert "Service Available" in result2.output

    @responses.activate
    def test_partial_batch_failure_workflow(self, cli_runner):
        """Test batch processing with partial failures"""
        # Create batch file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Prompt 1 - should succeed\n")
            f.write("Prompt 2 - will fail\n")
            f.write("Prompt 3 - should succeed\n")
            batch_file = Path(f.name)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "partial_failure_results.json"

            try:
                # Setup mixed responses
                success_response = {
                    "status": "success",
                    "data": {
                        "success": True,
                        "result": {
                            "best_prompt": "Successfully optimized prompt",
                            "quality_score": 85.0,
                        },
                    },
                }

                failure_response = {
                    "status": "success",
                    "data": {
                        "success": False,
                        "error": "Rate limit exceeded - please try again later",
                    },
                }

                responses.add(
                    responses.POST, f"{CONVEX_BASE_URL}/optimize", json=success_response, status=200
                )
                responses.add(
                    responses.POST, f"{CONVEX_BASE_URL}/optimize", json=failure_response, status=200
                )
                responses.add(
                    responses.POST, f"{CONVEX_BASE_URL}/optimize", json=success_response, status=200
                )

                # Run batch with continue-on-error
                result = cli_runner.invoke(
                    cli,
                    ["batch", str(batch_file), "--output", str(output_file), "--continue-on-error"],
                )

                assert result.exit_code == 0
                assert "Batch Optimization Complete" in result.output
                assert "Failed Prompts" in result.output
                assert output_file.exists()

                # Verify mixed results
                with open(output_file) as f:
                    data = json.load(f)
                    assert data["metadata"]["total_results"] == 3
                    assert data["metadata"]["successful"] == 2
                    assert data["metadata"]["failed"] == 1

                    # Check success and failure patterns
                    successful_count = sum(1 for r in data["results"] if r.get("success"))
                    failed_count = sum(1 for r in data["results"] if not r.get("success"))
                    assert successful_count == 2
                    assert failed_count == 1

            finally:
                if batch_file.exists():
                    batch_file.unlink()

    @responses.activate
    def test_network_error_recovery_workflow(self, cli_runner):
        """Test recovery from network errors"""
        # First request fails with network error
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            body=ConnectionError("Network connection failed"),
        )

        # Second request succeeds
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "Recovered and optimized successfully",
                        "quality_score": 87.2,
                    },
                },
            },
            status=200,
        )

        # First attempt should show network error
        result1 = cli_runner.invoke(cli, ["optimize", "Test prompt"])
        assert result1.exit_code == 0  # CLI doesn't exit with error code
        assert "Optimization failed" in result1.output
        assert "connection" in result1.output.lower() or "network" in result1.output.lower()

        # Second attempt should succeed
        result2 = cli_runner.invoke(cli, ["optimize", "Test prompt after recovery"])
        assert result2.exit_code == 0
        assert "Optimization Complete" in result2.output
        assert "87.2" in result2.output


class TestPerformanceWorkflows:
    """Test performance-related workflows and timing"""

    @responses.activate
    def test_quick_vs_advanced_mode_timing(self, cli_runner):
        """Test that advanced mode takes longer than quick mode"""

        # Setup responses with realistic delays
        def quick_response_callback(request):
            time.sleep(0.1)  # Simulate quick processing
            return (
                200,
                {},
                json.dumps(
                    {
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "Quick mode optimization",
                                "quality_score": 78.5,
                            },
                        },
                    }
                ),
            )

        def advanced_response_callback(request):
            time.sleep(0.3)  # Simulate longer processing
            return (
                200,
                {},
                json.dumps(
                    {
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "Advanced mode optimization with higher quality",
                                "quality_score": 89.2,
                            },
                        },
                    }
                ),
            )

        responses.add_callback(
            responses.POST, f"{CONVEX_BASE_URL}/optimize", callback=quick_response_callback
        )

        # Test quick mode
        start_time = time.time()
        quick_result = cli_runner.invoke(
            cli, ["optimize", "Test prompt for timing", "--mode", "quick"]
        )
        quick_duration = time.time() - start_time

        assert quick_result.exit_code == 0
        assert "quick mode" in quick_result.output

        # Reset responses for advanced mode
        responses.reset()
        responses.add_callback(
            responses.POST, f"{CONVEX_BASE_URL}/optimize", callback=advanced_response_callback
        )

        # Test advanced mode
        start_time = time.time()
        advanced_result = cli_runner.invoke(
            cli, ["optimize", "Test prompt for timing", "--mode", "advanced"]
        )
        advanced_duration = time.time() - start_time

        assert advanced_result.exit_code == 0
        assert "advanced mode" in advanced_result.output

        # Advanced mode should be slower (accounting for CLI overhead)
        assert advanced_duration > quick_duration

    @responses.activate
    def test_batch_processing_throughput(self, cli_runner):
        """Test batch processing throughput and rate limiting"""
        # Create medium-sized batch
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for prompt in BATCH_TEST_DATA["medium_batch"]:
                f.write(f"{prompt}\n")
            batch_file = Path(f.name)

        try:
            # Setup API response with small delay
            def batch_response_callback(request):
                time.sleep(0.05)  # Small delay per request
                return (
                    200,
                    {},
                    json.dumps(
                        {
                            "status": "success",
                            "data": {
                                "success": True,
                                "result": {
                                    "best_prompt": "Batch processed efficiently",
                                    "quality_score": 82.0,
                                },
                            },
                        }
                    ),
                )

            responses.add_callback(
                responses.POST, f"{CONVEX_BASE_URL}/optimize", callback=batch_response_callback
            )

            # Time batch processing
            start_time = time.time()
            result = cli_runner.invoke(cli, ["batch", str(batch_file), "--mode", "quick"])
            duration = time.time() - start_time

            assert result.exit_code == 0
            assert "Batch Optimization Complete" in result.output

            # Calculate throughput (should be reasonable)
            num_prompts = len(BATCH_TEST_DATA["medium_batch"])
            throughput = num_prompts / duration  # prompts per second

            # Should process at least 1 prompt per 5 seconds (accounting for delays)
            assert throughput > 0.2, f"Throughput too low: {throughput} prompts/second"

        finally:
            if batch_file.exists():
                batch_file.unlink()


class TestMultiFormatWorkflows:
    """Test workflows with different input/output formats"""

    @responses.activate
    def test_json_input_workflow(self, cli_runner):
        """Test workflow with JSON input file"""
        # Create JSON input file
        test_data = [
            {"prompt": "JSON test prompt 1", "metadata": {"priority": "high"}},
            {"text": "JSON test prompt 2", "category": "technical"},  # Different field name
            {"prompt": "JSON test prompt 3"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            json_file = Path(f.name)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "json_results.jsonl"

            try:
                # Setup API response
                responses.add(
                    responses.POST,
                    f"{CONVEX_BASE_URL}/optimize",
                    json={
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "JSON-processed optimization",
                                "quality_score": 86.3,
                            },
                        },
                    },
                    status=200,
                )

                # Process JSON batch
                result = cli_runner.invoke(
                    cli,
                    ["batch", str(json_file), "--output", str(output_file), "--format", "jsonl"],
                )

                assert result.exit_code == 0
                assert output_file.exists()

                # Verify JSONL output format
                with open(output_file) as f:
                    lines = f.readlines()
                    assert len(lines) == 3  # One line per input prompt

                    for line in lines:
                        data = json.loads(line)
                        assert "original_prompt" in data
                        assert "success" in data
                        if data["success"]:
                            assert "optimized_prompt" in data

            finally:
                if json_file.exists():
                    json_file.unlink()

    @responses.activate
    def test_csv_output_workflow(self, cli_runner):
        """Test workflow with CSV output format"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("CSV test prompt 1\n")
            f.write("CSV test prompt 2\n")
            input_file = Path(f.name)

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "csv_results.csv"

            try:
                # Setup API response
                responses.add(
                    responses.POST,
                    f"{CONVEX_BASE_URL}/optimize",
                    json={
                        "status": "success",
                        "data": {
                            "success": True,
                            "result": {
                                "best_prompt": "CSV-formatted optimization result",
                                "quality_score": 84.7,
                            },
                        },
                    },
                    status=200,
                )

                # Process with CSV output
                result = cli_runner.invoke(
                    cli, ["batch", str(input_file), "--output", str(output_file), "--format", "csv"]
                )

                assert result.exit_code == 0
                assert output_file.exists()

                # Verify CSV format
                import csv

                with open(output_file, "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                    assert len(rows) == 2
                    for row in rows:
                        assert "original_prompt" in row
                        assert "optimized_prompt" in row
                        assert "quality_score" in row
                        assert "success" in row

            finally:
                if input_file.exists():
                    input_file.unlink()


class TestDomainSpecializationWorkflows:
    """Test workflows with different domain specializations"""

    @responses.activate
    def test_technical_domain_workflow(self, cli_runner):
        """Test technical domain optimization workflow"""
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "You are a senior software engineer with expertise in Python performance optimization. Please analyze the provided code for potential performance bottlenecks and provide specific, actionable recommendations with code examples.",
                        "quality_score": 91.8,
                        "expert_profile": "Senior Software Engineer specializing in performance optimization",
                        "improvements": [
                            "Added specific technical expertise context",
                            "Specified analysis focus on performance bottlenecks",
                            "Requested actionable recommendations with examples",
                            "Enhanced technical precision and specificity",
                        ],
                    },
                },
            },
            status=200,
        )

        result = cli_runner.invoke(
            cli,
            [
                "optimize",
                "Help me optimize this Python code for better performance",
                "--domain",
                "technical",
                "--mode",
                "advanced",
            ],
        )

        assert result.exit_code == 0
        assert "technical domain" in result.output
        assert "software engineer" in result.output.lower()
        assert "performance" in result.output.lower()
        assert "91.8" in result.output

    @responses.activate
    def test_creative_domain_workflow(self, cli_runner):
        """Test creative domain optimization workflow"""
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "You are a master storyteller and creative writing expert. Craft an engaging, imaginative story that captivates readers from the first sentence. Use vivid imagery, dynamic characters, and unexpected plot twists to create a memorable narrative experience.",
                        "quality_score": 93.2,
                        "expert_profile": "Master Storyteller and Creative Writing Expert",
                        "improvements": [
                            "Added storytelling expertise and authority",
                            "Emphasized engagement and reader captivation",
                            "Specified creative elements: imagery, characters, plot twists",
                            "Enhanced focus on memorable narrative experience",
                        ],
                    },
                },
            },
            status=200,
        )

        result = cli_runner.invoke(
            cli,
            [
                "optimize",
                "Write an interesting story",
                "--domain",
                "creative",
                "--mode",
                "advanced",
            ],
        )

        assert result.exit_code == 0
        assert "creative domain" in result.output
        assert "storyteller" in result.output.lower()
        assert "93.2" in result.output


class TestInteractiveWorkflows:
    """Test interactive features and user guidance"""

    @responses.activate
    def test_comparison_display_workflow(self, cli_runner):
        """Test side-by-side comparison workflow"""
        responses.add(
            responses.POST,
            f"{CONVEX_BASE_URL}/optimize",
            json={
                "status": "success",
                "data": {
                    "success": True,
                    "result": {
                        "best_prompt": "You are a helpful AI assistant specializing in clear, concise explanations. Please provide a comprehensive overview of the topic, breaking down complex concepts into easily understandable components with practical examples.",
                        "quality_score": 88.9,
                        "expert_profile": "AI Assistant Expert in Clear Communication",
                    },
                },
            },
            status=200,
        )

        result = cli_runner.invoke(
            cli, ["optimize", "Explain this topic clearly", "--show-comparison"]
        )

        assert result.exit_code == 0
        assert "Original" in result.output
        assert "Optimized" in result.output
        # Should show both original and optimized prompts
        assert "Explain this topic clearly" in result.output
        assert "comprehensive overview" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
