"""OpenAI provider implementation with offline fuse."""

import os
from typing import Any, Dict, List

from .base import LLMProvider, ProviderDisabled


class OpenAIProvider:
    """OpenAI provider with offline-first design."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (will check environment if not provided)
            model: Model name to use

        Raises:
            ProviderDisabled: When offline mode is enabled
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        # Offline fuse - raise if conditions not met
        promptops_mode = os.getenv("PROMPTOPS_MODE", "stub")
        allow_network = os.getenv("ALLOW_NETWORK", "0").lower() in ("1", "true", "yes")

        if promptops_mode == "stub":
            raise ProviderDisabled("PROMPTOPS_MODE is set to 'stub' - real providers disabled")

        if not allow_network:
            raise ProviderDisabled("ALLOW_NETWORK is not enabled - real providers disabled")

        if not self.api_key:
            raise ProviderDisabled("OPENAI_API_KEY not found - real providers disabled")

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send chat messages to OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            Dict containing response data with usage statistics
        """
        # TODO: Implement real OpenAI API integration
        # This will be implemented when providers are enabled
        # Expected implementation:
        #   - Use openai library to call chat completions
        #   - Handle rate limits and retries
        #   - Return structured response with usage data
        #   - Log costs and token usage

        # For now, return stub response matching expected format
        return {
            "content": "Simulated OpenAI response",
            "model": self.model,
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            },
            "provider": "openai"
        }

    def chat_sync(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Synchronous version of chat method.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            Dict containing response data with usage statistics
        """
        # TODO: Implement synchronous OpenAI API integration
        # This will be implemented when providers are enabled

        # For now, return stub response matching expected format
        return {
            "content": "Simulated OpenAI sync response",
            "model": self.model,
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 20,
                "total_tokens": 70
            },
            "provider": "openai"
        }
