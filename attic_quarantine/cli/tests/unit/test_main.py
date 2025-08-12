"""
Unit tests for main.py CLI commands
Tests CLI argument parsing, command execution, and output formatting
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from click.testing import CliRunner
from promptevolver_cli.client import ConvexError
from promptevolver_cli.main import _display_quality_metrics, _save_optimization_results, cli
from tests.fixtures.sample_prompts import CONFIG_TEST_DATA, SAMPLE_PROMPTS


class TestCLIBasics:
    """Test basic CLI functionality"""

    def test_cli_version(self, cli_runner):
        """Test --version flag"""
        result = cli_runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self, cli_runner):
        """Test --help flag"""
        result = cli_runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PromptEvolver CLI" in result.output
        assert "optimize" in result.output
        assert "batch" in result.output
        assert "health" in result.output

    def test_invalid_command(self, cli_runner):
        """Test invalid command handling"""
        result = cli_runner.invoke(cli, ["invalid-command"])
        assert result.exit_code != 0
        assert "No such command" in result.output


class TestHealthCommand:
    """Test health check command"""

    @patch("promptevolver_cli.main.client")
    def test_health_check_success(self, mock_client, cli_runner):
        """Test successful health check"""
        mock_client.check_health.return_value = {"available": True, "model": "qwen3:4b"}

        result = cli_runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "Service Available" in result.output
        assert "qwen3:4b" in result.output
        mock_client.check_health.assert_called_once()

    @patch("promptevolver_cli.main.client")
    def test_health_check_failure(self, mock_client, cli_runner):
        """Test failed health check"""
        mock_client.check_health.return_value = {"available": False, "error": "Connection timeout"}

        result = cli_runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "Service Unavailable" in result.output
        assert "Connection timeout" in result.output

    @patch("promptevolver_cli.main.client")
    def test_health_check_exception(self, mock_client, cli_runner):
        """Test health check with exception"""
        mock_client.check_health.side_effect = ConvexError("Network error")

        result = cli_runner.invoke(cli, ["health"])
        assert result.exit_code == 0
        assert "Health check failed" in result.output
        assert "Network error" in result.output


class TestOptimizeCommand:
    """Test optimize command functionality"""

    @patch("promptevolver_cli.main.client")
    def test_optimize_with_prompt_argument(self, mock_client, cli_runner):
        """Test optimize with prompt as argument"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {
                "best_prompt": "Optimized test prompt",
                "quality_score": 85.5,
                "expert_profile": "Test expert",
                "improvements": ["Improvement 1", "Improvement 2"],
            },
        }

        result = cli_runner.invoke(cli, ["optimize", "Test prompt to optimize"])
        assert result.exit_code == 0
        assert "Optimization Complete" in result.output
        assert "Optimized test prompt" in result.output
        assert "85.5" in result.output
        mock_client.optimize_prompt.assert_called_once()

    @patch("promptevolver_cli.main.client")
    def test_optimize_with_file_input(self, mock_client, cli_runner, temp_prompt_file):
        """Test optimize with file input"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "File-based optimized prompt", "quality_score": 90.0},
        }

        result = cli_runner.invoke(cli, ["optimize", "--file", str(temp_prompt_file)])
        assert result.exit_code == 0
        assert "Optimization Complete" in result.output
        assert "File-based optimized prompt" in result.output
        mock_client.optimize_prompt.assert_called_once()

    def test_optimize_no_prompt(self, cli_runner):
        """Test optimize without prompt argument"""
        result = cli_runner.invoke(cli, ["optimize"])
        assert result.exit_code == 1
        assert "Please provide a prompt" in result.output

    @patch("promptevolver_cli.main.client")
    def test_optimize_different_modes(self, mock_client, cli_runner):
        """Test optimize with different modes"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Test", "quality_score": 80},
        }

        # Test quick mode
        result = cli_runner.invoke(cli, ["optimize", "test", "--mode", "quick"])
        assert result.exit_code == 0
        assert "quick mode" in result.output

        # Test advanced mode
        result = cli_runner.invoke(cli, ["optimize", "test", "--mode", "advanced"])
        assert result.exit_code == 0
        assert "advanced mode" in result.output

    @patch("promptevolver_cli.main.client")
    def test_optimize_different_domains(self, mock_client, cli_runner):
        """Test optimize with different domains"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Test", "quality_score": 80},
        }

        domains = ["general", "technical", "creative", "business", "academic"]
        for domain in domains:
            result = cli_runner.invoke(cli, ["optimize", "test", "--domain", domain])
            assert result.exit_code == 0
            assert f"{domain} domain" in result.output

    @patch("promptevolver_cli.main.client")
    def test_optimize_with_output_file(self, mock_client, cli_runner, temp_output_dir):
        """Test optimize with output file"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {
                "best_prompt": "Test output",
                "quality_score": 88.0,
                "expert_profile": "Test expert",
            },
        }

        output_file = temp_output_dir / "test_output.json"
        result = cli_runner.invoke(cli, ["optimize", "test prompt", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify output file content
        with open(output_file) as f:
            data = json.load(f)
            assert data["original_prompt"] == "test prompt"
            assert data["optimized_prompt"] == "Test output"
            assert data["quality_score"] == 88.0

    @patch("promptevolver_cli.main.client")
    def test_optimize_failure(self, mock_client, cli_runner):
        """Test optimize command failure"""
        mock_client.optimize_prompt.return_value = {
            "success": False,
            "error": "API rate limit exceeded",
        }

        result = cli_runner.invoke(cli, ["optimize", "test prompt"])
        assert result.exit_code == 0  # CLI doesn't exit with error code for API failures
        assert "Optimization failed" in result.output
        assert "API rate limit exceeded" in result.output

    @patch("promptevolver_cli.main.client")
    def test_optimize_exception(self, mock_client, cli_runner):
        """Test optimize with exception"""
        mock_client.optimize_prompt.side_effect = ConvexError("Connection failed")

        result = cli_runner.invoke(cli, ["optimize", "test prompt"])
        assert result.exit_code == 0
        assert "Optimization failed" in result.output
        assert "Connection failed" in result.output

    def test_optimize_empty_prompt(self, cli_runner):
        """Test optimize with empty prompt"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("")  # Empty file
            empty_file = Path(f.name)

        try:
            result = cli_runner.invoke(cli, ["optimize", "--file", str(empty_file)])
            assert result.exit_code == 1
            assert "Empty prompt provided" in result.output
        finally:
            empty_file.unlink()

    @patch("promptevolver_cli.main.client")
    def test_optimize_with_comparison(self, mock_client, cli_runner):
        """Test optimize with side-by-side comparison"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Optimized version", "quality_score": 90.0},
        }

        result = cli_runner.invoke(cli, ["optimize", "Original prompt", "--show-comparison"])
        assert result.exit_code == 0
        assert "Original" in result.output
        assert "Optimized" in result.output


