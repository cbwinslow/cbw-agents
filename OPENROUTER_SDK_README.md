# OpenRouter SDK - Quick Reference

## Installation

```bash
pip install requests
export OPENROUTER_API_KEY='your-key-here'
```

## Quick Start

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

# Get free models
free_models = models.get_free_models()
print(f"Found {free_models['count']} free models")

# Simple chat
result = chat.chat(
    message="What is Python?",
    model="meta-llama/llama-3.1-8b-instruct:free"
)
print(result["message"]["content"])

# Streaming chat
stream = chat.create_streaming_completion(
    model="meta-llama/llama-3.1-8b-instruct:free",
    messages=[{"role": "user", "content": "Tell me a joke"}]
)

for chunk in stream:
    print(chunk, end="", flush=True)
```

## Common Use Cases

### 1. Find Free Coding Models
```python
result = models.find_model("gemma", tier=ModelTier.FREE)
```

### 2. Multi-Turn Conversation
```python
chat.chat("My name is Alice", use_history=False)
response = chat.chat("What is my name?", use_history=True)
```

### 3. Estimate Tokens
```python
tokens = utils.estimate_tokens("This is my prompt")
```

### 4. Get Recommended Model
```python
rec = models.get_recommended_free_model("coding")
print(rec["model_id"])
```

## Files

- **SDK**: `tools/openrouter_sdk.py`
- **Guide**: `OPENROUTER_SDK_GUIDE.md`
- **Examples**: `examples/example_openrouter_sdk.py`
- **Function Calling**: `examples/example_openrouter_function_calling.py`
- **Agent Config**: `agents/openrouter_agent.json`
- **Implementation Summary**: `OPENROUTER_SDK_IMPLEMENTATION.md`

## Classes

1. **OpenRouterClient** - API client with retry logic
2. **OpenRouterModels** - Model discovery and management
3. **OpenRouterChat** - Chat completions and streaming
4. **OpenRouterUtilities** - Helper functions

## Free Models (Recommended)

- **General**: `meta-llama/llama-3.1-8b-instruct:free`
- **Coding**: `google/gemma-2-9b-it:free`
- **Reasoning**: `microsoft/phi-4:free`
- **Multimodal**: `meta-llama/llama-3.2-11b-vision-instruct:free`

## OpenAI Function Integration

```python
from tools.openrouter_sdk import OPENAI_FUNCTIONS

# Use with OpenAI
response = openai_client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Find free models"}],
    tools=OPENAI_FUNCTIONS
)
```

## Run Examples

```bash
# Set API key
export OPENROUTER_API_KEY='your-key'

# Run main examples
cd examples
python example_openrouter_sdk.py

# Run function calling demo
python example_openrouter_function_calling.py
```

## Documentation

For complete documentation, see:
- **User Guide**: `OPENROUTER_SDK_GUIDE.md`
- **Implementation Details**: `OPENROUTER_SDK_IMPLEMENTATION.md`

## Support

- Access 400+ AI models through unified API
- Focus on free models to minimize costs
- Full streaming support
- Conversation history management
- OpenAI-compatible function calling
- Comprehensive error handling

---

**Version**: 1.0.0 | **Status**: Production Ready | **Security**: Verified ✅
