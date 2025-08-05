"""
Convex HTTP Client for PromptEvolver CLI
Simple client to interact with existing Convex actions via HTTP
"""

import requests
import time
from typing import Dict, Any, Optional
from .config import CONVEX_BASE_URL, API_TIMEOUT


class ConvexClient:
    """HTTP client for Convex actions"""

    def __init__(self, base_url: str = CONVEX_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def call_http_endpoint(
        self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Call a Convex HTTP endpoint

        Args:
            endpoint: HTTP endpoint path (e.g., "/health", "/optimize")
            method: HTTP method (GET, POST)
            data: Data to send in request body

        Returns:
            Dictionary containing the response

        Raises:
            ConvexError: If the API request fails
        """
        # Convex HTTP endpoint format
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers={"Content-Type": "application/json"},
                    timeout=API_TIMEOUT,
                )
            else:
                response = requests.post(
                    url,
                    json=data or {},
                    headers={"Content-Type": "application/json"},
                    timeout=API_TIMEOUT,
                )

            response.raise_for_status()
            result = response.json()

            # Handle our HTTP endpoint response format
            if result.get("status") == "success":
                return result.get("data", result)
            elif result.get("status") == "error":
                raise ConvexError(
                    f"Convex error: {result.get('error', 'Unknown error')}"
                )
            else:
                # Fallback for other response formats
                return result

        except requests.RequestException as e:
            raise ConvexError(f"API request failed: {str(e)}")

    def check_health(self) -> Dict[str, Any]:
        """Check Ollama/PromptWizard health"""
        return self.call_http_endpoint("/health", "GET")

    def optimize_prompt(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a single prompt using test pipeline"""
        return self.call_http_endpoint(
            "/optimize",
            "POST",
            {
                "prompt": prompt,
                "domain": config.get("domain", "general"),
                "config": config,
            },
        )

    def quick_optimize(self, session_id: str) -> Dict[str, Any]:
        """Run quick optimization (requires session ID)"""
        # Note: This requires session management which isn't available via HTTP endpoints
        # For now, we'll use the test optimization endpoint
        raise ConvexError(
            "Quick optimize requires authenticated session - use optimize_prompt instead"
        )

    def advanced_optimize(
        self, session_id: str, max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run advanced optimization (requires session ID)"""
        # Note: This requires session management which isn't available via HTTP endpoints
        # For now, we'll use the test optimization endpoint
        raise ConvexError(
            "Advanced optimize requires authenticated session - use optimize_prompt instead"
        )


class ConvexError(Exception):
    """Exception raised for Convex API errors"""

    pass
