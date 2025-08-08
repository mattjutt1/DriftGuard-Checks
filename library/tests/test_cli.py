"""Tests for PromptOps CLI."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from promptops.cli import main


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_init():
    """Test config initialization."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init"])
        assert result.exit_code == 0
        assert Path(".promptops.yml").exists()

        # Check config content
        with open(".promptops.yml") as f:
            config = yaml.safe_load(f)
        assert config["threshold"] == 0.85


def test_cli_ci_pass():
    """Test CI command with passing evaluation."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create config
        config = {
            "version": "1.0",
            "threshold": 0.0,  # Set low threshold to ensure pass
            "test_prompts": ["Test prompt"],
        }
        with open(".promptops.yml", "w") as f:
            yaml.dump(config, f)

        # Run CI
        result = runner.invoke(main, ["ci", "--out", "results.json"])
        assert result.exit_code == 0
        assert "PASSED" in result.output
        assert Path("results.json").exists()

        # Check results
        with open("results.json") as f:
            results = json.load(f)
        assert results["pass"] is True


def test_cli_eval():
    """Test single prompt evaluation."""
    runner = CliRunner()
    result = runner.invoke(main, ["eval", "Test prompt"])
    assert result.exit_code == 0
    assert "Score:" in result.output
    assert "Improved:" in result.output
