"""
Image Analyzer Tool (OpenAI-Compatible)
Analyzes images for content, metadata, properties, and visual features.
"""

import requests
from PIL import Image, ExifTags
from io import BytesIO
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import mimetypes
from collections import Counter

class ImageAnalyzerTool:
    """
    OpenAI-compatible image analyzer for content and metadata extraction.
    Supports local files and URLs, with detailed analysis capabilities.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize image analyzer.
        
        Args:
            timeout: Request timeout for downloading images from URLs
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; ImageAnalyzer/1.0)'
        })
    
    def analyze_image(self, image_source: str, include_metadata: bool = True,
                     include_colors: bool = True, include_histogram: bool = False) -> Dict[str, Any]:
        """
        Analyze an image from file path or URL.
        
        Args:
            image_source: File path or URL to the image
            include_metadata: Extract EXIF metadata
            include_colors: Analyze dominant colors
            include_histogram: Include color histogram data
            
        Returns:
            Dictionary with image analysis
        """
        try:
            # Load image
            if image_source.startswith(('http://', 'https://')):
                img = self._load_image_from_url(image_source)
            else:
                img = self._load_image_from_file(image_source)
            
            if img is None:
                return {
                    "success": False,
                    "error": "Failed to load image"
                }
            
            # Basic properties
            result = {
                "success": True,
                "source": image_source,
                "properties": {
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "aspect_ratio": round(img.width / img.height, 2),
                    "megapixels": round((img.width * img.height) / 1000000, 2),
                    "has_transparency": img.mode in ('RGBA', 'LA', 'P')
                }
            }
            
            # Extract metadata
            if include_metadata:
                result["metadata"] = self._extract_metadata(img)
            
            # Analyze colors
            if include_colors:
                result["colors"] = self._analyze_colors(img)
            
            # Include histogram
            if include_histogram:
                result["histogram"] = self._get_histogram(img)
            
            # Calculate hash
            result["hash"] = self._calculate_image_hash(img)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def compare_images(self, image1_source: str, image2_source: str) -> Dict[str, Any]:
        """
        Compare two images for similarity.
        
        Args:
            image1_source: First image (file path or URL)
            image2_source: Second image (file path or URL)
            
        Returns:
            Dictionary with comparison results
        """
        try:
            # Load both images
            img1 = self._load_image(image1_source)
            img2 = self._load_image(image2_source)
            
            if img1 is None or img2 is None:
                return {
                    "success": False,
                    "error": "Failed to load one or both images"
                }
            
            # Compare dimensions
            same_dimensions = (img1.width == img2.width and img1.height == img2.height)
            
            # Compare hashes (simple similarity check)
            hash1 = self._calculate_image_hash(img1)
            hash2 = self._calculate_image_hash(img2)
            identical = hash1 == hash2
            
            # Compare formats
            same_format = img1.format == img2.format
            
            return {
                "success": True,
                "image1": image1_source,
                "image2": image2_source,
                "identical": identical,
                "same_dimensions": same_dimensions,
                "same_format": same_format,
                "dimensions_match": same_dimensions,
                "image1_size": f"{img1.width}x{img1.height}",
                "image2_size": f"{img2.width}x{img2.height}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_analyze(self, image_sources: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple images in batch.
        
        Args:
            image_sources: List of image file paths or URLs
            
        Returns:
            Dictionary with results for all images
        """
        results = []
        successful = 0
        failed = 0
        total_megapixels = 0
        
        for source in image_sources:
            result = self.analyze_image(source, include_metadata=False, 
                                       include_colors=False, include_histogram=False)
            results.append(result)
            
            if result["success"]:
                successful += 1
                total_megapixels += result["properties"]["megapixels"]
            else:
                failed += 1
        
        return {
            "success": True,
            "total_images": len(image_sources),
            "successful": successful,
            "failed": failed,
            "total_megapixels": round(total_megapixels, 2),
            "results": results
        }
    
    def get_thumbnail(self, image_source: str, max_size: tuple = (256, 256)) -> Dict[str, Any]:
        """
        Generate a thumbnail of an image.
        
        Args:
            image_source: Image file path or URL
            max_size: Maximum thumbnail dimensions (width, height)
            
        Returns:
            Dictionary with thumbnail info
        """
        try:
            img = self._load_image(image_source)
            
            if img is None:
                return {
                    "success": False,
                    "error": "Failed to load image"
                }
            
            # Create thumbnail (use LANCZOS for compatibility)
            try:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback for older Pillow versions
                img.thumbnail(max_size, Image.LANCZOS)
            
            return {
                "success": True,
                "original_source": image_source,
                "thumbnail_size": f"{img.width}x{img.height}",
                "thumbnail_width": img.width,
                "thumbnail_height": img.height,
                "message": "Thumbnail created in memory (call save to persist)"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_image(self, source: str) -> Optional[Image.Image]:
        """Load image from file or URL."""
        if source.startswith(('http://', 'https://')):
            return self._load_image_from_url(source)
        else:
            return self._load_image_from_file(source)
    
    def _load_image_from_url(self, url: str) -> Optional[Image.Image]:
        """Load image from URL."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except:
            return None
    
    def _load_image_from_file(self, file_path: str) -> Optional[Image.Image]:
        """Load image from file."""
        try:
            return Image.open(file_path)
        except:
            return None
    
    def _extract_metadata(self, img: Image.Image) -> Dict[str, Any]:
        """Extract EXIF and other metadata from image."""
        metadata = {
            "exif": {},
            "info": {}
        }
        
        # Extract EXIF data
        try:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    # Convert bytes to string if needed
                    if isinstance(value, bytes):
                        try:
                            value = value.decode()
                        except:
                            value = str(value)
                    metadata["exif"][str(tag)] = str(value)
        except:
            pass
        
        # Extract PIL info
        if hasattr(img, 'info'):
            for key, value in img.info.items():
                if isinstance(value, (str, int, float)):
                    metadata["info"][key] = value
        
        return metadata
    
    def _analyze_colors(self, img: Image.Image, num_colors: int = 5) -> Dict[str, Any]:
        """Analyze dominant colors in image."""
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize for faster processing
        img_small = img.copy()
        img_small.thumbnail((100, 100))
        
        # Get all pixels
        pixels = list(img_small.getdata())
        
        # Count color frequencies
        color_counts = Counter(pixels)
        most_common = color_counts.most_common(num_colors)
        
        dominant_colors = []
        for color, count in most_common:
            dominant_colors.append({
                "rgb": color,
                "hex": "#{:02x}{:02x}{:02x}".format(*color),
                "frequency": round(count / len(pixels), 4)
            })
        
        return {
            "dominant_colors": dominant_colors,
            "unique_colors": len(color_counts),
            "total_pixels": len(pixels)
        }
    
    def _get_histogram(self, img: Image.Image) -> Dict[str, List[int]]:
        """Get color histogram of image."""
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        histogram = img.histogram()
        
        return {
            "red": histogram[0:256],
            "green": histogram[256:512],
            "blue": histogram[512:768]
        }
    
    def _calculate_image_hash(self, img: Image.Image) -> str:
        """Calculate hash of image content."""
        # Convert to bytes
        img_bytes = img.tobytes()
        return hashlib.md5(img_bytes).hexdigest()

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image for properties, metadata, colors, and features",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "File path or URL to the image"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Extract EXIF and other metadata",
                        "default": True
                    },
                    "include_colors": {
                        "type": "boolean",
                        "description": "Analyze dominant colors",
                        "default": True
                    },
                    "include_histogram": {
                        "type": "boolean",
                        "description": "Include color histogram data",
                        "default": False
                    }
                },
                "required": ["image_source"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_images",
            "description": "Compare two images for similarity and differences",
            "parameters": {
                "type": "object",
                "properties": {
                    "image1_source": {
                        "type": "string",
                        "description": "First image (file path or URL)"
                    },
                    "image2_source": {
                        "type": "string",
                        "description": "Second image (file path or URL)"
                    }
                },
                "required": ["image1_source", "image2_source"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "batch_analyze",
            "description": "Analyze multiple images in batch",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of image file paths or URLs"
                    }
                },
                "required": ["image_sources"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_thumbnail",
            "description": "Generate a thumbnail of an image",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_source": {
                        "type": "string",
                        "description": "Image file path or URL"
                    },
                    "max_size": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Maximum thumbnail dimensions [width, height]",
                        "default": [256, 256]
                    }
                },
                "required": ["image_source"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "image_analyzer",
    "description": "OpenAI-compatible image analyzer for content and metadata extraction",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "analyze_image",
        "compare_images",
        "batch_analyze",
        "get_thumbnail"
    ],
    "requirements": ["Pillow", "requests"],
    "safety_features": [
        "Request timeout",
        "Error handling",
        "Memory-efficient processing",
        "Format validation"
    ]
}

if __name__ == "__main__":
    # Example usage
    import json
    tool = ImageAnalyzerTool()
    
    # Test analysis
    print("Image Analyzer Tool ready for testing")
