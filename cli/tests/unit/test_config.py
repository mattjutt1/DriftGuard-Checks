"""
Unit tests for config.py configuration settings
Tests configuration values, domain-specific settings, and environment handling
"""

import os
from unittest.mock import patch

import pytest
from promptevolver_cli.config import (
    ADVANCED_MODE_CONFIG,
    API_TIMEOUT,
    BATCH_DELAY,
    CONVEX_BASE_URL,
    DEFAULT_CONFIG,
    DOMAIN_CONFIGS,
    QUICK_MODE_CONFIG,
)


class TestDefaultConfiguration:
    """Test default configuration values"""

    def test_default_config_structure(self):
        """Test that DEFAULT_CONFIG has all required fields"""
        required_fields = [
            "generate_reasoning",
            "generate_expert_identity",
            "mutation_rounds",
            "seen_set_size",
            "few_shot_count",
            "temperature",
            "max_tokens",
        ]

        for field in required_fields:
            assert field in DEFAULT_CONFIG, f"Missing required field: {field}"

    def test_default_config_values(self):
        """Test default configuration values are reasonable"""
        assert DEFAULT_CONFIG["generate_reasoning"] is True
        assert DEFAULT_CONFIG["generate_expert_identity"] is True
        assert isinstance(DEFAULT_CONFIG["mutation_rounds"], int)
        assert DEFAULT_CONFIG["mutation_rounds"] > 0
        assert isinstance(DEFAULT_CONFIG["seen_set_size"], int)
        assert DEFAULT_CONFIG["seen_set_size"] > 0
        assert isinstance(DEFAULT_CONFIG["few_shot_count"], int)
        assert DEFAULT_CONFIG["few_shot_count"] > 0
        assert isinstance(DEFAULT_CONFIG["temperature"], (int, float))
        assert 0.0 <= DEFAULT_CONFIG["temperature"] <= 2.0
        assert isinstance(DEFAULT_CONFIG["max_tokens"], int)
        assert DEFAULT_CONFIG["max_tokens"] > 0

    def test_config_immutability(self):
        """Test that modifying configs doesn't affect original"""
        original_rounds = DEFAULT_CONFIG["mutation_rounds"]
        test_config = DEFAULT_CONFIG.copy()
        test_config["mutation_rounds"] = 999

        assert DEFAULT_CONFIG["mutation_rounds"] == original_rounds
        assert test_config["mutation_rounds"] == 999


class TestModeConfigurations:
    """Test quick and advanced mode configurations"""

    def test_quick_mode_config(self):
        """Test quick mode configuration"""
        assert "mutate_refine_iterations" in QUICK_MODE_CONFIG
        assert QUICK_MODE_CONFIG["mutate_refine_iterations"] == 1

        # Should inherit from DEFAULT_CONFIG
        assert QUICK_MODE_CONFIG["generate_reasoning"] == DEFAULT_CONFIG["generate_reasoning"]
        assert QUICK_MODE_CONFIG["temperature"] == DEFAULT_CONFIG["temperature"]

    def test_advanced_mode_config(self):
        """Test advanced mode configuration"""
        assert "mutate_refine_iterations" in ADVANCED_MODE_CONFIG
        assert ADVANCED_MODE_CONFIG["mutate_refine_iterations"] == 3

        # Should inherit from DEFAULT_CONFIG
        assert ADVANCED_MODE_CONFIG["generate_reasoning"] == DEFAULT_CONFIG["generate_reasoning"]
        assert ADVANCED_MODE_CONFIG["temperature"] == DEFAULT_CONFIG["temperature"]

    def test_mode_config_inheritance(self):
        """Test that mode configs properly inherit from default"""
        # Quick mode should have all default values plus iterations
        expected_keys = set(DEFAULT_CONFIG.keys()) | {"mutate_refine_iterations"}
        assert set(QUICK_MODE_CONFIG.keys()) == expected_keys

        # Advanced mode should have all default values plus iterations
        assert set(ADVANCED_MODE_CONFIG.keys()) == expected_keys

    def test_mode_config_differences(self):
        """Test differences between quick and advanced modes"""
        assert QUICK_MODE_CONFIG["mutate_refine_iterations"] < ADVANCED_MODE_CONFIG["mutate_refine_iterations"]

        # Other values should be the same
        for key in DEFAULT_CONFIG:
            assert QUICK_MODE_CONFIG[key] == ADVANCED_MODE_CONFIG[key]


