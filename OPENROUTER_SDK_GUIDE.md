# OpenRouter SDK Suite

Comprehensive Object-Oriented Python SDK for OpenRouter API with focus on free models and agent integration.

## 📚 Overview

The OpenRouter SDK Suite provides a complete, OOP-based interface for interacting with the OpenRouter API. It includes specialized classes for different operations, utility functions for common tasks, and full support for OpenAI-compatible function calling.

### Key Features

- **🎯 OOP Design**: Clean, modular class structure
- **💰 Free Model Focus**: Built-in filtering and recommendations for zero-cost models
- **🔄 Streaming Support**: Real-time response streaming
- **📝 Conversation History**: Automatic conversation tracking
- **🛠️ Utility Functions**: Token estimation, cost calculation, formatting helpers
- **🔌 OpenAI Compatible**: Drop-in replacement for OpenAI API
- **🔁 Retry Logic**: Automatic retry with exponential backoff
- **✨ Agent Ready**: Pre-defined OpenAI function definitions for agent integration

## 🚀 Quick Start

### Installation

```bash
# Install required dependencies
pip install requests

# Set your API key
export OPENROUTER_API_KEY='your-key-here'
```

### Basic Usage

```python
from tools.openrouter_sdk import (
    OpenRouterClient,
    OpenRouterModels,
    OpenRouterChat,
    OpenRouterUtilities
)

# Initialize
client = OpenRouterClient()
models = OpenRouterModels(client)
chat = OpenRouterChat(client)
utils = OpenRouterUtilities()

# List free models
free_models = models.get_free_models()
print(f"Found {free_models['count']} free models")

# Simple chat
result = chat.chat(
    message="What is Python?",
    model="meta-llama/llama-3.1-8b-instruct:free"
)
print(result["message"]["content"])
```

## 📦 Classes

### 1. OpenRouterClient

Base client for API interactions with authentication and request management.

```python
client = OpenRouterClient(
    api_key="your-key",      # Optional if set in env
    timeout=120,              # Request timeout
    max_retries=3,            # Retry attempts
    retry_delay=2             # Delay between retries
)

# Get available models
models = client.get_models()

# Get usage limits
limits = client.get_limits()
```

**Methods:**
- `get_models()`: Retrieve available models
- `get_limits()`: Get API usage limits
- `_make_request()`: Internal method for HTTP requests

### 2. OpenRouterModels

Model discovery and management operations.

```python
models = OpenRouterModels(client)

# List all models
all_models = models.list_models()

# Get only free models
free_models = models.get_free_models()

# Search for models
llama_models = models.find_model("llama", tier=ModelTier.FREE)

# Get model info
info = models.get_model_info("meta-llama/llama-3.1-8b-instruct:free")

# Get recommended model
rec = models.get_recommended_free_model("coding")
```

**Methods:**
- `list_models(tier, refresh_cache)`: List models with filtering
- `get_free_models()`: Get free models only
- `find_model(query, tier)`: Search models by name/ID
- `get_model_info(model_id)`: Get detailed model info
- `get_recommended_free_model(use_case)`: Get recommendation for use case

**Model Tiers:**
- `ModelTier.FREE`: Zero-cost models
- `ModelTier.PAID`: Paid models
- `ModelTier.ALL`: All models

**Recommended Models by Use Case:**
- **General**: `meta-llama/llama-3.1-8b-instruct:free`
- **Coding**: `google/gemma-2-9b-it:free`
- **Reasoning**: `microsoft/phi-4:free`
- **Multimodal**: `meta-llama/llama-3.2-11b-vision-instruct:free`

### 3. OpenRouterChat

Chat completion operations with conversation history.

