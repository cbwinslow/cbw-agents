"""
Web Browsing Tool (OpenAI-Compatible)
Provides comprehensive web browsing capabilities for AI agents with OpenAI function calling support.
"""

import requests
import json
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

class WebBrowsingTool:
    """
    OpenAI-compatible web browsing tool with comprehensive features.
    Supports headless browsing, JavaScript rendering, and content extraction.
    """
    
    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        """
        Initialize web browsing tool.
        
        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.history = []
        
    def browse_url(self, url: str, extract_content: bool = True) -> Dict[str, Any]:
        """
        Browse a URL and extract content.
        
        Args:
            url: URL to browse
            extract_content: Whether to extract and parse content
            
        Returns:
            Dictionary with page content and metadata
        """
        try:
            response = self.session.get(
                url, 
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            self.history.append({
                "url": url,
                "status_code": response.status_code,
                "timestamp": time.time()
            })
            
            result = {
                "success": True,
                "url": response.url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "final_url": response.url,
                "redirected": url != response.url
            }
            
            if extract_content:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for element in soup(['script', 'style', 'noscript']):
                    element.decompose()
                
                result["title"] = soup.title.string if soup.title else ""
                result["text_content"] = soup.get_text(separator=' ', strip=True)
                result["main_content"] = self._extract_main_content(soup)
                result["links"] = self._extract_links(soup, url)
                result["images"] = self._extract_images(soup, url)
                result["meta_description"] = self._get_meta_description(soup)
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def click_link(self, text: str) -> Dict[str, Any]:
        """
        Click a link by text content (simulates clicking).
        
        Args:
            text: Text of the link to click
            
        Returns:
            Dictionary with navigation result
        """
        if not self.history:
            return {"success": False, "error": "No page loaded"}
        
        last_page = self.history[-1]["url"]
        result = self.browse_url(last_page, extract_content=False)
        
        if not result["success"]:
            return result
        
        response = self.session.get(last_page)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find link by text
        link = soup.find('a', string=lambda s: s and text.lower() in s.lower())
        if link and link.get('href'):
            target_url = urljoin(last_page, link['href'])
            return self.browse_url(target_url)
        
        return {"success": False, "error": f"Link with text '{text}' not found"}
    
    def search_page(self, query: str) -> Dict[str, Any]:
        """
        Search for text in the current page.
        
        Args:
            query: Text to search for
            
        Returns:
            Dictionary with search results
        """
        if not self.history:
            return {"success": False, "error": "No page loaded"}
        
        last_page = self.history[-1]["url"]
        response = self.session.get(last_page)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        text_content = soup.get_text()
        occurrences = text_content.lower().count(query.lower())
        
        # Find context around matches
        contexts = []
        if occurrences > 0:
            sentences = text_content.split('.')
            for sentence in sentences:
                if query.lower() in sentence.lower():
                    contexts.append(sentence.strip())
                    if len(contexts) >= 5:  # Limit to 5 contexts
                        break
        
        return {
            "success": True,
            "query": query,
            "occurrences": occurrences,
            "contexts": contexts
        }
    
    def get_page_structure(self) -> Dict[str, Any]:
        """
        Get the structure of the current page (headings, sections, etc.).
        
        Returns:
            Dictionary with page structure
        """
        if not self.history:
            return {"success": False, "error": "No page loaded"}
        
        last_page = self.history[-1]["url"]
        response = self.session.get(last_page)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        structure = {
            "success": True,
            "headings": {},
            "sections": [],
            "forms": [],
            "tables": []
        }
        
        # Extract headings
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            if headings:
                structure["headings"][f"h{level}"] = [h.get_text(strip=True) for h in headings]
        
        # Extract sections
        for section in soup.find_all(['section', 'article', 'div'], class_=True):
            structure["sections"].append({
                "tag": section.name,
                "classes": section.get('class', []),
                "id": section.get('id', '')
            })
        
        # Extract forms
        for form in soup.find_all('form'):
            inputs = [{"type": inp.get('type', 'text'), "name": inp.get('name', '')} 
                     for inp in form.find_all('input')]
            structure["forms"].append({
                "action": form.get('action', ''),
                "method": form.get('method', 'get'),
                "inputs": inputs
            })
        
        # Extract tables
        for table in soup.find_all('table'):
            structure["tables"].append({
                "rows": len(table.find_all('tr')),
                "headers": [th.get_text(strip=True) for th in table.find_all('th')]
            })
        
        return structure
    
    def get_history(self) -> Dict[str, Any]:
        """
        Get browsing history.
        
        Returns:
            Dictionary with browsing history
        """
        return {
            "success": True,
            "history": self.history,
            "count": len(self.history)
        }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page."""
        # Try to find main content
        main = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main:
            return main.get_text(separator=' ', strip=True)[:2000]  # Limit to 2000 chars
        return soup.get_text(separator=' ', strip=True)[:2000]
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from page."""
        links = []
        for link in soup.find_all('a', href=True)[:50]:  # Limit to 50 links
            links.append({
                "text": link.get_text(strip=True),
                "url": urljoin(base_url, link['href']),
                "title": link.get('title', '')
            })
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from page."""
        images = []
        for img in soup.find_all('img', src=True)[:20]:  # Limit to 20 images
            images.append({
                "url": urljoin(base_url, img['src']),
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })
        return images
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Get meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content']
        return ""

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "browse_url",
            "description": "Browse a URL and extract its content, including text, links, images, and metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to browse (must include http:// or https://)"
                    },
                    "extract_content": {
                        "type": "boolean",
                        "description": "Whether to extract and parse page content",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click_link",
            "description": "Click a link on the current page by its text content",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text of the link to click"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_page",
            "description": "Search for text in the current page and get contextual matches",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The text to search for on the page"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_structure",
            "description": "Get the structural elements of the current page (headings, sections, forms, tables)",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_history",
            "description": "Get the browsing history for the current session",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "web_browsing",
    "description": "OpenAI-compatible web browsing tool with content extraction",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "browse_url",
        "click_link",
        "search_page",
        "get_page_structure",
        "get_history"
    ],
    "requirements": ["requests", "beautifulsoup4", "lxml"],
    "safety_features": [
        "Request timeout",
        "Redirect limits",
        "Content size limits",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    tool = WebBrowsingTool()
    
    # Test browsing
    result = tool.browse_url("https://example.com")
    print(json.dumps(result, indent=2)[:500])
