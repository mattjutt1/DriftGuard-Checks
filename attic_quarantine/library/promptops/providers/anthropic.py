"""Anthropic provider implementation with offline fuse."""

import os
from typing import Any, Dict, List

from .base import LLMProvider, ProviderDisabled


class AnthropicProvider:
    """Anthropic provider with offline-first design."""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (will check environment if not provided)
            model: Model name to use

        Raises:
            ProviderDisabled: When offline mode is enabled
        """
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        # Offline fuse - raise if conditions not met
        promptops_mode = os.getenv("PROMPTOPS_MODE", "stub")
        allow_network = os.getenv("ALLOW_NETWORK", "0").lower() in ("1", "true", "yes")

        if promptops_mode == "stub":
            raise ProviderDisabled("PROMPTOPS_MODE is set to 'stub' - real providers disabled")

        if not allow_network:
            raise ProviderDisabled("ALLOW_NETWORK is not enabled - real providers disabled")

        if not self.api_key:
            raise ProviderDisabled("ANTHROPIC_API_KEY not found - real providers disabled")

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send chat messages to Anthropic API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            Dict containing response data with usage statistics
        """
        # TODO: Implement real Anthropic API integration
        # This will be implemented when providers are enabled
        # Expected implementation:
        #   - Use anthropic library to call messages API
        #   - Handle rate limits and retries
        #   - Return structured response with usage data
        #   - Log costs and token usage
        #   - Convert OpenAI-style messages to Anthropic format

        # For now, return stub response matching expected format
        return {
            "content": "Simulated Anthropic response",
            "model": self.model,
            "usage": {
                "input_tokens": 45,
                "output_tokens": 25,
                "total_tokens": 70
            },
            "provider": "anthropic"
        }

    def chat_sync(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Synchronous version of chat method.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            Dict containing response data with usage statistics
        """
        # TODO: Implement synchronous Anthropic API integration
        # This will be implemented when providers are enabled

        # For now, return stub response matching expected format
        return {
            "content": "Simulated Anthropic sync response",
            "model": self.model,
            "usage": {
                "input_tokens": 45,
                "output_tokens": 25,
                "total_tokens": 70
            },
            "provider": "anthropic"
        }
