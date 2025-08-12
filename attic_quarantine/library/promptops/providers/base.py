"""Base provider interfaces and protocols."""

from typing import Any, Dict, List, Protocol


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Send chat messages to the LLM provider.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict containing response data with usage statistics

        Raises:
            ProviderDisabled: When provider is disabled by configuration
        """
        ...


class ProviderDisabled(RuntimeError):
    """Raised when a provider is disabled by configuration."""
    pass
