"""
Configuration settings for PromptEvolver CLI
"""

import os
from typing import Optional

# Convex deployment URL - can be overridden with environment variable
CONVEX_BASE_URL = os.getenv("CONVEX_URL", "https://enchanted-rooster-257.convex.site")

# Default optimization settings
DEFAULT_CONFIG = {
    "generate_reasoning": True,
    "generate_expert_identity": True,
    "mutation_rounds": 3,
    "seen_set_size": 25,
    "few_shot_count": 3,
    "temperature": 0.7,
    "max_tokens": 1024,
}

# Quick mode settings (1 iteration)
QUICK_MODE_CONFIG = {**DEFAULT_CONFIG, "mutate_refine_iterations": 1}

# Advanced mode settings (3 iterations)
ADVANCED_MODE_CONFIG = {**DEFAULT_CONFIG, "mutate_refine_iterations": 3}

# API timeout settings
API_TIMEOUT = 30  # seconds
BATCH_DELAY = 1  # seconds between batch requests

# Domain-specific configurations
DOMAIN_CONFIGS = {
    "general": {
        "task_description": "You are a helpful assistant that provides clear, accurate, and engaging responses.",
        "base_instruction": "Think step by step and provide a comprehensive response.",
    },
    "technical": {
        "task_description": "You are a technical expert providing precise, detailed, and accurate technical information.",
        "base_instruction": "Provide technical details with clear explanations and examples where appropriate.",
        "style_variation": 2,  # More focused, less creative variation
    },
    "creative": {
        "task_description": "You are a creative assistant that generates engaging, imaginative, and inspiring content.",
        "base_instruction": "Be creative, engaging, and think outside the box while maintaining relevance.",
        "style_variation": 5,  # More creative variation
        "temperature": 0.8,  # Higher temperature for creativity
    },
    "business": {
        "task_description": "You are a business professional providing strategic, practical, and actionable insights.",
        "base_instruction": "Focus on practical business value, clear communication, and actionable recommendations.",
        "few_shot_count": 2,  # Fewer examples for conciseness
    },
    "academic": {
        "task_description": "You are an academic expert providing scholarly, well-researched, and comprehensive analysis.",
        "base_instruction": "Provide thorough analysis with proper reasoning, evidence, and academic rigor.",
        "mutation_rounds": 4,  # More thorough optimization
        "seen_set_size": 30,  # Larger context for academic work
    },
}
