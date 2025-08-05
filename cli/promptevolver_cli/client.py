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
        self.base_url = base_url.rstrip('/')
        
    def call_action(self, action_name: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a Convex action via HTTP
        
        Args:
            action_name: Name of the Convex action to call
            args: Arguments to pass to the action
            
        Returns:
            Dictionary containing the action result
            
        Raises:
            ConvexError: If the API request fails
        """
        # Convex HTTP API endpoint format
        url = f"{self.base_url}/api/action"
        payload = {
            "path": action_name,
            "args": args or {},
            "format": "json"
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=API_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle Convex response format
            if result.get("status") == "success":
                return result.get("value", result)
            elif result.get("status") == "error":
                raise ConvexError(f"Convex error: {result.get('errorMessage', 'Unknown error')}")
            else:
                # Fallback for other response formats
                return result
                
        except requests.RequestException as e:
            raise ConvexError(f"API request failed: {str(e)}")
    
    def check_health(self) -> Dict[str, Any]:
        """Check Ollama/PromptWizard health"""
        return self.call_action("actions:checkOllamaHealth")
    
    def optimize_prompt(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a single prompt using test pipeline"""
        return self.call_action("actions:testOptimizationPipeline", {
            "testPrompt": prompt,
            "contextDomain": config.get("domain", "general")
        })
    
    def quick_optimize(self, session_id: str) -> Dict[str, Any]:
        """Run quick optimization (requires session ID)"""
        return self.call_action("actions:quickOptimize", {
            "sessionId": session_id
        })
    
    def advanced_optimize(self, session_id: str, max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """Run advanced optimization (requires session ID)"""
        args = {"sessionId": session_id}
        if max_iterations:
            args["maxIterations"] = max_iterations
        return self.call_action("actions:advancedOptimize", args)

class ConvexError(Exception):
    """Exception raised for Convex API errors"""
    pass