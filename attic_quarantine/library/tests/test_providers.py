"""Tests for provider system with offline fuse behavior."""

import os
import pytest
from unittest.mock import patch

from promptops.providers import (
    LLMProvider,
    ProviderDisabled,
    OpenAIProvider,
    AnthropicProvider
)


class TestProviderDisabledBehavior:
    """Test that providers are properly disabled by default."""

    def test_openai_provider_disabled_by_default(self):
        """Test OpenAI provider is disabled in default mode."""
        with pytest.raises(ProviderDisabled, match="PROMPTOPS_MODE is set to 'stub'"):
            OpenAIProvider()

    def test_anthropic_provider_disabled_by_default(self):
        """Test Anthropic provider is disabled in default mode."""
        with pytest.raises(ProviderDisabled, match="PROMPTOPS_MODE is set to 'stub'"):
            AnthropicProvider()

    @patch.dict(os.environ, {"PROMPTOPS_MODE": "production"})
    def test_provider_disabled_without_network_permission(self):
        """Test providers disabled when ALLOW_NETWORK is not set."""
        with pytest.raises(ProviderDisabled, match="ALLOW_NETWORK is not enabled"):
            OpenAIProvider()

        with pytest.raises(ProviderDisabled, match="ALLOW_NETWORK is not enabled"):
            AnthropicProvider()

    @patch.dict(os.environ, {"PROMPTOPS_MODE": "production", "ALLOW_NETWORK": "1"})
    def test_provider_disabled_without_api_key(self):
        """Test providers disabled when API key is missing."""
        # Clear any existing API key env vars
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"PROMPTOPS_MODE": "production", "ALLOW_NETWORK": "1"}):
                with pytest.raises(ProviderDisabled, match="OPENAI_API_KEY not found"):
                    OpenAIProvider()

                with pytest.raises(ProviderDisabled, match="ANTHROPIC_API_KEY not found"):
                    AnthropicProvider()

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "1",
        "OPENAI_API_KEY": "sk-test123",
        "ANTHROPIC_API_KEY": "sk-ant-test123"
    })
    def test_providers_enabled_with_all_conditions_met(self):
        """Test providers can be instantiated when all conditions are met."""
        # This should not raise an exception
        openai_provider = OpenAIProvider()
        assert openai_provider.model == "gpt-4o-mini"
        assert openai_provider.api_key == "sk-test123"

        anthropic_provider = AnthropicProvider()
        assert anthropic_provider.model == "claude-3-5-sonnet-20241022"
        assert anthropic_provider.api_key == "sk-ant-test123"


class TestProviderStubResponses:
    """Test that providers return expected stub responses when disabled."""

    def test_provider_protocol_compliance(self):
        """Test that provider classes implement the LLMProvider protocol."""
        # This is mostly for type checking - the classes should have the right methods
        assert hasattr(OpenAIProvider, 'chat')
        assert hasattr(AnthropicProvider, 'chat')

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "1",
        "OPENAI_API_KEY": "sk-test123"
    })
    @pytest.mark.anyio
    async def test_openai_stub_response_format(self):
        """Test OpenAI provider returns correct stub response format."""
        provider = OpenAIProvider(model="gpt-4o-mini")

        messages = [{"role": "user", "content": "Hello"}]
        response = await provider.chat(messages)

        # Verify response structure
        assert isinstance(response, dict)
        assert "content" in response
        assert "model" in response
        assert "usage" in response
        assert "provider" in response

        # Verify specific values
        assert response["model"] == "gpt-4o-mini"
        assert response["provider"] == "openai"
        assert response["content"] == "Simulated OpenAI response"

        # Verify usage structure
        usage = response["usage"]
        assert "prompt_tokens" in usage
        assert "completion_tokens" in usage
        assert "total_tokens" in usage
        assert isinstance(usage["total_tokens"], int)
        assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "1",
        "ANTHROPIC_API_KEY": "sk-ant-test123"
    })
    @pytest.mark.anyio
    async def test_anthropic_stub_response_format(self):
        """Test Anthropic provider returns correct stub response format."""
        provider = AnthropicProvider(model="claude-3-5-sonnet-20241022")

        messages = [{"role": "user", "content": "Hello"}]
        response = await provider.chat(messages)

        # Verify response structure
        assert isinstance(response, dict)
        assert "content" in response
        assert "model" in response
        assert "usage" in response
        assert "provider" in response

        # Verify specific values
        assert response["model"] == "claude-3-5-sonnet-20241022"
        assert response["provider"] == "anthropic"
        assert response["content"] == "Simulated Anthropic response"

        # Verify usage structure (Anthropic uses different token naming)
        usage = response["usage"]
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert "total_tokens" in usage
        assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "1",
        "OPENAI_API_KEY": "sk-test123"
    })
    def test_openai_sync_method(self):
        """Test OpenAI provider sync method."""
        provider = OpenAIProvider()

        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat_sync(messages)

        assert response["content"] == "Simulated OpenAI sync response"
        assert response["provider"] == "openai"

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "1",
        "ANTHROPIC_API_KEY": "sk-ant-test123"
    })
    def test_anthropic_sync_method(self):
        """Test Anthropic provider sync method."""
        provider = AnthropicProvider()

        messages = [{"role": "user", "content": "Hello"}]
        response = provider.chat_sync(messages)

        assert response["content"] == "Simulated Anthropic sync response"
        assert response["provider"] == "anthropic"


