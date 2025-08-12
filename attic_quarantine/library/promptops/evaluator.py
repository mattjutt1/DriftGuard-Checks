"""Core evaluation logic for PromptOps."""

import os
import random
from typing import Dict, Any, List
from datetime import datetime

from .config import Config

# Check offline mode
PROMPTOPS_MODE = os.getenv("PROMPTOPS_MODE", "production")
DISABLE_NETWORK = os.getenv("DISABLE_NETWORK", "0").lower() in ("1", "true", "yes")
ALLOW_NETWORK = os.getenv("ALLOW_NETWORK", "0").lower() in ("1", "true", "yes")

if PROMPTOPS_MODE != "stub" and DISABLE_NETWORK and not ALLOW_NETWORK:
    raise RuntimeError("PROMPTOPS_MODE is not 'stub' but network is disabled. Set ALLOW_NETWORK=1 to override.")


class Evaluator:
    """Main evaluator class."""

    def __init__(self, config: Config):
        """Initialize evaluator with config."""
        self.config = config

    def evaluate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Evaluate a single prompt (mocked for now)."""
        # Mock evaluation - in production, this would call real models
        score = random.uniform(0.7, 1.0)

        return {
            "original": prompt,
            "score": score,
            "improved": f"[Optimized] {prompt}",
            "metrics": {
                "clarity": random.uniform(0.7, 1.0),
                "specificity": random.uniform(0.7, 1.0),
                "completeness": random.uniform(0.7, 1.0),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def run_ci_evaluation(self) -> Dict[str, Any]:
        """Run CI evaluation against configured prompts."""
        results = []

        # Use test prompts from config or defaults
        test_prompts = self.config.test_prompts or [
            "Write a Python function",
            "Explain machine learning",
            "Create a REST API",
        ]

        for prompt in test_prompts:
            result = self.evaluate_prompt(prompt)
            results.append(result)

        # Calculate aggregate metrics
        avg_score = sum(r["score"] for r in results) / len(results) if results else 0
        win_rate = sum(1 for r in results if r["score"] > 0.8) / len(results) if results else 0

        # Determine pass/fail
        passed = win_rate >= self.config.threshold

        return {
            "pass": passed,
            "threshold": self.config.threshold,
            "metrics": {
                "win_rate": win_rate,
                "avg_score": avg_score,
                "total_prompts": len(results),
            },
            "details": results,
            "timestamp": datetime.utcnow().isoformat(),
            "config_version": self.config.version,
        }

    def batch_evaluate(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Evaluate multiple prompts in batch."""
        return [self.evaluate_prompt(p) for p in prompts]
