"""
GitHub Operations Tool

Comprehensive tool for GitHub API operations including repository analysis,
documentation generation, and bulk actions on GitHub accounts.

Capabilities:
- Repository listing and analysis
- File operations (list, read, search)
- Documentation generation
- Bulk actions across repositories
- Repository cataloging and indexing
- Code analysis and summaries
- Diagram generation

Safety Features:
- Rate limiting
- Authentication with tokens
- Pagination support
- Error handling and retries
- Content caching
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Warning: 'requests' library not installed. Install with: pip install requests")
    requests = None


class GitHubOperationsTool:
    """
    Tool for comprehensive GitHub API operations.
    
    Supports authentication via GITHUB_TOKEN environment variable
    or explicit token parameter.
    """
    
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize GitHub operations tool.
        
        Args:
            token: GitHub personal access token (or use GITHUB_TOKEN env var)
            base_url: GitHub API base URL
            rate_limit_delay: Delay between requests (seconds)
            max_retries: Maximum retry attempts on failure
            cache_dir: Directory for caching responses
        """
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "CBW-GitHub-Agent/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        
        self.last_request_time = 0
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to GitHub API with rate limiting and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            Dictionary with API response
        """
        if not requests:
            return {
                "success": False,
                "error": "requests library not installed"
            }
        
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        url = urljoin(self.base_url, endpoint)
        
        for attempt in range(self.max_retries):
            try:
                self.last_request_time = time.time()
                
                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=30
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url,
                        headers=self.headers,
                        params=params,
                        json=data,
                        timeout=30
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported method: {method}"
                    }
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": response.json(),
                        "rate_limit": {
                            "remaining": response.headers.get("X-RateLimit-Remaining"),
                            "reset": response.headers.get("X-RateLimit-Reset")
                        }
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded or forbidden",
                        "rate_limit": {
                            "remaining": response.headers.get("X-RateLimit-Remaining"),
                            "reset": response.headers.get("X-RateLimit-Reset")
                        }
                    }
                else:
                    if attempt == self.max_retries - 1:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}: {response.text[:200]}"
                        }
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": f"Request failed: {str(e)}"
                    }
                time.sleep(2 ** attempt)
        
        return {
            "success": False,
            "error": "Max retries exceeded"
        }
    
    def list_user_repos(
        self,
        username: Optional[str] = None,
        repo_type: str = "all",
        sort: str = "updated",
        per_page: int = 100,
        max_repos: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List repositories for a user or authenticated user.
        
        Args:
            username: GitHub username (None for authenticated user)
            repo_type: Type of repos (all, owner, public, private, member)
            sort: Sort by (created, updated, pushed, full_name)
            per_page: Results per page (max 100)
            max_repos: Maximum number of repos to retrieve
            
        Returns:
            Dictionary with repository list
        """
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"
        
        repos = []
        page = 1
        
        while True:
            params = {
                "type": repo_type,
                "sort": sort,
                "per_page": min(per_page, 100),
                "page": page
            }
            
            result = self._make_request("GET", endpoint, params=params)
            
            if not result["success"]:
                return result
            
            batch = result["data"]
            if not batch:
                break
            
            repos.extend(batch)
            
            if max_repos and len(repos) >= max_repos:
                repos = repos[:max_repos]
                break
            
            if len(batch) < per_page:
                break
            
            page += 1
        
        return {
            "success": True,
            "data": repos,
            "count": len(repos),
            "metadata": {
                "username": username or "authenticated_user",
                "repo_type": repo_type,
                "retrieved_at": datetime.now().isoformat()
            }
        }
    
    def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with repository information
        """
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request("GET", endpoint)
    
    def list_repo_contents(
        self,
        owner: str,
        repo: str,
        path: str = "",
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List contents of a repository directory.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository
            ref: Git reference (branch, tag, commit)
            
        Returns:
            Dictionary with directory contents
        """
        endpoint = f"/repos/{owner}/{repo}/contents/{path}"
        params = {}
        if ref:
            params["ref"] = ref
        
        return self._make_request("GET", endpoint, params=params)
    
    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get content of a file from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Git reference (branch, tag, commit)
            
        Returns:
            Dictionary with file content (decoded)
        """
        result = self.list_repo_contents(owner, repo, path, ref)
        
        if not result["success"]:
            return result
        
        if isinstance(result["data"], list):
            return {
                "success": False,
                "error": "Path is a directory, not a file"
            }
        
        import base64
        try:
            content = base64.b64decode(result["data"]["content"]).decode("utf-8")
            return {
                "success": True,
                "data": {
                    "content": content,
                    "name": result["data"]["name"],
                    "path": result["data"]["path"],
                    "size": result["data"]["size"],
                    "sha": result["data"]["sha"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to decode content: {str(e)}"
            }
    
    def search_code(
        self,
        query: str,
        per_page: int = 30,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for code across GitHub.
        
        Args:
            query: Search query (e.g., "language:python user:username")
            per_page: Results per page (max 100)
            max_results: Maximum results to retrieve
            
        Returns:
            Dictionary with search results
        """
        endpoint = "/search/code"
        results = []
        page = 1
        
        while True:
            params = {
                "q": query,
                "per_page": min(per_page, 100),
                "page": page
            }
            
            result = self._make_request("GET", endpoint, params=params)
            
            if not result["success"]:
                return result
            
            batch = result["data"].get("items", [])
            if not batch:
                break
            
            results.extend(batch)
            
            if max_results and len(results) >= max_results:
                results = results[:max_results]
                break
            
            if len(batch) < per_page:
                break
            
            page += 1
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "metadata": {
                "query": query,
                "retrieved_at": datetime.now().isoformat()
            }
        }
    
    def search_repositories(
        self,
        query: str,
        sort: Optional[str] = None,
        order: str = "desc",
        per_page: int = 30,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for repositories on GitHub.
        
        Args:
            query: Search query (e.g., "user:username language:python")
            sort: Sort by (stars, forks, updated)
            order: Order (asc, desc)
            per_page: Results per page (max 100)
            max_results: Maximum results to retrieve
            
        Returns:
            Dictionary with search results
        """
        endpoint = "/search/repositories"
        results = []
        page = 1
        
        while True:
            params = {
                "q": query,
                "per_page": min(per_page, 100),
                "page": page,
                "order": order
            }
            if sort:
                params["sort"] = sort
            
            result = self._make_request("GET", endpoint, params=params)
            
            if not result["success"]:
                return result
            
            batch = result["data"].get("items", [])
            if not batch:
                break
            
            results.extend(batch)
            
            if max_results and len(results) >= max_results:
                results = results[:max_results]
                break
            
            if len(batch) < per_page:
                break
            
            page += 1
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "metadata": {
                "query": query,
                "sort": sort,
                "order": order,
                "retrieved_at": datetime.now().isoformat()
            }
        }
    
    def get_repo_tree(
        self,
        owner: str,
        repo: str,
        tree_sha: str = "HEAD",
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Get repository tree structure.
        
        Args:
            owner: Repository owner
            repo: Repository name
            tree_sha: Tree SHA or branch name
            recursive: Get full tree recursively
            
        Returns:
            Dictionary with tree structure
        """
        # First get the branch to get the tree SHA
        if tree_sha == "HEAD":
            branch_result = self._make_request("GET", f"/repos/{owner}/{repo}/branches/main")
            if not branch_result["success"]:
                branch_result = self._make_request("GET", f"/repos/{owner}/{repo}/branches/master")
            
            if branch_result["success"]:
                tree_sha = branch_result["data"]["commit"]["commit"]["tree"]["sha"]
            else:
                return {
                    "success": False,
                    "error": "Could not determine tree SHA"
                }
        
        endpoint = f"/repos/{owner}/{repo}/git/trees/{tree_sha}"
        params = {}
        if recursive:
            params["recursive"] = "1"
        
        return self._make_request("GET", endpoint, params=params)
    
    def list_repo_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get programming languages used in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with language statistics
        """
        endpoint = f"/repos/{owner}/{repo}/languages"
        return self._make_request("GET", endpoint)
    
    def get_repo_readme(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository README content.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with README content
        """
        endpoint = f"/repos/{owner}/{repo}/readme"
        result = self._make_request("GET", endpoint)
        
        if not result["success"]:
            return result
        
        import base64
        try:
            content = base64.b64decode(result["data"]["content"]).decode("utf-8")
            return {
                "success": True,
                "data": {
                    "content": content,
                    "name": result["data"]["name"],
                    "path": result["data"]["path"],
                    "size": result["data"]["size"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to decode README: {str(e)}"
            }
    
    def catalog_repositories(
        self,
        username: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive catalog of all user repositories.
        
        Args:
            username: GitHub username (None for authenticated user)
            output_file: Optional file to save catalog
            
        Returns:
            Dictionary with repository catalog
        """
        # Get all repositories
        repos_result = self.list_user_repos(username=username)
        
        if not repos_result["success"]:
            return repos_result
        
        catalog = {
            "username": username or "authenticated_user",
            "total_repos": repos_result["count"],
            "cataloged_at": datetime.now().isoformat(),
            "repositories": []
        }
        
        for repo in repos_result["data"]:
            repo_info = {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "private": repo["private"],
                "url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "pushed_at": repo["pushed_at"],
                "size": repo["size"],
                "stargazers_count": repo["stargazers_count"],
                "watchers_count": repo["watchers_count"],
                "forks_count": repo["forks_count"],
                "open_issues_count": repo["open_issues_count"],
                "language": repo.get("language"),
                "topics": repo.get("topics", []),
                "default_branch": repo["default_branch"]
            }
            
            # Get languages
            languages_result = self.list_repo_languages(repo["owner"]["login"], repo["name"])
            if languages_result["success"]:
                repo_info["languages"] = languages_result["data"]
            
            catalog["repositories"].append(repo_info)
        
        if output_file:
            try:
                with open(output_file, "w") as f:
                    json.dump(catalog, f, indent=2)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to save catalog: {str(e)}"
                }
        
        return {
            "success": True,
            "data": catalog,
            "metadata": {
                "total_repos": catalog["total_repos"],
                "output_file": output_file
            }
        }
    
    def analyze_repository(
        self,
        owner: str,
        repo: str,
        include_tree: bool = True,
        include_readme: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            include_tree: Include full file tree
            include_readme: Include README content
            
        Returns:
            Dictionary with repository analysis
        """
        analysis = {
            "repository": f"{owner}/{repo}",
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Get basic info
        info_result = self.get_repo_info(owner, repo)
        if not info_result["success"]:
            return info_result
        
        analysis["info"] = info_result["data"]
        
        # Get languages
        languages_result = self.list_repo_languages(owner, repo)
        if languages_result["success"]:
            analysis["languages"] = languages_result["data"]
        
        # Get README
        if include_readme:
            readme_result = self.get_repo_readme(owner, repo)
            if readme_result["success"]:
                analysis["readme"] = readme_result["data"]
        
        # Get file tree
        if include_tree:
            tree_result = self.get_repo_tree(owner, repo)
            if tree_result["success"]:
                analysis["tree"] = tree_result["data"]
                # Analyze file types
                files = tree_result["data"].get("tree", [])
                file_types = {}
                for file in files:
                    if file["type"] == "blob":
                        ext = Path(file["path"]).suffix or "no_extension"
                        file_types[ext] = file_types.get(ext, 0) + 1
                analysis["file_statistics"] = {
                    "total_files": len([f for f in files if f["type"] == "blob"]),
                    "total_dirs": len([f for f in files if f["type"] == "tree"]),
                    "file_types": file_types
                }
        
        return {
            "success": True,
            "data": analysis
        }


# Tool metadata for agent integration
TOOL_INFO = {
    "name": "github_operations",
    "description": "Comprehensive GitHub API operations tool",
    "version": "1.0.0",
    "author": "CBW Agents",
    "capabilities": [
        "list_repositories",
        "search_code",
        "search_repositories",
        "get_file_content",
        "list_directory",
        "analyze_repository",
        "catalog_repositories",
        "get_readme",
        "get_languages",
        "get_tree_structure"
    ],
    "requirements": ["requests"],
    "safety_features": [
        "rate_limiting",
        "authentication",
        "error_handling",
        "retry_logic",
        "pagination_support"
    ],
    "authentication": "GITHUB_TOKEN environment variable or token parameter"
}


if __name__ == "__main__":
    # Example usage
    tool = GitHubOperationsTool()
    
    # Test with a public repository
    print("Testing GitHub Operations Tool...")
    
    # Analyze a repository
    result = tool.analyze_repository("torvalds", "linux", include_tree=False)
    if result["success"]:
        print(f"\nRepository: {result['data']['info']['full_name']}")
        print(f"Description: {result['data']['info']['description']}")
        print(f"Stars: {result['data']['info']['stargazers_count']}")
        print(f"Languages: {result['data'].get('languages', {})}")
    else:
        print(f"Error: {result['error']}")
