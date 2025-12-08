"""
Web Crawler Tool (OpenAI-Compatible)
Crawls websites systematically with depth control, URL filtering, and content extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
from collections import deque
import re

class WebCrawlerTool:
    """
    OpenAI-compatible web crawler with depth control and robots.txt compliance.
    Supports systematic crawling, content extraction, and link discovery.
    """
    
    def __init__(self, timeout: int = 30, delay: float = 1.0, max_pages: int = 100):
        """
        Initialize web crawler.
        
        Args:
            timeout: Request timeout in seconds
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to crawl
        """
        self.timeout = timeout
        self.delay = delay
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; WebCrawler/1.0)'
        })
        self.visited_urls: Set[str] = set()
        self.crawl_results: List[Dict] = []
        
    def crawl_site(self, start_url: str, max_depth: int = 2, 
                   same_domain_only: bool = True, respect_robots: bool = True) -> Dict[str, Any]:
        """
        Crawl a website starting from a URL.
        
        Args:
            start_url: Starting URL for the crawl
            max_depth: Maximum depth to crawl
            same_domain_only: Only crawl URLs from the same domain
            respect_robots: Respect robots.txt rules
            
        Returns:
            Dictionary with crawl results
        """
        try:
            self.visited_urls.clear()
            self.crawl_results.clear()
            
            # Parse start URL
            start_domain = urlparse(start_url).netloc
            
            # Check robots.txt if needed
            robot_parser = None
            if respect_robots:
                robot_parser = self._get_robots_parser(start_url)
            
            # Initialize queue with (url, depth) tuples
            queue = deque([(start_url, 0)])
            pages_crawled = 0
            
            while queue and pages_crawled < self.max_pages:
                current_url, depth = queue.popleft()
                
                # Skip if already visited
                if current_url in self.visited_urls:
                    continue
                
                # Skip if max depth exceeded
                if depth > max_depth:
                    continue
                
                # Check robots.txt
                if robot_parser and not robot_parser.can_fetch("*", current_url):
                    continue
                
                # Crawl the page
                page_result = self._crawl_page(current_url)
                
                if page_result["success"]:
                    self.visited_urls.add(current_url)
                    self.crawl_results.append({
                        "url": current_url,
                        "depth": depth,
                        "title": page_result.get("title", ""),
                        "links_found": len(page_result.get("links", [])),
                        "content_length": len(page_result.get("content", "")),
                        "status_code": page_result.get("status_code", 0)
                    })
                    
                    pages_crawled += 1
                    
                    # Add found links to queue
                    if depth < max_depth:
                        for link in page_result.get("links", []):
                            link_url = link["url"]
                            link_domain = urlparse(link_url).netloc
                            
                            # Filter by domain if needed
                            if same_domain_only and link_domain != start_domain:
                                continue
                            
                            if link_url not in self.visited_urls:
                                queue.append((link_url, depth + 1))
                    
                    # Rate limiting
                    time.sleep(self.delay)
            
            # Generate statistics
            total_links = sum(r["links_found"] for r in self.crawl_results)
            avg_links = total_links / len(self.crawl_results) if self.crawl_results else 0
            
            return {
                "success": True,
                "start_url": start_url,
                "pages_crawled": pages_crawled,
                "max_depth_reached": max_depth,
                "total_links_found": total_links,
                "average_links_per_page": round(avg_links, 2),
                "results": self.crawl_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def crawl_sitemap(self, sitemap_url: str) -> Dict[str, Any]:
        """
        Crawl URLs from a sitemap.
        
        Args:
            sitemap_url: URL of the sitemap (XML)
            
        Returns:
            Dictionary with sitemap URLs
        """
        try:
            response = self.session.get(sitemap_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            
            # Find all URL elements
            urls = []
            for loc in soup.find_all('loc'):
                url = loc.get_text(strip=True)
                if url:
                    urls.append(url)
            
            return {
                "success": True,
                "sitemap_url": sitemap_url,
                "urls_found": len(urls),
                "urls": urls
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_broken_links(self, url: str, check_depth: int = 1) -> Dict[str, Any]:
        """
        Find broken links on a website.
        
        Args:
            url: Starting URL
            check_depth: Depth to check for broken links
            
        Returns:
            Dictionary with broken links report
        """
        try:
            # First crawl the site
            crawl_result = self.crawl_site(url, max_depth=check_depth, same_domain_only=True)
            
            if not crawl_result["success"]:
                return crawl_result
            
            broken_links = []
            working_links = []
            
            # Check all discovered URLs
            for result in crawl_result["results"]:
                page_url = result["url"]
                
                # Get links from this page
                page_data = self._crawl_page(page_url)
                if page_data["success"]:
                    for link in page_data.get("links", []):
                        link_url = link["url"]
                        
                        # Check if link works
                        try:
                            head_response = self.session.head(link_url, timeout=5, allow_redirects=True)
                            if head_response.status_code >= 400:
                                broken_links.append({
                                    "url": link_url,
                                    "found_on": page_url,
                                    "status_code": head_response.status_code,
                                    "link_text": link.get("text", "")
                                })
                            else:
                                working_links.append(link_url)
                        except:
                            broken_links.append({
                                "url": link_url,
                                "found_on": page_url,
                                "status_code": "error",
                                "link_text": link.get("text", "")
                            })
                        
                        time.sleep(0.5)  # Rate limiting
            
            return {
                "success": True,
                "start_url": url,
                "total_links_checked": len(broken_links) + len(working_links),
                "broken_links_count": len(broken_links),
                "working_links_count": len(working_links),
                "broken_links": broken_links
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def extract_emails(self, url: str, max_depth: int = 1) -> Dict[str, Any]:
        """
        Extract email addresses from a website.
        
        Args:
            url: Starting URL
            max_depth: Depth to search for emails
            
        Returns:
            Dictionary with extracted emails
        """
        try:
            crawl_result = self.crawl_site(url, max_depth=max_depth, same_domain_only=True)
            
            if not crawl_result["success"]:
                return crawl_result
            
            emails = set()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            
            for result in crawl_result["results"]:
                page_url = result["url"]
                page_data = self._crawl_page(page_url)
                
                if page_data["success"]:
                    content = page_data.get("content", "")
                    found_emails = re.findall(email_pattern, content)
                    emails.update(found_emails)
            
            return {
                "success": True,
                "start_url": url,
                "pages_searched": crawl_result["pages_crawled"],
                "emails_found": len(emails),
                "emails": sorted(list(emails))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _crawl_page(self, url: str) -> Dict[str, Any]:
        """Crawl a single page and extract content."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                # Only include http/https URLs
                if absolute_url.startswith(('http://', 'https://')):
                    links.append({
                        "text": link.get_text(strip=True)[:100],  # Limit text length
                        "url": absolute_url
                    })
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "title": soup.title.string if soup.title else "",
                "content": soup.get_text(separator=' ', strip=True),
                "links": links
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_robots_parser(self, url: str) -> Optional[RobotFileParser]:
        """Get robots.txt parser for a URL."""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp
        except:
            return None

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "crawl_site",
            "description": "Crawl a website systematically with depth control and content extraction",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_url": {"type": "string", "description": "Starting URL for the crawl"},
                    "max_depth": {"type": "integer", "description": "Maximum depth to crawl", "default": 2},
                    "same_domain_only": {"type": "boolean", "description": "Only crawl same domain", "default": True},
                    "respect_robots": {"type": "boolean", "description": "Respect robots.txt", "default": True}
                },
                "required": ["start_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crawl_sitemap",
            "description": "Extract URLs from a sitemap XML file",
            "parameters": {
                "type": "object",
                "properties": {
                    "sitemap_url": {"type": "string", "description": "URL of the sitemap"}
                },
                "required": ["sitemap_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_broken_links",
            "description": "Find broken links on a website",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Starting URL"},
                    "check_depth": {"type": "integer", "description": "Depth to check", "default": 1}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_emails",
            "description": "Extract email addresses from a website",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Starting URL"},
                    "max_depth": {"type": "integer", "description": "Depth to search", "default": 1}
                },
                "required": ["url"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "web_crawler",
    "description": "OpenAI-compatible web crawler with depth control and content extraction",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "crawl_site",
        "crawl_sitemap",
        "find_broken_links",
        "extract_emails"
    ],
    "requirements": ["requests", "beautifulsoup4", "lxml"],
    "safety_features": [
        "Robots.txt compliance",
        "Rate limiting",
        "Max pages limit",
        "Timeout protection",
        "Domain filtering"
    ]
}
