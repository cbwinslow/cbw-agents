"""
Example: OpenRouter SDK Usage
Demonstrates how to use the OpenRouter SDK suite with free models.
"""

import sys
import os
sys.path.append('..')

from tools.openrouter_sdk import (
    OpenRouterClient,
    OpenRouterModels,
    OpenRouterChat,
    OpenRouterUtilities,
    ModelTier
)


def example_list_models():
    """Example: List and filter models"""
    print("=" * 60)
    print("Example 1: Listing and Filtering Models")
    print("=" * 60)
    
    client = OpenRouterClient()
    models = OpenRouterModels(client)
    
    # Get free models
    print("\n1. Getting free models...")
    result = models.get_free_models()
    if result["success"]:
        print(f"   ✓ Found {result['count']} free models")
        
        # Show first 5
        print("\n   First 5 free models:")
        for i, model in enumerate(result["models"][:5], 1):
            print(f"   {i}. {model['id']}")
            print(f"      Name: {model.get('name', 'N/A')}")
            print(f"      Context: {model.get('context_length', 'N/A')} tokens")
    else:
        print(f"   ✗ Error: {result.get('error')}")
    
    # Search for specific models
    print("\n2. Searching for 'llama' models...")
    result = models.find_model("llama", tier=ModelTier.FREE)
    if result["success"]:
        print(f"   ✓ Found {result['count']} matching models")
        for i, model in enumerate(result["models"][:3], 1):
            print(f"   {i}. {model['id']}")
    else:
        print(f"   ✗ Error: {result.get('error')}")
    
    # Get recommended model
    print("\n3. Getting recommended models by use case...")
    for use_case in ["general", "coding", "reasoning"]:
        rec = models.get_recommended_free_model(use_case)
        print(f"   {use_case.capitalize()}: {rec['model_id']}")


def example_simple_chat():
    """Example: Simple chat completion"""
    print("\n" + "=" * 60)
    print("Example 2: Simple Chat Completion")
    print("=" * 60)
    
    client = OpenRouterClient()
    chat = OpenRouterChat(client)
    
    # Simple chat
    print("\n1. Simple chat with free model...")
    result = chat.chat(
        message="What is Python? Answer in one sentence.",
        model="meta-llama/llama-3.1-8b-instruct:free",
        system_message="You are a helpful assistant. Be concise."
    )
    
    if result["success"]:
        content = OpenRouterUtilities.extract_content(result)
        print(f"   ✓ Response: {content}")
        
        usage = result.get("usage", {})
        print(f"\n   Usage:")
        print(f"   - Prompt tokens: {usage.get('prompt_tokens', 0)}")
        print(f"   - Completion tokens: {usage.get('completion_tokens', 0)}")
        print(f"   - Total tokens: {usage.get('total_tokens', 0)}")
    else:
        print(f"   ✗ Error: {result.get('error')}")


def example_conversation_history():
    """Example: Conversation with history"""
    print("\n" + "=" * 60)
    print("Example 3: Conversation with History")
    print("=" * 60)
    
    client = OpenRouterClient()
    chat = OpenRouterChat(client)
    
    print("\n1. Multi-turn conversation...")
    
    # Turn 1
    print("\n   User: What is 2+2?")
    result = chat.chat(
        message="What is 2+2?",
        model="meta-llama/llama-3.1-8b-instruct:free",
        use_history=False
    )
    
    if result["success"]:
        content = OpenRouterUtilities.extract_content(result)
        print(f"   Assistant: {content}")
    
    # Turn 2 - with history
    print("\n   User: Multiply that by 3")
    result = chat.chat(
        message="Multiply that by 3",
        model="meta-llama/llama-3.1-8b-instruct:free",
        use_history=True
    )
    
    if result["success"]:
        content = OpenRouterUtilities.extract_content(result)
        print(f"   Assistant: {content}")
    
    # Show history
    history = chat.get_history()
    print(f"\n   ✓ Conversation history has {history['count']} messages")


def example_streaming_chat():
    """Example: Streaming chat completion"""
    print("\n" + "=" * 60)
    print("Example 4: Streaming Chat Completion")
    print("=" * 60)
    
    client = OpenRouterClient()
    chat = OpenRouterChat(client)
    
    print("\n1. Streaming response...")
    print("   User: Write a haiku about programming")
    print("   Assistant: ", end="", flush=True)
    
    try:
        stream = chat.create_streaming_completion(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a poet."},
                {"role": "user", "content": "Write a haiku about programming"}
            ]
        )
        
        output = OpenRouterUtilities.print_streaming_output(stream)
        print(f"\n   ✓ Streamed {len(output)} characters")
    except Exception as e:
        print(f"\n   ✗ Error: {e}")


def example_utilities():
    """Example: Utility functions"""
    print("\n" + "=" * 60)
    print("Example 5: Utility Functions")
    print("=" * 60)
    
    utils = OpenRouterUtilities()
    
    # Token estimation
    print("\n1. Token estimation...")
    texts = [
        "Hello, world!",
        "This is a longer message with more words and content.",
        "A" * 1000  # 1000 characters
    ]
    
    for text in texts:
        tokens = utils.estimate_tokens(text)
        print(f"   Text length: {len(text)} chars → ~{tokens} tokens")
    
    # Cost calculation
    print("\n2. Cost calculation...")
    cost = utils.calculate_cost(
        prompt_tokens=1000,
        completion_tokens=500,
        prompt_price=0.0,  # Free model
        completion_price=0.0
    )
    print(f"   Prompt tokens: {cost['prompt_tokens']}")
    print(f"   Completion tokens: {cost['completion_tokens']}")
    print(f"   Total cost: ${cost['total_cost']:.4f}")
    
    # Message formatting
    print("\n3. Message formatting...")
    messages = utils.format_messages(
        user_message="Hello!",
        system_message="You are helpful.",
        history=[
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
    )
    print(f"   ✓ Formatted {len(messages)} messages")
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. {msg['role']}: {msg['content'][:30]}...")
    
    # Model validation
    print("\n4. Model ID validation...")
    test_ids = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "invalid-model",
        "google/gemma-2-9b-it:free"
    ]
    
    for model_id in test_ids:
        valid = utils.validate_model_id(model_id)
        status = "✓" if valid else "✗"
        print(f"   {status} {model_id}: {'Valid' if valid else 'Invalid'}")


def example_advanced_completion():
    """Example: Advanced completion with parameters"""
    print("\n" + "=" * 60)
    print("Example 6: Advanced Completion Parameters")
    print("=" * 60)
    
    client = OpenRouterClient()
    chat = OpenRouterChat(client)
    
    print("\n1. Testing different temperature settings...")
    
    prompt = "Complete this sentence: The future of AI is"
    
    for temp in [0.3, 0.7, 1.5]:
        print(f"\n   Temperature: {temp}")
        result = chat.create_completion(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=50
        )
        
        if result["success"]:
            content = OpenRouterUtilities.extract_content(result)
            print(f"   Response: {content[:100]}...")
        else:
            print(f"   Error: {result.get('error')}")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "OpenRouter SDK Usage Examples" + " " * 18 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Check for API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\n⚠️  WARNING: OPENROUTER_API_KEY environment variable not set")
        print("   Please set it to run these examples:")
        print("   export OPENROUTER_API_KEY='your-key-here'")
        print("\n   Continuing with limited examples...\n")
        
        # Show utility examples that don't require API
        example_utilities()
        return
    
    try:
        # Run examples
        example_list_models()
        example_simple_chat()
        example_conversation_history()
        example_streaming_chat()
        example_utilities()
        example_advanced_completion()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
