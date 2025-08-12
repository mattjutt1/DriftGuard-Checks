"""Configuration management for PromptOps."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class EvaluationConfig(BaseModel):
    """Evaluation configuration."""
    metrics: List[str] = Field(
        default=["clarity", "specificity", "completeness"],
        description="Metrics to evaluate",
    )
    timeout: int = Field(default=30, description="Timeout in seconds")
    batch_size: int = Field(default=10, description="Batch size for evaluation")


class Config(BaseModel):
    """Main configuration for PromptOps."""
    version: str = Field(default="1.0", description="Config version")
    threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Pass threshold")
    model: str = Field(default="mock", description="Model to use")
    test_prompts: List[str] = Field(default_factory=list, description="Test prompts")
    evaluation: EvaluationConfig = Field(
        default_factory=EvaluationConfig,
        description="Evaluation settings",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load config from YAML file."""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