```python
chat = OpenRouterChat(client)

# Simple chat
result = chat.chat(
    message="Hello!",
    model="meta-llama/llama-3.1-8b-instruct:free",
    system_message="You are helpful.",
    use_history=False
)

# Advanced completion
result = chat.create_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[
        {"role": "system", "content": "You are a poet."},
        {"role": "user", "content": "Write a haiku"}
    ],
    temperature=0.7,
    max_tokens=100
)

# Streaming completion
stream = chat.create_streaming_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[{"role": "user", "content": "Tell me a story"}]
)

for chunk in stream:
    print(chunk, end="", flush=True)

# Manage history
chat.get_history()
chat.clear_history()
```

**Methods:**
- `create_completion(...)`: Create chat completion
- `create_streaming_completion(...)`: Stream chat completion
- `chat(message, model, ...)`: Simple chat interface
- `get_history()`: Get conversation history
- `clear_history()`: Clear conversation history

**Parameters:**
- `model`: Model identifier
- `messages`: List of message dicts
- `temperature`: 0-2 (default: 1.0)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Nucleus sampling (default: 1.0)
- `frequency_penalty`: -2 to 2 (default: 0.0)
- `presence_penalty`: -2 to 2 (default: 0.0)
- `stream`: Enable streaming (default: False)

### 4. OpenRouterUtilities

Helper functions for common operations.

```python
utils = OpenRouterUtilities()

# Estimate tokens
tokens = utils.estimate_tokens("Hello, world!", method="simple")

# Format messages
messages = utils.format_messages(
    user_message="Hello",
    system_message="You are helpful",
    history=[...]
)

# Extract content
content = utils.extract_content(response)

# Calculate cost
cost = utils.calculate_cost(
    prompt_tokens=1000,
    completion_tokens=500,
    prompt_price=0.0,
    completion_price=0.0
)

# Collect streaming output without printing
output = utils.collect_streaming_output(stream_iterator)

# Or print and collect streaming output
output = utils.print_streaming_output(stream_iterator, prefix="Bot: ")

# Validate model ID
is_valid = utils.validate_model_id("meta-llama/llama-3.1-8b-instruct:free")

# Check if model is free
is_free = utils.is_free_model(model_info)

# Get error message
error = utils.get_error_message(response)
```

**Static Methods:**
- `estimate_tokens(text, method)`: Estimate token count
- `format_messages(...)`: Format message list
- `extract_content(response)`: Extract text from response
- `calculate_cost(...)`: Calculate API cost
- `collect_streaming_output(iterator)`: Collect stream to string (no printing)
- `print_streaming_output(iterator, prefix)`: Print and collect stream to string
- `validate_model_id(model_id)`: Validate model ID format
- `is_free_model(model_info)`: Check if model is free
- `get_error_message(response)`: Extract error message

## 🔌 OpenAI Function Calling Integration

The SDK includes pre-defined OpenAI function definitions for agent integration.

```python
from tools.openrouter_sdk import OPENAI_FUNCTIONS
import openai

client = openai.OpenAI()

# Use functions in completion
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "user", "content": "Find free OpenRouter models for coding"}
    ],
    tools=OPENAI_FUNCTIONS,
    tool_choice="auto"
)

# Handle function calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Execute function
        if function_name == "get_free_models":
            result = models.get_free_models()
        elif function_name == "find_model":
            result = models.find_model(**arguments)
        # ... handle other functions
```

**Available Functions:**
1. `list_openrouter_models`: List models with tier filtering
2. `get_free_models`: Get free models
3. `find_model`: Search for models
4. `chat_completion`: Create chat completion
5. `estimate_tokens`: Estimate token count
6. `get_recommended_model`: Get recommendation by use case

## 💡 Examples

### Example 1: List Free Models

```python
from tools.openrouter_sdk import OpenRouterClient, OpenRouterModels

client = OpenRouterClient()
models = OpenRouterModels(client)

# Get all free models
result = models.get_free_models()

print(f"Found {result['count']} free models:")
for model in result['models'][:5]:
    print(f"  - {model['id']}")
    print(f"    Context: {model.get('context_length', 'N/A')} tokens")
```

### Example 2: Simple Chat