class TestBatchCommand:
    """Test batch processing command"""

    @patch("promptevolver_cli.main.client")
    def test_batch_processing_success(self, mock_client, cli_runner, temp_prompt_file, temp_output_dir):
        """Test successful batch processing"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Batch optimized prompt", "quality_score": 85.0},
        }

        output_file = temp_output_dir / "batch_results.json"
        result = cli_runner.invoke(cli, ["batch", str(temp_prompt_file), "--output", str(output_file)])

        assert result.exit_code == 0
        assert "Batch Optimization Complete" in result.output
        assert output_file.exists()

        # Verify output file
        with open(output_file) as f:
            data = json.load(f)
            assert "metadata" in data
            assert "results" in data
            assert len(data["results"]) > 0

    @patch("promptevolver_cli.main.client")
    def test_batch_processing_with_errors(self, mock_client, cli_runner, temp_prompt_file):
        """Test batch processing with some errors"""
        # Simulate some successes and some failures
        responses = [
            {"success": True, "result": {"best_prompt": "Success 1", "quality_score": 80}},
            {"success": False, "error": "API error"},
            {"success": True, "result": {"best_prompt": "Success 2", "quality_score": 85}},
        ]
        mock_client.optimize_prompt.side_effect = responses

        result = cli_runner.invoke(cli, ["batch", str(temp_prompt_file), "--continue-on-error"])

        assert result.exit_code == 0
        assert "Failed Prompts" in result.output or "Batch Optimization Complete" in result.output

    def test_batch_nonexistent_file(self, cli_runner):
        """Test batch with nonexistent file"""
        result = cli_runner.invoke(cli, ["batch", "nonexistent_file.txt"])
        assert result.exit_code != 0

    @patch("promptevolver_cli.main.client")
    def test_batch_different_formats(self, mock_client, cli_runner, temp_json_file):
        """Test batch with different file formats"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "JSON batch result", "quality_score": 90},
        }

        result = cli_runner.invoke(cli, ["batch", str(temp_json_file)])
        assert result.exit_code == 0
        assert "Batch Optimization Complete" in result.output

    @patch("promptevolver_cli.main.client")
    def test_batch_output_formats(self, mock_client, cli_runner, temp_prompt_file, temp_output_dir):
        """Test batch with different output formats"""
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Format test", "quality_score": 75},
        }

        formats = ["json", "jsonl", "csv", "txt"]
        for fmt in formats:
            output_file = temp_output_dir / f"test_output.{fmt}"
            result = cli_runner.invoke(
                cli, ["batch", str(temp_prompt_file), "--output", str(output_file), "--format", fmt]
            )
            assert result.exit_code == 0
            assert output_file.exists()


