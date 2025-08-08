"""PromptOps SDK - Lightweight prompt evaluation and CI/CD."""

__version__ = "0.1.0"

from .evaluator import Evaluator
from .config import Config

__all__ = ["Evaluator", "Config"]
