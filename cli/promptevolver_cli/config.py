"""
Configuration settings for PromptEvolver CLI
"""

import os
from typing import Optional

# Convex deployment URL - can be overridden with environment variable
CONVEX_BASE_URL = os.getenv("CONVEX_URL", "https://resilient-guanaco-29.convex.cloud")

# Default optimization settings
DEFAULT_CONFIG = {
    "generate_reasoning": True,
    "generate_expert_identity": True,
    "mutation_rounds": 3,
    "seen_set_size": 25,
    "few_shot_count": 3,
    "temperature": 0.7,
    "max_tokens": 1024
}

# Quick mode settings (1 iteration)
QUICK_MODE_CONFIG = {
    **DEFAULT_CONFIG,
    "mutate_refine_iterations": 1
}

# Advanced mode settings (3 iterations)
ADVANCED_MODE_CONFIG = {
    **DEFAULT_CONFIG,
    "mutate_refine_iterations": 3
}

# API timeout settings
API_TIMEOUT = 30  # seconds
BATCH_DELAY = 1   # seconds between batch requests