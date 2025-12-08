"""
Example: Web Browsing Tool Usage
Demonstrates basic and advanced web browsing capabilities.
"""

import sys
sys.path.append('..')

from tools.web_browsing import WebBrowsingTool
import json

def main():
    print("=== Web Browsing Tool Example ===\n")
    
    # Initialize the tool
    browser = WebBrowsingTool(timeout=30)
    
    # Example 1: Basic browsing
    print("Example 1: Browse a URL")
    print("-" * 50)
    result = browser.browse_url("https://example.com", extract_content=True)
    
    if result["success"]:
        print(f"✓ Successfully browsed: {result['url']}")
        print(f"  Title: {result['title']}")
        print(f"  Main content preview: {result['main_content'][:100]}...")
        print(f"  Links found: {len(result['links'])}")
        print(f"  Images found: {len(result['images'])}")
    else:
        print(f"✗ Error: {result['error']}")
    
    print("\n")
    
    # Example 2: Get page structure
    print("Example 2: Analyze page structure")
    print("-" * 50)
    structure = browser.get_page_structure()
    
    if structure["success"]:
        print(f"✓ Page structure extracted")
        if structure["headings"]:
            print(f"  Headings:")
            for level, headings in structure["headings"].items():
                print(f"    {level}: {len(headings)} found")
        print(f"  Forms: {len(structure['forms'])}")
        print(f"  Tables: {len(structure['tables'])}")
    
    print("\n")
    
    # Example 3: Search within page
    print("Example 3: Search page content")
    print("-" * 50)
    search_result = browser.search_page("example")
    
    if search_result["success"]:
        print(f"✓ Search completed")
        print(f"  Query: '{search_result['query']}'")
        print(f"  Occurrences: {search_result['occurrences']}")
        if search_result['contexts']:
            print(f"  Sample context: {search_result['contexts'][0][:100]}...")
    
    print("\n")
    
    # Example 4: View browsing history
    print("Example 4: Browsing history")
    print("-" * 50)
    history = browser.get_history()
    
    if history["success"]:
        print(f"✓ History retrieved")
        print(f"  Pages visited: {history['count']}")
        for i, entry in enumerate(history['history'][-3:], 1):
            print(f"  {i}. {entry['url']} (Status: {entry['status_code']})")
    
    print("\n")
    print("=== Example Complete ===")

if __name__ == "__main__":
    main()
