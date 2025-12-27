"""
Example: OpenRouter SDK Integration with OpenAI Function Calling
Demonstrates how to integrate the OpenRouter SDK with OpenAI's function calling API.
"""

import sys
import json
sys.path.append('..')

from tools.openrouter_sdk import (
    OpenRouterClient,
    OpenRouterModels,
    OpenRouterChat,
    OpenRouterUtilities,
    OPENAI_FUNCTIONS
)


def create_function_router(client, models, chat, utils):
    """
    Create a function router that handles OpenAI function calls.
    
    Args:
        client: OpenRouterClient instance
        models: OpenRouterModels instance
        chat: OpenRouterChat instance
        utils: OpenRouterUtilities instance
        
    Returns:
        Function that routes and executes function calls
    """
    
    def execute_function(function_name, arguments):
        """Route function calls to appropriate SDK methods"""
        
        try:
            # Model listing and discovery
            if function_name == "list_openrouter_models":
                tier = arguments.get("tier", "all")
                from tools.openrouter_sdk import ModelTier
                tier_enum = ModelTier.FREE if tier == "free" else (
                    ModelTier.PAID if tier == "paid" else ModelTier.ALL
                )
                return models.list_models(tier=tier_enum)
            
            elif function_name == "get_free_models":
                return models.get_free_models()
            
            elif function_name == "find_model":
                query = arguments["query"]
                tier = arguments.get("tier", "all")
                from tools.openrouter_sdk import ModelTier
                tier_enum = ModelTier.FREE if tier == "free" else (
                    ModelTier.PAID if tier == "paid" else ModelTier.ALL
                )
                return models.find_model(query, tier=tier_enum)
            
            # Chat operations
            elif function_name == "chat_completion":
                model = arguments["model"]
                message = arguments["message"]
                system_message = arguments.get("system_message")
                temperature = arguments.get("temperature", 1.0)
                max_tokens = arguments.get("max_tokens")
                
                return chat.chat(
                    message=message,
                    model=model,
                    system_message=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    use_history=False
                )
            
            # Utility operations
            elif function_name == "estimate_tokens":
                text = arguments["text"]
                method = arguments.get("method", "simple")
                tokens = utils.estimate_tokens(text, method)
                return {
                    "success": True,
                    "text_length": len(text),
                    "estimated_tokens": tokens,
                    "method": method
                }
            
            elif function_name == "get_recommended_model":
                use_case = arguments.get("use_case", "general")
                return models.get_recommended_free_model(use_case)
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "function": function_name
            }
    
    return execute_function


def demo_function_calling():
    """Demonstrate function calling integration"""
    
    print("=" * 70)
    print("OpenRouter SDK - OpenAI Function Calling Integration Demo")
    print("=" * 70)
    
    # Check for API key
    import os
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\n⚠️  OPENROUTER_API_KEY not set. Using mock examples only.\n")
        demo_mock_integration()
        return
    
    # Initialize SDK
    client = OpenRouterClient()
    models = OpenRouterModels(client)
    chat = OpenRouterChat(client)
    utils = OpenRouterUtilities()
    
    # Create function router
    execute_function = create_function_router(client, models, chat, utils)
    
    # Example 1: List free models
    print("\n1. Calling function: list_openrouter_models")
    print("   Arguments: {'tier': 'free'}")
    result = execute_function("list_openrouter_models", {"tier": "free"})
    if result["success"]:
        print(f"   ✓ Found {result['count']} free models")
        if result["models"]:
            print(f"   Examples:")
            for model in result["models"][:3]:
                print(f"   - {model['id']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Example 2: Find specific models
    print("\n2. Calling function: find_model")
    print("   Arguments: {'query': 'llama', 'tier': 'free'}")
    result = execute_function("find_model", {"query": "llama", "tier": "free"})
    if result["success"]:
        print(f"   ✓ Found {result['count']} matching models")
        for i, model in enumerate(result["models"][:2], 1):
            print(f"   {i}. {model['id']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Example 3: Estimate tokens
    print("\n3. Calling function: estimate_tokens")
    text = "What is the meaning of life?"
    print(f"   Arguments: {{'text': '{text}'}}")
    result = execute_function("estimate_tokens", {"text": text})
    if result["success"]:
        print(f"   ✓ Estimated tokens: {result['estimated_tokens']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Example 4: Get recommendation
    print("\n4. Calling function: get_recommended_model")
    print("   Arguments: {'use_case': 'coding'}")
    result = execute_function("get_recommended_model", {"use_case": "coding"})
    if result["success"]:
        print(f"   ✓ Recommended: {result['model_id']}")
        print(f"   Use case: {result['use_case']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Example 5: Chat completion
    print("\n5. Calling function: chat_completion")
    print("   Arguments: {")
    print("     'model': 'meta-llama/llama-3.1-8b-instruct:free',")
    print("     'message': 'Say hello in one sentence'")
    print("   }")
    result = execute_function("chat_completion", {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "message": "Say hello in one sentence",
        "system_message": "You are concise."
    })
    if result["success"]:
        content = utils.extract_content(result)
        print(f"   ✓ Response: {content[:100]}...")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    print("\n" + "=" * 70)
    print("✓ Function calling demo complete!")
    print("=" * 70)


def demo_mock_integration():
    """Show mock integration examples without API calls"""
    
    print("\n📋 Mock Integration Examples (No API Key Required)\n")
    
    print("=" * 70)
    print("Example: How to integrate with OpenAI function calling")
    print("=" * 70)
    
    print("""
# 1. Import the SDK
from tools.openrouter_sdk import (
    OpenRouterClient, OpenRouterModels, OpenRouterChat,
    OpenRouterUtilities, OPENAI_FUNCTIONS
)

# 2. Initialize SDK components
client = OpenRouterClient()
models = OpenRouterModels(client)
chat = OpenRouterChat(client)
utils = OpenRouterUtilities()

# 3. Use with OpenAI API
import openai

openai_client = openai.OpenAI(api_key="your-openai-key")

response = openai_client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "user",
            "content": "Find me free AI models for coding tasks"
        }
    ],
    tools=OPENAI_FUNCTIONS,
    tool_choice="auto"
)

# 4. Handle function calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Route to appropriate SDK method
        if function_name == "find_model":
            result = models.find_model(**arguments)
        elif function_name == "chat_completion":
            result = chat.chat(**arguments)
        # ... handle other functions
        
        print(f"Function result: {result}")
""")
    
    print("\n=" * 70)
    print("Available Functions for OpenAI Integration:")
    print("=" * 70)
    
    for i, func_def in enumerate(OPENAI_FUNCTIONS, 1):
        func = func_def["function"]
        print(f"\n{i}. {func['name']}")
        print(f"   Description: {func['description']}")
        params = func.get("parameters", {}).get("properties", {})
        if params:
            print(f"   Parameters:")
            for param_name, param_info in params.items():
                required = param_name in func.get("parameters", {}).get("required", [])
                req_str = " (required)" if required else " (optional)"
                print(f"   - {param_name}{req_str}: {param_info.get('description', 'N/A')}")


def main():
    """Run the integration demo"""
    demo_function_calling()


if __name__ == "__main__":
    main()
