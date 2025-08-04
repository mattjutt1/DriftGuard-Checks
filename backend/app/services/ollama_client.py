"""
Ollama client for local AI model integration.
Provides async communication with Ollama server for prompt optimization.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
import json

from ..core.config import settings

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    """Custom exception for Ollama-related errors."""
    pass


class OllamaClient:
    """
    Async client for communicating with Ollama server.
    
    Handles model communication, error recovery, and performance monitoring
    for the PromptWizard integration.
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.max_retries = settings.OLLAMA_MAX_RETRIES
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make an async HTTP request to Ollama server with retry logic.
        
        Args:
            endpoint: API endpoint to call
            data: Request payload
            retry_count: Current retry attempt
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            OllamaError: If request fails after all retries
        """
        if not self._client:
            raise OllamaError("Client not initialized. Use async context manager.")
        
        try:
            response = await self._client.post(endpoint, json=data)
            response.raise_for_status()
            
            # Handle streaming responses
            if response.headers.get("content-type", "").startswith("application/x-ndjson"):
                return await self._handle_streaming_response(response)
            else:
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self._make_request(endpoint, data, retry_count + 1)
            raise OllamaError(f"HTTP error after {self.max_retries} retries: {e}")
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            if retry_count < self.max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self._make_request(endpoint, data, retry_count + 1)
            raise OllamaError(f"Request error after {self.max_retries} retries: {e}")
    
    async def _handle_streaming_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle streaming NDJSON response from Ollama.
        
        Args:
            response: HTTP response object
            
        Returns:
            Dict[str, Any]: Parsed response data
        """
        full_response = ""
        final_data = None
        
        async for line in response.aiter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                    if data.get("done", False):
                        final_data = data
                        break
                except json.JSONDecodeError:
                    continue
        
        if final_data:
            final_data["response"] = full_response
            return final_data
        else:
            return {"response": full_response, "done": True}
    
    async def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a completion using the Ollama model.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stop_sequences: List of stop sequences
            
        Returns:
            Dict[str, Any]: Model response with metadata
        """
        # Prepare the request data
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,  # Use streaming for better UX
            "options": {
                "temperature": temperature,
            }
        }
        
        if system_prompt:
            request_data["system"] = system_prompt
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        if stop_sequences:
            request_data["options"]["stop"] = stop_sequences
        
        start_time = datetime.utcnow()
        
        try:
            response = await self._make_request("/api/generate", request_data)
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Add metadata to response
            response.update({
                "processing_time": processing_time,
                "model_used": self.model,
                "temperature": temperature,
                "timestamp": end_time.isoformat(),
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise OllamaError(f"Failed to generate completion: {e}")
    
    async def check_model_availability(self) -> bool:
        """
        Check if the specified model is available on the Ollama server.
        
        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            response = await self._make_request("/api/tags", {})
            models = response.get("models", [])
            
            for model in models:
                if model.get("name", "").startswith(self.model.split(":")[0]):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dict[str, Any]: Model information
        """
        try:
            response = await self._make_request("/api/show", {"model": self.model})
            return response
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            raise OllamaError(f"Failed to get model info: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the Ollama server.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        start_time = datetime.utcnow()
        
        try:
            # Simple test generation
            test_response = await self.generate_completion(
                prompt="Say 'Hello'",
                temperature=0.1,
                max_tokens=10
            )
            
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()
            
            model_available = await self.check_model_availability()
            
            return {
                "status": "healthy",
                "model": self.model,
                "model_available": model_available,
                "response_time": response_time,
                "server_url": self.base_url,
                "timestamp": end_time.isoformat(),
                "test_response": test_response.get("response", "")[:50] + "..."
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "model": self.model,
                "error": str(e),
                "server_url": self.base_url,
                "timestamp": datetime.utcnow().isoformat()
            }