```python
from tools.openrouter_sdk import OpenRouterClient, OpenRouterChat

client = OpenRouterClient()
chat = OpenRouterChat(client)

result = chat.chat(
    message="Explain quantum computing in one sentence.",
    model="meta-llama/llama-3.1-8b-instruct:free",
    system_message="You are a physics expert. Be concise."
)

if result["success"]:
    print(result["message"]["content"])
```

### Example 3: Conversation with History

```python
from tools.openrouter_sdk import OpenRouterClient, OpenRouterChat

client = OpenRouterClient()
chat = OpenRouterChat(client)

# Turn 1
chat.chat(
    message="My favorite color is blue.",
    model="meta-llama/llama-3.1-8b-instruct:free",
    use_history=False
)

# Turn 2 - remembers previous context
result = chat.chat(
    message="What is my favorite color?",
    model="meta-llama/llama-3.1-8b-instruct:free",
    use_history=True
)

print(result["message"]["content"])  # Should mention blue
```

### Example 4: Streaming Response

```python
from tools.openrouter_sdk import OpenRouterClient, OpenRouterChat

client = OpenRouterClient()
chat = OpenRouterChat(client)

print("Response: ", end="", flush=True)

stream = chat.create_streaming_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[
        {"role": "user", "content": "Write a short poem about coding"}
    ]
)

for chunk in stream:
    print(chunk, end="", flush=True)

print()  # New line
```

### Example 5: Token Estimation and Cost

```python
from tools.openrouter_sdk import OpenRouterUtilities

utils = OpenRouterUtilities()

# Estimate tokens
text = "This is my prompt that I want to send to the API."
tokens = utils.estimate_tokens(text)
print(f"Estimated tokens: {tokens}")

# Calculate cost (free model = $0)
cost = utils.calculate_cost(
    prompt_tokens=tokens,
    completion_tokens=100,
    prompt_price=0.0,
    completion_price=0.0
)

print(f"Total cost: ${cost['total_cost']:.4f}")
```

### Example 6: Advanced Parameters

```python
from tools.openrouter_sdk import OpenRouterClient, OpenRouterChat

client = OpenRouterClient()
chat = OpenRouterChat(client)

# Creative writing (high temperature)
creative = chat.create_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[{"role": "user", "content": "Write a unique story opening"}],
    temperature=1.5,
    max_tokens=100,
    top_p=0.9
)

# Factual response (low temperature)
factual = chat.create_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    temperature=0.1,
    max_tokens=50
)
```

## 🆓 Free Models (2024-2025)

The SDK includes built-in support for discovering and using free models:

### Top Free Models

1. **Meta LLaMA 3.1 8B Instruct** (`meta-llama/llama-3.1-8b-instruct:free`)
   - Best for: General purpose, conversational AI
   - Context: 128K tokens

2. **Google Gemma 2 9B IT** (`google/gemma-2-9b-it:free`)
   - Best for: Code generation, technical tasks
   - Context: 8K tokens

3. **Microsoft Phi-4** (`microsoft/phi-4:free`)
   - Best for: Reasoning, math, logic
   - Context: 16K tokens

4. **Meta LLaMA 3.2 11B Vision** (`meta-llama/llama-3.2-11b-vision-instruct:free`)
   - Best for: Multimodal (text + images)
   - Context: 128K tokens

### Finding Free Models

```python
# Get all free models
free_models = models.get_free_models()

# Search for specific free models
llama_free = models.find_model("llama", tier=ModelTier.FREE)

# Get recommendation
coding_model = models.get_recommended_free_model("coding")
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export OPENROUTER_API_KEY='your-api-key-here'

# Optional - for openrouter_lookup.py compatibility
export OPENROUTER_MODEL='meta-llama/llama-3.1-8b-instruct:free'
export OPENROUTER_SUMMARY_MODEL='google/gemma-2-9b-it:free'
```

### Client Configuration

