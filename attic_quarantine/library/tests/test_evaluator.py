"""Tests for PromptOps evaluator."""

import pytest
from promptops import Evaluator, Config


def test_evaluate_prompt():
    """Test single prompt evaluation."""
    config = Config()
    evaluator = Evaluator(config)

    result = evaluator.evaluate_prompt("Test prompt")

    assert "original" in result
    assert "score" in result
    assert "improved" in result
    assert 0.0 <= result["score"] <= 1.0


def test_run_ci_evaluation():
    """Test CI evaluation run."""
    config = Config(
        threshold=0.85,
        test_prompts=["Test 1", "Test 2", "Test 3"],
    )
    evaluator = Evaluator(config)

    results = evaluator.run_ci_evaluation()

    assert "pass" in results
    assert "metrics" in results
    assert "win_rate" in results["metrics"]
    assert results["threshold"] == 0.85


def test_batch_evaluate():
    """Test batch evaluation."""
    config = Config()
    evaluator = Evaluator(config)

    prompts = ["Prompt 1", "Prompt 2", "Prompt 3"]
    results = evaluator.batch_evaluate(prompts)

    assert len(results) == 3
    for result in results:
        assert "score" in result
        assert 0.0 <= result["score"] <= 1.0