class TestDomainConfigurations:
    """Test domain-specific configurations"""

    def test_domain_configs_exist(self):
        """Test that all expected domains are configured"""
        expected_domains = ["general", "technical", "creative", "business", "academic"]

        for domain in expected_domains:
            assert domain in DOMAIN_CONFIGS, f"Missing domain config: {domain}"

    def test_general_domain_config(self):
        """Test general domain configuration"""
        general_config = DOMAIN_CONFIGS["general"]

        assert "task_description" in general_config
        assert "base_instruction" in general_config
        assert "helpful assistant" in general_config["task_description"].lower()

    def test_technical_domain_config(self):
        """Test technical domain configuration"""
        technical_config = DOMAIN_CONFIGS["technical"]

        assert "task_description" in technical_config
        assert "base_instruction" in technical_config
        assert "technical expert" in technical_config["task_description"].lower()

        # Technical domain should have reduced style variation
        if "style_variation" in technical_config:
            assert technical_config["style_variation"] <= 3

    def test_creative_domain_config(self):
        """Test creative domain configuration"""
        creative_config = DOMAIN_CONFIGS["creative"]

        assert "task_description" in creative_config
        assert "base_instruction" in creative_config
        assert "creative" in creative_config["task_description"].lower()

        # Creative domain should have higher variation and temperature
        if "style_variation" in creative_config:
            assert creative_config["style_variation"] >= 4
        if "temperature" in creative_config:
            assert creative_config["temperature"] >= 0.7

    def test_business_domain_config(self):
        """Test business domain configuration"""
        business_config = DOMAIN_CONFIGS["business"]

        assert "task_description" in business_config
        assert "base_instruction" in business_config
        assert "business" in business_config["task_description"].lower()

        # Business domain should be more concise
        if "few_shot_count" in business_config:
            assert business_config["few_shot_count"] <= 3

    def test_academic_domain_config(self):
        """Test academic domain configuration"""
        academic_config = DOMAIN_CONFIGS["academic"]

        assert "task_description" in academic_config
        assert "base_instruction" in academic_config
        assert "academic" in academic_config["task_description"].lower()

        # Academic domain should be more thorough
        if "mutation_rounds" in academic_config:
            assert academic_config["mutation_rounds"] >= 3
        if "seen_set_size" in academic_config:
            assert academic_config["seen_set_size"] >= 25

    def test_domain_config_overrides(self):
        """Test that domain configs properly override defaults"""
        # Creative domain should override temperature
        creative_config = DOMAIN_CONFIGS["creative"]
        if "temperature" in creative_config:
            merged_config = {**DEFAULT_CONFIG, **creative_config}
            assert merged_config["temperature"] == creative_config["temperature"]
            assert merged_config["temperature"] != DEFAULT_CONFIG["temperature"]

        # Business domain should override few_shot_count
        business_config = DOMAIN_CONFIGS["business"]
        if "few_shot_count" in business_config:
            merged_config = {**DEFAULT_CONFIG, **business_config}
            assert merged_config["few_shot_count"] == business_config["few_shot_count"]
            assert merged_config["few_shot_count"] != DEFAULT_CONFIG["few_shot_count"]


class TestEnvironmentConfiguration:
    """Test environment-based configuration"""

    def test_default_convex_url(self):
        """Test default Convex URL"""
        assert CONVEX_BASE_URL is not None
        assert CONVEX_BASE_URL.startswith("https://")
        assert "convex.site" in CONVEX_BASE_URL

    @patch.dict(os.environ, {"CONVEX_URL": "https://custom-convex.example.com"})
    def test_custom_convex_url_from_env(self):
        """Test custom Convex URL from environment variable"""
        # Need to reimport to pick up new environment variable
        import importlib

        import promptevolver_cli.config

        importlib.reload(promptevolver_cli.config)

        assert promptevolver_cli.config.CONVEX_BASE_URL == "https://custom-convex.example.com"

    @patch.dict(os.environ, {}, clear=True)  # Clear all env vars
    def test_convex_url_fallback(self):
        """Test Convex URL fallback when env var not set"""
        import importlib

        import promptevolver_cli.config

        importlib.reload(promptevolver_cli.config)

        # Should fall back to default
        assert promptevolver_cli.config.CONVEX_BASE_URL.startswith("https://")
        assert "convex.site" in promptevolver_cli.config.CONVEX_BASE_URL


class TestTimeoutAndDelaySettings:
    """Test timeout and delay configurations"""

    def test_api_timeout_value(self):
        """Test API timeout is reasonable"""
        assert isinstance(API_TIMEOUT, int)
        assert API_TIMEOUT > 0
        assert API_TIMEOUT <= 300  # Should not be more than 5 minutes

    def test_batch_delay_value(self):
        """Test batch delay is reasonable"""
        assert isinstance(BATCH_DELAY, (int, float))
        assert BATCH_DELAY >= 0
        assert BATCH_DELAY <= 10  # Should not be more than 10 seconds

    def test_timeout_batch_delay_relationship(self):
        """Test relationship between timeout and batch delay"""
        # Batch delay should be much smaller than API timeout
        assert BATCH_DELAY < API_TIMEOUT / 10


