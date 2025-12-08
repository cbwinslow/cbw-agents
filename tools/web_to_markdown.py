"""
Web to Markdown Converter Tool (OpenAI-Compatible)
Converts web pages to clean, readable Markdown format.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import re
import html2text

class WebToMarkdownTool:
    """
    OpenAI-compatible tool for converting web pages to Markdown.
    Supports clean formatting, link preservation, and metadata extraction.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize web to markdown converter.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; MarkdownConverter/1.0)'
        })
        
        # Configure html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_emphasis = False
        self.h2t.body_width = 0  # No wrapping
        self.h2t.protect_links = True
        self.h2t.unicode_snob = True
        
    def convert_url(self, url: str, include_metadata: bool = True,
                   include_links: bool = True, include_images: bool = True) -> Dict[str, Any]:
        """
        Convert a web page to Markdown.
        
        Args:
            url: URL of the web page to convert
            include_metadata: Include page metadata in output
            include_links: Include links in the markdown
            include_images: Include images in the markdown
            
        Returns:
            Dictionary with markdown content and metadata
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Clean the HTML
            cleaned_html = self._clean_html(soup, include_links, include_images)
            
            # Configure converter based on options
            self.h2t.ignore_links = not include_links
            self.h2t.ignore_images = not include_images
            
            # Convert to markdown
            markdown = self.h2t.handle(str(cleaned_html))
            
            # Clean up the markdown
            markdown = self._clean_markdown(markdown)
            
            result = {
                "success": True,
                "url": url,
                "markdown": markdown,
                "character_count": len(markdown),
                "word_count": len(markdown.split())
            }
            
            if include_metadata:
                result["metadata"] = metadata
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert_html(self, html_content: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert HTML content to Markdown.
        
        Args:
            html_content: HTML content to convert
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with markdown content
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Clean the HTML
            cleaned_html = self._clean_html(soup)
            
            # Convert to markdown
            markdown = self.h2t.handle(str(cleaned_html))
            
            # Clean up the markdown
            markdown = self._clean_markdown(markdown)
            
            return {
                "success": True,
                "markdown": markdown,
                "character_count": len(markdown),
                "word_count": len(markdown.split())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert_to_file(self, url: str, output_path: str) -> Dict[str, Any]:
        """
        Convert a web page to Markdown and save to file.
        
        Args:
            url: URL of the web page to convert
            output_path: Path to save the markdown file
            
        Returns:
            Dictionary with conversion result
        """
        try:
            result = self.convert_url(url)
            
            if not result["success"]:
                return result
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write metadata as frontmatter if available
                if "metadata" in result:
                    f.write("---\n")
                    for key, value in result["metadata"].items():
                        f.write(f"{key}: {value}\n")
                    f.write("---\n\n")
                
                f.write(result["markdown"])
            
            return {
                "success": True,
                "url": url,
                "output_path": output_path,
                "character_count": result["character_count"],
                "word_count": result["word_count"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_convert(self, urls: List[str]) -> Dict[str, Any]:
        """
        Convert multiple URLs to Markdown.
        
        Args:
            urls: List of URLs to convert
            
        Returns:
            Dictionary with results for all conversions
        """
        results = []
        successful = 0
        failed = 0
        total_words = 0
        
        for url in urls:
            result = self.convert_url(url, include_metadata=False)
            results.append(result)
            
            if result["success"]:
                successful += 1
                total_words += result["word_count"]
            else:
                failed += 1
        
        return {
            "success": True,
            "total_urls": len(urls),
            "successful": successful,
            "failed": failed,
            "total_words": total_words,
            "results": results
        }
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """Extract metadata from HTML."""
        metadata = {
            "url": url,
            "title": soup.title.string if soup.title else "",
            "description": "",
            "author": "",
            "date": "",
            "keywords": ""
        }
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower() or meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if 'description' in name:
                metadata["description"] = content
            elif 'author' in name:
                metadata["author"] = content
            elif 'date' in name or 'published' in name:
                metadata["date"] = content
            elif 'keywords' in name:
                metadata["keywords"] = content
        
        return metadata
    
    def _clean_html(self, soup: BeautifulSoup, include_links: bool = True, 
                   include_images: bool = True) -> BeautifulSoup:
        """Clean and prepare HTML for conversion."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                           'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, type(soup))):
            comment.extract()
        
        # Clean up attributes
        for tag in soup.find_all(True):
            # Keep only essential attributes
            if tag.name == 'a' and include_links:
                tag.attrs = {k: v for k, v in tag.attrs.items() if k in ['href', 'title']}
            elif tag.name == 'img' and include_images:
                tag.attrs = {k: v for k, v in tag.attrs.items() if k in ['src', 'alt', 'title']}
            else:
                tag.attrs = {}
        
        # Try to extract main content
        main = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main:
            return main
        
        return soup.find('body') or soup
    
    def _clean_markdown(self, markdown: str) -> str:
        """Clean up markdown output."""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.rstrip() for line in markdown.split('\n')]
        markdown = '\n'.join(lines)
        
        # Remove empty list items
        markdown = re.sub(r'^\s*[\*\-]\s*$', '', markdown, flags=re.MULTILINE)
        
        # Clean up spacing around headers
        markdown = re.sub(r'\n(#{1,6}\s)', r'\n\n\1', markdown)
        
        return markdown.strip()

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "convert_url",
            "description": "Convert a web page URL to clean Markdown format with optional metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to convert"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include page metadata (title, description, author, etc.)",
                        "default": True
                    },
                    "include_links": {
                        "type": "boolean",
                        "description": "Include links in the markdown output",
                        "default": True
                    },
                    "include_images": {
                        "type": "boolean",
                        "description": "Include images in the markdown output",
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
            "name": "convert_html",
            "description": "Convert raw HTML content to Markdown format",
            "parameters": {
                "type": "object",
                "properties": {
                    "html_content": {
                        "type": "string",
                        "description": "The HTML content to convert"
                    },
                    "base_url": {
                        "type": "string",
                        "description": "Optional base URL for resolving relative links"
                    }
                },
                "required": ["html_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_to_file",
            "description": "Convert a web page to Markdown and save to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the web page to convert"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the markdown file should be saved"
                    }
                },
                "required": ["url", "output_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "batch_convert",
            "description": "Convert multiple web pages to Markdown in batch",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to convert"
                    }
                },
                "required": ["urls"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "web_to_markdown",
    "description": "OpenAI-compatible web page to Markdown converter",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "convert_url",
        "convert_html",
        "convert_to_file",
        "batch_convert"
    ],
    "requirements": ["requests", "beautifulsoup4", "html2text", "lxml"],
    "safety_features": [
        "Request timeout",
        "HTML sanitization",
        "Script/style removal",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    import json
    tool = WebToMarkdownTool()
    
    # Test conversion
    result = tool.convert_url("https://example.com")
    if result["success"]:
        print(result["markdown"][:500])