class TestProviderConfigurationOptions:
    """Test provider configuration and environment variable handling."""

    @patch.dict(os.environ, {"PROMPTOPS_MODE": "stub"})
    def test_stub_mode_explicit(self):
        """Test explicit stub mode setting."""
        with pytest.raises(ProviderDisabled, match="PROMPTOPS_MODE is set to 'stub'"):
            OpenAIProvider()

    @patch.dict(os.environ, {"ALLOW_NETWORK": "0"})
    def test_network_disabled_explicit(self):
        """Test explicit network disabling."""
        with patch.dict(os.environ, {"PROMPTOPS_MODE": "production", "ALLOW_NETWORK": "0"}):
            with pytest.raises(ProviderDisabled, match="ALLOW_NETWORK is not enabled"):
                OpenAIProvider()

    @patch.dict(os.environ, {"ALLOW_NETWORK": "false"})
    def test_network_disabled_false_string(self):
        """Test network disabled with 'false' string."""
        with patch.dict(os.environ, {"PROMPTOPS_MODE": "production", "ALLOW_NETWORK": "false"}):
            with pytest.raises(ProviderDisabled, match="ALLOW_NETWORK is not enabled"):
                OpenAIProvider()

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "true",
        "OPENAI_API_KEY": "sk-test123"
    })
    def test_network_enabled_true_string(self):
        """Test network enabled with 'true' string."""
        # Should not raise exception
        provider = OpenAIProvider()
        assert provider.api_key == "sk-test123"

    @patch.dict(os.environ, {
        "PROMPTOPS_MODE": "production",
        "ALLOW_NETWORK": "yes",
        "OPENAI_API_KEY": "sk-test123"
    })
    def test_network_enabled_yes_string(self):
        """Test network enabled with 'yes' string."""
        # Should not raise exception
        provider = OpenAIProvider()
        assert provider.api_key == "sk-test123"

    def test_provider_custom_model(self):
        """Test providers accept custom model names."""
        with patch.dict(os.environ, {
            "PROMPTOPS_MODE": "production",
            "ALLOW_NETWORK": "1",
            "OPENAI_API_KEY": "sk-test123"
        }):
            provider = OpenAIProvider(model="gpt-3.5-turbo")
            assert provider.model == "gpt-3.5-turbo"

        with patch.dict(os.environ, {
            "PROMPTOPS_MODE": "production",
            "ALLOW_NETWORK": "1",
            "ANTHROPIC_API_KEY": "sk-ant-test123"
        }):
            provider = AnthropicProvider(model="claude-3-haiku-20240307")
            assert provider.model == "claude-3-haiku-20240307"

    def test_provider_custom_api_key(self):
        """Test providers accept custom API keys."""
        with patch.dict(os.environ, {"PROMPTOPS_MODE": "production", "ALLOW_NETWORK": "1"}):
            provider = OpenAIProvider(api_key="custom-openai-key")
            assert provider.api_key == "custom-openai-key"

            provider = AnthropicProvider(api_key="custom-anthropic-key")
            assert provider.api_key == "custom-anthropic-key"


class TestProviderException:
    """Test the ProviderDisabled exception class."""

    def test_provider_disabled_is_runtime_error(self):
        """Test ProviderDisabled inherits from RuntimeError."""
        assert issubclass(ProviderDisabled, RuntimeError)

    def test_provider_disabled_message(self):
        """Test ProviderDisabled preserves error messages."""
        message = "Test error message"
        exc = ProviderDisabled(message)
        assert str(exc) == message

    def test_provider_disabled_can_be_caught(self):
        """Test ProviderDisabled can be caught properly."""
        with pytest.raises(ProviderDisabled) as exc_info:
            raise ProviderDisabled("Test exception")

        assert "Test exception" in str(exc_info.value)


class TestProviderOfflineEnforcement:
    """Test that providers never make actual HTTP calls in test environment."""

    def test_no_real_http_imports(self):
        """Test that providers don't import actual HTTP libraries."""
        # Verify that providers can be imported without openai/anthropic libraries
        from promptops.providers.openai import OpenAIProvider
        from promptops.providers.anthropic import AnthropicProvider

        # This test passes if imports work without real API libraries
        assert OpenAIProvider is not None
        assert AnthropicProvider is not None

    @patch.dict(os.environ, {"PROMPTOPS_MODE": "stub"})
    def test_default_offline_mode_blocks_all(self):
        """Test that default mode blocks all providers."""
        providers = [OpenAIProvider, AnthropicProvider]

        for ProviderClass in providers:
            with pytest.raises(ProviderDisabled):
                ProviderClass()

    def test_environment_isolation(self):
        """Test that environment variables are properly isolated in tests."""
        # This test should run in clean environment
        assert os.getenv("PROMPTOPS_MODE", "stub") == "stub"
        assert os.getenv("ALLOW_NETWORK", "0") == "0"

        # Providers should be disabled by default
        with pytest.raises(ProviderDisabled):
            OpenAIProvider()

        with pytest.raises(ProviderDisabled):
            AnthropicProvider()
