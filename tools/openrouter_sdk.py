"""
OpenRouter SDK Suite (OpenAI-Compatible)
Provides comprehensive OOP interface for OpenRouter API operations with focus on free models.

This suite provides:
- OpenRouterClient: Base client for API interactions
- OpenRouterModels: Model management and listing
- OpenRouterChat: Chat completion operations
- OpenRouterUtilities: Helper functions for common operations
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional, Iterator, Union
from datetime import datetime
from enum import Enum


class ModelTier(Enum):
    """Model pricing tiers"""
    FREE = "free"
    PAID = "paid"
    ALL = "all"


class OpenRouterClient:
    """
    Base client for OpenRouter API interactions.
    Handles authentication, request management, and error handling.
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (can be set via OPENROUTER_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        import os
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set via OPENROUTER_API_KEY environment variable")
        
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/cbwinslow/cbw-agents",
            "X-Title": "CBW Agents OpenRouter SDK",
            "Content-Type": "application/json"
        })
        
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make HTTP request to OpenRouter API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request payload
            stream: Whether to stream the response
            
        Returns:
            Response data or Response object if streaming
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=self.timeout)
                elif method == "POST":
                    response = self.session.post(
                        url, 
                        json=data, 
                        timeout=self.timeout,
                        stream=stream
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                if stream:
                    return response
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                time.sleep(self.retry_delay * (attempt + 1))
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def get_models(self) -> Dict[str, Any]:
        """
        Get list of available models.
        
        Returns:
            Dictionary with models list
        """
        response = self._make_request("GET", "/models")
        if isinstance(response, dict) and "data" in response:
            return {"success": True, "models": response["data"]}
        elif isinstance(response, dict) and "error" in response:
            return response
        return {"success": True, "models": response}
    
    def get_limits(self) -> Dict[str, Any]:
        """
        Get current API usage limits.
        
        Returns:
            Dictionary with usage limits
        """
        response = self._make_request("GET", "/auth/key")
        if isinstance(response, dict) and "error" not in response:
            return {"success": True, "limits": response}
        return response


class OpenRouterModels:
    """
    Model management and discovery operations.
    Provides utilities for listing, filtering, and selecting models.
    """
    
    def __init__(self, client: OpenRouterClient):
        """
        Initialize model manager.
        
        Args:
            client: OpenRouterClient instance
        """
        self.client = client
        self._models_cache = None
        self._cache_time = None
        self._cache_ttl = 3600  # 1 hour
    
    def list_models(
        self, 
        tier: ModelTier = ModelTier.ALL,
        refresh_cache: bool = False
    ) -> Dict[str, Any]:
        """
        List available models with optional filtering.
        
        Args:
            tier: Filter by pricing tier (FREE, PAID, ALL)
            refresh_cache: Force refresh of models cache
            
        Returns:
            Dictionary with filtered models
        """
        # Check cache
        if not refresh_cache and self._models_cache and self._cache_time:
            if time.time() - self._cache_time < self._cache_ttl:
                models = self._models_cache
            else:
                result = self.client.get_models()
                if not result.get("success", True):
                    return result
                models = result.get("models", [])
                self._models_cache = models
                self._cache_time = time.time()
        else:
            result = self.client.get_models()
            if not result.get("success", True):
                return result
            models = result.get("models", [])
            self._models_cache = models
            self._cache_time = time.time()
        
        # Filter by tier using utility method for consistency
        if tier == ModelTier.FREE:
            filtered = [m for m in models if OpenRouterUtilities.is_free_model(m)]
        elif tier == ModelTier.PAID:
            filtered = [m for m in models if not OpenRouterUtilities.is_free_model(m)]
        else:
            filtered = models
        
        return {
            "success": True,
            "models": filtered,
            "count": len(filtered),
            "tier": tier.value
        }
    
    def get_free_models(self) -> Dict[str, Any]:
        """
        Get list of free models only.
        
        Returns:
            Dictionary with free models
        """
        return self.list_models(tier=ModelTier.FREE)
    
    def find_model(self, query: str, tier: ModelTier = ModelTier.ALL) -> Dict[str, Any]:
        """
        Find models matching a search query.
        
        Args:
            query: Search query (matches model id and name)
            tier: Filter by pricing tier
            
        Returns:
            Dictionary with matching models
        """
        result = self.list_models(tier=tier)
        if not result["success"]:
            return result
        
        query_lower = query.lower()
        matched = [
            m for m in result["models"]
            if query_lower in m.get("id", "").lower() 
            or query_lower in m.get("name", "").lower()
        ]
        
        return {
            "success": True,
            "models": matched,
            "count": len(matched),
            "query": query
        }
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dictionary with model information
        """
        result = self.list_models()
        if not result["success"]:
            return result
        
        for model in result["models"]:
            if model.get("id") == model_id:
                return {
                    "success": True,
                    "model": model
                }
        
        return {
            "success": False,
            "error": f"Model not found: {model_id}"
        }
    
    def get_recommended_free_model(self, use_case: str = "general") -> Dict[str, Any]:
        """
        Get recommended free model for a specific use case.
        
        Args:
            use_case: Use case (general, coding, reasoning, multimodal)
            
        Returns:
            Dictionary with recommended model
        """
        # Recommended free models by use case
        recommendations = {
            "general": "meta-llama/llama-3.1-8b-instruct:free",
            "coding": "google/gemma-2-9b-it:free",
            "reasoning": "microsoft/phi-4:free",
            "multimodal": "meta-llama/llama-3.2-11b-vision-instruct:free"
        }
        
        model_id = recommendations.get(use_case, recommendations["general"])
        
        return {
            "success": True,
            "model_id": model_id,
            "use_case": use_case,
            "note": "This is a recommended free model. Availability may vary."
        }


class OpenRouterChat:
    """
    Chat completion operations with streaming support.
    Handles message formatting, completion requests, and response processing.
    """
    
    def __init__(self, client: OpenRouterClient):
        """
        Initialize chat manager.
        
        Args:
            client: OpenRouterClient instance
        """
        self.client = client
        self.conversation_history = []
    
    def create_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: Model identifier
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            stream: Whether to stream the response
            **kwargs: Additional parameters for OpenRouter API
            
        Returns:
            Dictionary with completion result
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if stream:
            payload["stream"] = True
            response = self.client._make_request(
                "POST", 
                "/chat/completions", 
                data=payload,
                stream=True
            )
            
            if isinstance(response, dict) and "error" in response:
                return response
            
            return {
                "success": True,
                "stream": True,
                "response": response
            }
        
        response = self.client._make_request(
            "POST", 
            "/chat/completions", 
            data=payload
        )
        
        if isinstance(response, dict) and "error" in response:
            return response
        
        # Store in conversation history
        if "choices" in response and len(response["choices"]) > 0:
            assistant_message = response["choices"][0]["message"]
            self.conversation_history.extend(messages)
            self.conversation_history.append(assistant_message)
        
        return {
            "success": True,
            "response": response,
            "message": response.get("choices", [{}])[0].get("message", {}),
            "usage": response.get("usage", {})
        }
    
    def create_streaming_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Iterator[str]:
        """
        Create a streaming chat completion.
        
        Args:
            model: Model identifier
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Yields:
            Content chunks from the stream
        """
        result = self.create_completion(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        if not result.get("success"):
            yield json.dumps({"error": result.get("error")})
            return
        
        response = result["response"]
        
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8')
                if line_text.startswith('data: '):
                    data_text = line_text[6:]
                    if data_text == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_text)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue
    
    def chat(
        self,
        message: str,
        model: str = "meta-llama/llama-3.1-8b-instruct:free",
        system_message: Optional[str] = None,
        use_history: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Simple chat interface with optional conversation history.
        
        Args:
            message: User message
            model: Model to use
            system_message: Optional system message
            use_history: Whether to include conversation history
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with chat response
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        if use_history:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        return self.create_completion(model=model, messages=messages, **kwargs)
    
    def clear_history(self) -> Dict[str, Any]:
        """
        Clear conversation history.
        
        Returns:
            Dictionary with success status
        """
        self.conversation_history = []
        return {"success": True, "message": "Conversation history cleared"}
    
    def get_history(self) -> Dict[str, Any]:
        """
        Get conversation history.
        
        Returns:
            Dictionary with conversation history
        """
        return {
            "success": True,
            "history": self.conversation_history,
            "count": len(self.conversation_history)
        }


class OpenRouterUtilities:
    """
    Utility functions for common OpenRouter operations.
    Provides helpers for token estimation, response formatting, and more.
    """
    
    @staticmethod
    def estimate_tokens(text: str, method: str = "simple") -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            method: Estimation method (simple, words, chars)
            
        Returns:
            Estimated token count
        """
        if method == "simple":
            # Rough estimate: ~4 chars per token
            return len(text) // 4
        elif method == "words":
            # Rough estimate: ~0.75 tokens per word
            return int(len(text.split()) * 0.75)
        elif method == "chars":
            # Character-based estimate
            return len(text) // 4
        return 0
    
    @staticmethod
    def format_messages(
        user_message: str,
        system_message: Optional[str] = None,
        history: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        Format messages for chat completion.
        
        Args:
            user_message: User's message
            system_message: Optional system message
            history: Optional conversation history
            
        Returns:
            Formatted messages list
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    @staticmethod
    def extract_content(response: Dict[str, Any]) -> Optional[str]:
        """
        Extract text content from completion response.
        
        Args:
            response: Completion response dictionary
            
        Returns:
            Extracted content or None
        """
        if not response.get("success"):
            return None
        
        resp_data = response.get("response", {})
        choices = resp_data.get("choices", [])
        
        if choices and len(choices) > 0:
            message = choices[0].get("message", {})
            return message.get("content")
        
        return None
    
    @staticmethod
    def calculate_cost(
        prompt_tokens: int,
        completion_tokens: int,
        prompt_price: float = 0.0,
        completion_price: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate cost for a completion request.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            prompt_price: Price per 1M prompt tokens
            completion_price: Price per 1M completion tokens
            
        Returns:
            Dictionary with cost breakdown
        """
        prompt_cost = (prompt_tokens / 1_000_000) * prompt_price
        completion_cost = (completion_tokens / 1_000_000) * completion_price
        total_cost = prompt_cost + completion_cost
        
        return {
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "total_cost": total_cost,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
    
    @staticmethod
    def collect_streaming_output(iterator: Iterator[str]) -> str:
        """
        Collect streaming output into a single string without printing.
        
        Args:
            iterator: Stream iterator
            
        Returns:
            Combined output string
        """
        output = []
        for chunk in iterator:
            output.append(chunk)
        return "".join(output)
    
    @staticmethod
    def print_streaming_output(iterator: Iterator[str], prefix: str = "") -> str:
        """
        Print and collect streaming output in real-time.
        
        Args:
            iterator: Stream iterator
            prefix: Optional prefix for each chunk
            
        Returns:
            Combined output string
        """
        output = []
        for chunk in iterator:
            if prefix:
                print(prefix + chunk, end="", flush=True)
            else:
                print(chunk, end="", flush=True)
            output.append(chunk)
        print()  # New line at end
        return "".join(output)
    
    @staticmethod
    def validate_model_id(model_id: str) -> bool:
        """
        Validate model ID format.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if valid format
        """
        # Basic validation: should contain provider/model format
        return "/" in model_id and len(model_id.split("/")) >= 2
    
    @staticmethod
    def get_error_message(response: Dict[str, Any]) -> Optional[str]:
        """
        Extract error message from response.
        
        Args:
            response: Response dictionary
            
        Returns:
            Error message or None
        """
        if response.get("success") is False:
            return response.get("error", "Unknown error")
        return None
    
    @staticmethod
    def is_free_model(model_info: Dict[str, Any]) -> bool:
        """
        Check if a model is free.
        
        Args:
            model_info: Model information dictionary
            
        Returns:
            True if model is free
        """
        pricing = model_info.get("pricing", {})
        prompt_price = float(pricing.get("prompt", "0"))
        completion_price = float(pricing.get("completion", "0"))
        return prompt_price == 0.0 and completion_price == 0.0


# OpenAI function definitions for agent integration
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_openrouter_models",
            "description": "List available OpenRouter models with optional filtering by pricing tier",
            "parameters": {
                "type": "object",
                "properties": {
                    "tier": {
                        "type": "string",
                        "enum": ["free", "paid", "all"],
                        "description": "Filter models by pricing tier",
                        "default": "all"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_free_models",
            "description": "Get list of free OpenRouter models",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_model",
            "description": "Search for OpenRouter models by name or ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to match model names or IDs"
                    },
                    "tier": {
                        "type": "string",
                        "enum": ["free", "paid", "all"],
                        "description": "Filter by pricing tier",
                        "default": "all"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chat_completion",
            "description": "Create a chat completion using OpenRouter with specified model",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Model identifier (e.g., 'meta-llama/llama-3.1-8b-instruct:free')"
                    },
                    "message": {
                        "type": "string",
                        "description": "User message to send"
                    },
                    "system_message": {
                        "type": "string",
                        "description": "Optional system message to set behavior"
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Sampling temperature (0-2)",
                        "default": 1.0
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to generate"
                    }
                },
                "required": ["model", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_tokens",
            "description": "Estimate token count for a text string",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to estimate tokens for"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["simple", "words", "chars"],
                        "description": "Estimation method",
                        "default": "simple"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommended_model",
            "description": "Get recommended free model for a specific use case",
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case": {
                        "type": "string",
                        "enum": ["general", "coding", "reasoning", "multimodal"],
                        "description": "Use case for model selection",
                        "default": "general"
                    }
                },
                "required": ["use_case"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "openrouter_sdk",
    "description": "Comprehensive OOP SDK for OpenRouter API with focus on free models",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "list_models",
        "get_free_models",
        "find_model",
        "chat_completion",
        "streaming_chat",
        "token_estimation",
        "cost_calculation",
        "model_recommendations"
    ],
    "requirements": ["requests"],
    "features": [
        "OOP design with multiple classes",
        "Support for free models",
        "Streaming support",
        "Conversation history",
        "Token estimation utilities",
        "Error handling and retries",
        "OpenAI-compatible function definitions"
    ]
}


if __name__ == "__main__":
    # Example usage
    import os
    
    print("=== OpenRouter SDK Example ===\n")
    
    # Check for API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("Please set OPENROUTER_API_KEY environment variable")
        print("Example: export OPENROUTER_API_KEY='your-key-here'")
    else:
        # Initialize client
        client = OpenRouterClient()
        
        # Initialize managers
        models = OpenRouterModels(client)
        chat = OpenRouterChat(client)
        utils = OpenRouterUtilities()
        
        # List free models
        print("1. Listing free models...")
        result = models.get_free_models()
        if result["success"]:
            print(f"   Found {result['count']} free models")
            if result["models"]:
                print(f"   Example: {result['models'][0].get('id', 'N/A')}")
        
        # Get recommended model
        print("\n2. Getting recommended model for coding...")
        rec = models.get_recommended_free_model("coding")
        print(f"   Recommended: {rec['model_id']}")
        
        # Estimate tokens
        print("\n3. Estimating tokens...")
        text = "Hello, this is a test message!"
        tokens = utils.estimate_tokens(text)
        print(f"   Text: '{text}'")
        print(f"   Estimated tokens: {tokens}")
        
        print("\n=== Example Complete ===")