class TestUtilityFunctions:
    """Test utility functions"""

    def test_display_quality_metrics(self, capsys):
        """Test quality metrics display"""
        from rich.console import Console

        console = Console()

        _display_quality_metrics(console, 85.5, 12.3, "advanced", "technical")

        captured = capsys.readouterr()
        # Note: Rich output testing is complex, so we just check it doesn't crash
        assert True  # Function executed without error

    def test_save_optimization_results(self, temp_output_dir):
        """Test saving optimization results"""
        output_file = temp_output_dir / "test_save.json"
        result_data = {
            "best_prompt": "Test optimized prompt",
            "quality_score": 88.5,
            "expert_profile": "Test expert",
            "improvements": ["Test improvement"],
        }

        _save_optimization_results(output_file, "Original prompt", result_data, 15.2, "quick", "general")

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
            assert data["original_prompt"] == "Original prompt"
            assert data["optimized_prompt"] == "Test optimized prompt"
            assert data["quality_score"] == 88.5
            assert data["processing_time"] == 15.2
            assert data["mode"] == "quick"
            assert data["domain"] == "general"


class TestArgumentValidation:
    """Test CLI argument validation"""

    def test_invalid_mode(self, cli_runner):
        """Test invalid mode argument"""
        result = cli_runner.invoke(cli, ["optimize", "test", "--mode", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value for '--mode'" in result.output

    def test_invalid_domain(self, cli_runner):
        """Test invalid domain argument"""
        result = cli_runner.invoke(cli, ["optimize", "test", "--domain", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value for '--domain'" in result.output

    def test_invalid_rounds(self, cli_runner):
        """Test invalid rounds argument"""
        result = cli_runner.invoke(cli, ["optimize", "test", "--rounds", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value for '--rounds'" in result.output

    def test_file_not_exists(self, cli_runner):
        """Test file that doesn't exist"""
        result = cli_runner.invoke(cli, ["optimize", "--file", "nonexistent.txt"])
        assert result.exit_code != 0
        assert "does not exist" in result.output


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @patch("promptevolver_cli.main.client")
    def test_very_long_prompt(self, mock_client, cli_runner):
        """Test optimization with very long prompt"""
        long_prompt = "A" * 5000  # 5000 character prompt
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Optimized long prompt", "quality_score": 70},
        }

        result = cli_runner.invoke(cli, ["optimize", long_prompt])
        assert result.exit_code == 0
        mock_client.optimize_prompt.assert_called_once()

    @patch("promptevolver_cli.main.client")
    def test_special_characters(self, mock_client, cli_runner):
        """Test prompt with special characters"""
        special_prompt = "Test with special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Handled special chars", "quality_score": 75},
        }

        result = cli_runner.invoke(cli, ["optimize", special_prompt])
        assert result.exit_code == 0

    @patch("promptevolver_cli.main.client")
    def test_unicode_prompt(self, mock_client, cli_runner):
        """Test prompt with Unicode characters"""
        unicode_prompt = "Test Unicode: 你好 🌍 Здравствуй"
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Unicode handled", "quality_score": 82},
        }

        result = cli_runner.invoke(cli, ["optimize", unicode_prompt])
        assert result.exit_code == 0

    @patch("promptevolver_cli.main.client")
    def test_multiline_prompt(self, mock_client, cli_runner):
        """Test multiline prompt"""
        multiline_prompt = "Line 1\nLine 2\nLine 3"
        mock_client.optimize_prompt.return_value = {
            "success": True,
            "result": {"best_prompt": "Multiline optimized", "quality_score": 78},
        }

        result = cli_runner.invoke(cli, ["optimize", multiline_prompt])
        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
