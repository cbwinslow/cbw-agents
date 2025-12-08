"""
Example: OpenAI Function Calling Integration
Demonstrates how to integrate tools with OpenAI's function calling API.
"""

import sys
sys.path.append('..')

from tools.web_browsing import WebBrowsingTool, OPENAI_FUNCTIONS as WEB_FUNCTIONS
from tools.file_downloader import FileDownloaderTool, OPENAI_FUNCTIONS as DOWNLOAD_FUNCTIONS
import json

def main():
    print("=== OpenAI Function Calling Integration Example ===\n")
    
    # Initialize tools
    browser = WebBrowsingTool()
    downloader = FileDownloaderTool()
    
    # Combine function definitions
    all_functions = WEB_FUNCTIONS + DOWNLOAD_FUNCTIONS
    
    print("Available Functions:")
    print("-" * 50)
    for func_def in all_functions:
        func = func_def["function"]
        print(f"  • {func['name']}: {func['description']}")
    
    print("\n")
    
    # Function router
    def execute_function(name, args):
        """Route function calls to appropriate tool methods"""
        
        # Web browsing functions
        if name == "browse_url":
            return browser.browse_url(**args)
        elif name == "click_link":
            return browser.click_link(**args)
        elif name == "search_page":
            return browser.search_page(**args)
        elif name == "get_page_structure":
            return browser.get_page_structure()
        elif name == "get_history":
            return browser.get_history()
        
        # File downloader functions
        elif name == "download_file":
            return downloader.download_file(**args)
        elif name == "get_file_info":
            return downloader.get_file_info(**args)
        elif name == "list_downloads":
            return downloader.list_downloads()
        
        return {"success": False, "error": f"Unknown function: {name}"}
    
    # Example function calls (simulating OpenAI responses)
    print("Example Function Calls:")
    print("-" * 50)
    
    # 1. Browse URL
    print("\n1. Calling: browse_url")
    result = execute_function("browse_url", {
        "url": "https://example.com",
        "extract_content": True
    })
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Title: {result['title']}")
    
    # 2. Get file info
    print("\n2. Calling: get_file_info")
    result = execute_function("get_file_info", {
        "url": "https://example.com/sample.pdf"
    })
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   File size: {result.get('size_mb', 'unknown')} MB")
    
    # 3. List downloads
    print("\n3. Calling: list_downloads")
    result = execute_function("list_downloads", {})
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Files in downloads: {result['file_count']}")
    
    print("\n")
    
    # Show OpenAI integration template
    print("OpenAI Integration Template:")
    print("-" * 50)
    print("""
import openai

client = openai.OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "user", "content": "Browse https://example.com"}
    ],
    tools=all_functions,  # Use our combined functions
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        result = execute_function(function_name, arguments)
        print(result)
    """)
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()