class TestConfigurationMerging:
    """Test configuration merging logic"""

    def test_merge_default_with_quick_mode(self):
        """Test merging default config with quick mode"""
        merged = {**DEFAULT_CONFIG, **{"mutate_refine_iterations": 1}}

        # Should have all default values
        for key, value in DEFAULT_CONFIG.items():
            assert merged[key] == value

        # Plus the mode-specific value
        assert merged["mutate_refine_iterations"] == 1

    def test_merge_mode_with_domain(self):
        """Test merging mode config with domain config"""
        base_config = QUICK_MODE_CONFIG.copy()
        domain_config = DOMAIN_CONFIGS["creative"]
        merged = {**base_config, **domain_config}

        # Should have mode-specific values
        assert merged["mutate_refine_iterations"] == QUICK_MODE_CONFIG["mutate_refine_iterations"]

        # Should have domain-specific overrides
        for key, value in domain_config.items():
            assert merged[key] == value

        # Should have default values for non-overridden keys
        for key in DEFAULT_CONFIG:
            if key not in domain_config:
                assert merged[key] == DEFAULT_CONFIG[key]

    def test_full_config_merge(self):
        """Test full configuration merge (default + mode + domain)"""
        base_config = ADVANCED_MODE_CONFIG.copy()
        domain_config = DOMAIN_CONFIGS["academic"]
        final_config = {**base_config, **domain_config, "domain": "academic"}

        # Should have mode setting
        assert final_config["mutate_refine_iterations"] == ADVANCED_MODE_CONFIG["mutate_refine_iterations"]

        # Should have domain overrides
        for key, value in domain_config.items():
            assert final_config[key] == value

        # Should have domain identifier
        assert final_config["domain"] == "academic"

        # Should have all required keys
        all_keys = set(DEFAULT_CONFIG.keys()) | set(domain_config.keys()) | {"mutate_refine_iterations", "domain"}
        assert set(final_config.keys()) == all_keys


class TestConfigurationValidation:
    """Test configuration validation and constraints"""

    def test_temperature_ranges(self):
        """Test that temperature values are within valid ranges"""
        # Default temperature
        assert 0.0 <= DEFAULT_CONFIG["temperature"] <= 2.0

        # Domain-specific temperatures
        for domain, config in DOMAIN_CONFIGS.items():
            if "temperature" in config:
                assert 0.0 <= config["temperature"] <= 2.0, f"Invalid temperature in {domain} domain"

    def test_positive_integer_values(self):
        """Test that integer configuration values are positive"""
        integer_fields = ["mutation_rounds", "seen_set_size", "few_shot_count", "max_tokens"]

        # Check default config
        for field in integer_fields:
            assert DEFAULT_CONFIG[field] > 0, f"Invalid {field} in default config"

        # Check domain configs
        for domain, config in DOMAIN_CONFIGS.items():
            for field in integer_fields:
                if field in config:
                    assert config[field] > 0, f"Invalid {field} in {domain} domain"

    def test_reasonable_value_ranges(self):
        """Test that configuration values are in reasonable ranges"""
        # Mutation rounds should be reasonable (1-10)
        assert 1 <= DEFAULT_CONFIG["mutation_rounds"] <= 10

        # Few shot count should be reasonable (1-10)
        assert 1 <= DEFAULT_CONFIG["few_shot_count"] <= 10

        # Seen set size should be reasonable (5-100)
        assert 5 <= DEFAULT_CONFIG["seen_set_size"] <= 100

        # Max tokens should be reasonable (100-4000)
        assert 100 <= DEFAULT_CONFIG["max_tokens"] <= 4000

    def test_boolean_values(self):
        """Test that boolean configuration values are valid"""
        boolean_fields = ["generate_reasoning", "generate_expert_identity"]

        for field in boolean_fields:
            assert isinstance(DEFAULT_CONFIG[field], bool), f"{field} should be boolean"


class TestConfigurationDocumentation:
    """Test that configurations are well-documented through their values"""

    def test_task_descriptions_exist(self):
        """Test that all domains have task descriptions"""
        for domain, config in DOMAIN_CONFIGS.items():
            assert "task_description" in config, f"Missing task description for {domain}"
            assert len(config["task_description"]) > 10, f"Task description too short for {domain}"

    def test_base_instructions_exist(self):
        """Test that all domains have base instructions"""
        for domain, config in DOMAIN_CONFIGS.items():
            assert "base_instruction" in config, f"Missing base instruction for {domain}"
            assert len(config["base_instruction"]) > 10, f"Base instruction too short for {domain}"

    def test_domain_specialization(self):
        """Test that domain configurations are actually specialized"""
        task_descriptions = [config["task_description"] for config in DOMAIN_CONFIGS.values()]

        # All task descriptions should be different
        assert len(set(task_descriptions)) == len(task_descriptions), "Domain task descriptions should be unique"

        # Should contain domain-specific keywords
        assert "technical" in DOMAIN_CONFIGS["technical"]["task_description"].lower()
        assert "creative" in DOMAIN_CONFIGS["creative"]["task_description"].lower()
        assert "business" in DOMAIN_CONFIGS["business"]["task_description"].lower()
        assert "academic" in DOMAIN_CONFIGS["academic"]["task_description"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