```python
client = OpenRouterClient(
    api_key="your-key",      # Override env variable
    timeout=120,              # Request timeout (seconds)
    max_retries=3,            # Number of retry attempts
    retry_delay=2             # Initial retry delay (seconds)
)
```

## 🔒 Error Handling

All methods return consistent response format:

```python
{
    "success": True/False,
    "error": "error message",     # If success=False
    "error_type": "ExceptionType" # If success=False
    # ... other fields if success=True
}
```

Example error handling:

```python
result = chat.chat(message="Hello", model="invalid-model")

if not result["success"]:
    error = OpenRouterUtilities.get_error_message(result)
    print(f"Error: {error}")
else:
    content = OpenRouterUtilities.extract_content(result)
    print(f"Response: {content}")
```

## 🧪 Testing

Run the example script to test all features:

```bash
# Set API key
export OPENROUTER_API_KEY='your-key'

# Run examples
python examples/example_openrouter_sdk.py
```

The example script includes:
1. Model listing and filtering
2. Simple chat completions
3. Conversation history
4. Streaming responses
5. Utility functions
6. Advanced parameters

## 📊 Performance Tips

1. **Use Free Models**: Zero cost for experimentation
2. **Enable Caching**: Model list is cached for 1 hour
3. **Estimate Tokens First**: Avoid unexpected costs
4. **Use Streaming**: Better UX for long responses
5. **Set Max Tokens**: Control response length and cost
6. **Adjust Temperature**: Lower for factual, higher for creative

## 🔄 Migration from OpenAI

The SDK is designed to be OpenAI-compatible:

```python
# OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# OpenRouter SDK
from tools.openrouter_sdk import OpenRouterClient, OpenRouterChat
client = OpenRouterClient()
chat = OpenRouterChat(client)
response = chat.create_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 📝 Best Practices

1. **Always Check Success**: Verify `result["success"]` before using data
2. **Use Type Hints**: Import types for better IDE support
3. **Handle Errors Gracefully**: Use utility functions for error extraction
4. **Clear History**: Call `clear_history()` for new conversations
5. **Validate Model IDs**: Use `validate_model_id()` before requests
6. **Estimate Before Sending**: Check token counts for large prompts
7. **Use Recommended Models**: Start with `get_recommended_free_model()`

## 🛠️ Advanced Usage

### Custom Retry Logic

```python
client = OpenRouterClient(
    max_retries=5,
    retry_delay=3
)
```

### Conversation Management

```python
# Start conversation
chat = OpenRouterChat(client)

# Add messages
chat.chat("Hello", use_history=False)
chat.chat("How are you?", use_history=True)

# View history
history = chat.get_history()
print(f"Messages: {history['count']}")

# Clear for new conversation
chat.clear_history()
```

### Model Comparison

```python
models = OpenRouterModels(client)

# Compare free vs paid models
free = models.list_models(tier=ModelTier.FREE)
paid = models.list_models(tier=ModelTier.PAID)

print(f"Free models: {free['count']}")
print(f"Paid models: {paid['count']}")
```

## 🐛 Troubleshooting

### API Key Issues

```python
# Check if key is set
import os
if not os.environ.get("OPENROUTER_API_KEY"):
    print("Please set OPENROUTER_API_KEY")
```

### Timeout Errors

```python
# Increase timeout for slow connections
client = OpenRouterClient(timeout=300)
```

### Model Not Found

```python
# Validate model ID
utils = OpenRouterUtilities()
if not utils.validate_model_id(model_id):
    print("Invalid model ID format")

# Check if model exists
info = models.get_model_info(model_id)
if not info["success"]:
    print(f"Model not found: {model_id}")
```

## 📚 API Reference

See inline documentation in `tools/openrouter_sdk.py` for complete API reference.

## 🤝 Contributing

Improvements welcome! Follow the existing OOP patterns and include:
- Type hints
- Docstrings
- Error handling
- Example usage

## 📄 License

See main repository LICENSE file.

---

**Version**: 1.0.0  
**Last Updated**: 2024-12-27  
**Author**: CBW Agents
