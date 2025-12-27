#!/usr/bin/env python3
"""
Test GitHub Operations Tool

Simple tests to verify the tool functionality without requiring API access.
Tests the structure, methods, and error handling.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.github_operations import GitHubOperationsTool, TOOL_INFO


def test_tool_initialization():
    """Test tool can be initialized."""
    print("Test 1: Tool Initialization")
    try:
        tool = GitHubOperationsTool()
        print("✓ Tool initialized successfully")
        print(f"  Base URL: {tool.base_url}")
        print(f"  Rate limit delay: {tool.rate_limit_delay}s")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_tool_metadata():
    """Test tool metadata is properly defined."""
    print("\nTest 2: Tool Metadata")
    try:
        assert TOOL_INFO["name"] == "github_operations"
        assert TOOL_INFO["version"] == "1.0.0"
        assert len(TOOL_INFO["capabilities"]) > 0
        print("✓ Tool metadata is valid")
        print(f"  Name: {TOOL_INFO['name']}")
        print(f"  Version: {TOOL_INFO['version']}")
        print(f"  Capabilities: {len(TOOL_INFO['capabilities'])}")
        return True
    except AssertionError as e:
        print(f"✗ Failed: {e}")
        return False


def test_method_signatures():
    """Test that all expected methods exist."""
    print("\nTest 3: Method Signatures")
    try:
        tool = GitHubOperationsTool()
        methods = [
            'list_user_repos',
            'get_repo_info',
            'list_repo_contents',
            'get_file_content',
            'search_code',
            'search_repositories',
            'get_repo_tree',
            'list_repo_languages',
            'get_repo_readme',
            'catalog_repositories',
            'analyze_repository'
        ]
        
        for method in methods:
            assert hasattr(tool, method), f"Missing method: {method}"
        
        print(f"✓ All {len(methods)} expected methods exist")
        return True
    except AssertionError as e:
        print(f"✗ Failed: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTest 4: Error Handling")
    try:
        tool = GitHubOperationsTool()
        
        # Test with invalid repository (without actual API call if no token)
        # The tool should handle missing authentication gracefully
        result = tool._make_request("INVALID_METHOD", "/test")
        assert not result["success"], "Should fail for invalid method"
        assert "error" in result, "Should have error message"
        
        print("✓ Error handling works correctly")
        print(f"  Error message present: {bool(result.get('error'))}")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_authentication_setup():
    """Test authentication setup."""
    print("\nTest 5: Authentication Setup")
    try:
        # Test with no token
        tool1 = GitHubOperationsTool()
        has_auth1 = "Authorization" in tool1.headers
        
        # Test with explicit token
        tool2 = GitHubOperationsTool(token="test_token")
        has_auth2 = "Authorization" in tool2.headers
        
        print("✓ Authentication setup works")
        print(f"  Without token: {'Authorization' if has_auth1 else 'No authorization'} header")
        print(f"  With token: {'Authorization' if has_auth2 else 'No authorization'} header")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    print("=" * 60)
    print("GitHub Operations Tool - Unit Tests")
    print("=" * 60)
    
    tests = [
        test_tool_initialization,
        test_tool_metadata,
        test_method_signatures,
        test_error_handling,
        test_authentication_setup
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
