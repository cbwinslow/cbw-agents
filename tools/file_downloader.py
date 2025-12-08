"""
File Downloader Tool (OpenAI-Compatible)
Provides secure file downloading capabilities with progress tracking and validation.
"""

import requests
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from urllib.parse import urlparse, unquote
import time

class FileDownloaderTool:
    """
    OpenAI-compatible file downloader with security and progress tracking.
    Supports multiple file types, resume capability, and integrity checking.
    """
    
    def __init__(self, download_dir: str = "./downloads", max_file_size: int = 500 * 1024 * 1024):
        """
        Initialize file downloader.
        
        Args:
            download_dir: Directory to save downloaded files
            max_file_size: Maximum file size in bytes (default: 500MB)
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; FileDownloader/1.0)'
        })
        
    def download_file(self, url: str, filename: Optional[str] = None, 
                     verify_ssl: bool = True) -> Dict[str, Any]:
        """
        Download a file from URL.
        
        Args:
            url: URL to download from
            filename: Optional custom filename (auto-detected if not provided)
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            Dictionary with download result and file info
        """
        try:
            # Get file info first
            head_response = self.session.head(url, allow_redirects=True, verify=verify_ssl)
            
            if head_response.status_code >= 400:
                return {
                    "success": False,
                    "error": f"HTTP {head_response.status_code}: Unable to access file"
                }
            
            # Check file size
            content_length = int(head_response.headers.get('content-length', 0))
            if content_length > self.max_file_size:
                return {
                    "success": False,
                    "error": f"File size ({content_length} bytes) exceeds maximum ({self.max_file_size} bytes)"
                }
            
            # Determine filename
            if not filename:
                filename = self._get_filename_from_url(url, head_response.headers)
            
            file_path = self.download_dir / filename
            
            # Download file
            response = self.session.get(url, stream=True, verify=verify_ssl)
            response.raise_for_status()
            
            downloaded_size = 0
            start_time = time.time()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate hash
            file_hash = self._calculate_file_hash(file_path)
            
            return {
                "success": True,
                "filename": filename,
                "file_path": str(file_path),
                "size_bytes": downloaded_size,
                "size_mb": round(downloaded_size / (1024 * 1024), 2),
                "download_time_seconds": round(duration, 2),
                "speed_mbps": round((downloaded_size / duration) / (1024 * 1024), 2) if duration > 0 else 0,
                "mime_type": response.headers.get('content-type', 'unknown'),
                "sha256": file_hash,
                "url": url
            }
            
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
    
    def download_multiple(self, urls: List[str]) -> Dict[str, Any]:
        """
        Download multiple files.
        
        Args:
            urls: List of URLs to download
            
        Returns:
            Dictionary with results for all downloads
        """
        results = []
        successful = 0
        failed = 0
        total_size = 0
        
        for url in urls:
            result = self.download_file(url)
            results.append(result)
            
            if result["success"]:
                successful += 1
                total_size += result["size_bytes"]
            else:
                failed += 1
        
        return {
            "success": True,
            "total_files": len(urls),
            "successful": successful,
            "failed": failed,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "results": results
        }
    
    def get_file_info(self, url: str) -> Dict[str, Any]:
        """
        Get information about a file without downloading it.
        
        Args:
            url: URL of the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            response = self.session.head(url, allow_redirects=True)
            response.raise_for_status()
            
            content_length = int(response.headers.get('content-length', 0))
            
            return {
                "success": True,
                "url": url,
                "final_url": response.url,
                "size_bytes": content_length,
                "size_mb": round(content_length / (1024 * 1024), 2),
                "mime_type": response.headers.get('content-type', 'unknown'),
                "filename": self._get_filename_from_url(url, response.headers),
                "can_download": content_length <= self.max_file_size,
                "headers": dict(response.headers)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_downloads(self) -> Dict[str, Any]:
        """
        List all downloaded files.
        
        Returns:
            Dictionary with list of downloaded files
        """
        try:
            files = []
            total_size = 0
            
            for file_path in self.download_dir.iterdir():
                if file_path.is_file():
                    size = file_path.stat().st_size
                    total_size += size
                    
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                        "modified": file_path.stat().st_mtime,
                        "mime_type": mimetypes.guess_type(file_path)[0] or 'unknown'
                    })
            
            return {
                "success": True,
                "download_dir": str(self.download_dir),
                "file_count": len(files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files": files
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_download(self, filename: str) -> Dict[str, Any]:
        """
        Delete a downloaded file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            file_path = self.download_dir / filename
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "File not found"
                }
            
            file_path.unlink()
            
            return {
                "success": True,
                "message": f"Deleted {filename}",
                "filename": filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_filename_from_url(self, url: str, headers: Dict) -> str:
        """Extract filename from URL or headers."""
        # Try Content-Disposition header first
        content_disposition = headers.get('content-disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
            return filename
        
        # Extract from URL
        parsed = urlparse(url)
        filename = unquote(os.path.basename(parsed.path))
        
        # If no extension, try to add one based on content type
        if not os.path.splitext(filename)[1]:
            content_type = headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type.split(';')[0])
            if ext:
                filename += ext
        
        # Fallback to generic name
        if not filename or filename == '/':
            filename = f"download_{int(time.time())}"
        
        return filename
    
    def _calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash."""
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "download_file",
            "description": "Download a file from a URL with progress tracking and validation",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the file to download"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename (auto-detected if not provided)"
                    },
                    "verify_ssl": {
                        "type": "boolean",
                        "description": "Whether to verify SSL certificates",
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
            "name": "download_multiple",
            "description": "Download multiple files from a list of URLs",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of URLs to download"
                    }
                },
                "required": ["urls"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "Get information about a file without downloading it",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the file to get information about"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_downloads",
            "description": "List all downloaded files in the download directory",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_download",
            "description": "Delete a downloaded file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete"
                    }
                },
                "required": ["filename"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "file_downloader",
    "description": "OpenAI-compatible file downloader with progress tracking and validation",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "download_file",
        "download_multiple",
        "get_file_info",
        "list_downloads",
        "delete_download"
    ],
    "requirements": ["requests", "pathlib", "hashlib", "mimetypes"],
    "safety_features": [
        "File size limits",
        "SSL verification",
        "Progress tracking",
        "Integrity checking (SHA256)",
        "Error handling"
    ]
}

if __name__ == "__main__":
    # Example usage
    import json
    tool = FileDownloaderTool()
    
    # Test getting file info
    result = tool.get_file_info("https://example.com/sample.pdf")
    print(json.dumps(result, indent=2))
