"""
Price Data Collector Tool (OpenAI-Compatible)
Collects and tracks price data from various sources with historical tracking.
"""

import requests
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

class PriceDataCollectorTool:
    """
    OpenAI-compatible price data collector with historical tracking.
    Supports multiple data sources, APIs, and web scraping for price information.
    """
    
    def __init__(self, db_path: str = "./price_data.db", timeout: int = 30):
        """
        Initialize price data collector.
        
        Args:
            db_path: Path to SQLite database for price history
            timeout: Request timeout in seconds
        """
        self.db_path = Path(db_path)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; PriceCollector/1.0)'
        })
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for price tracking."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create price_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                item_id TEXT NOT NULL,
                item_name TEXT,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                timestamp TEXT NOT NULL,
                url TEXT,
                metadata TEXT
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_item_timestamp 
            ON price_data(item_id, timestamp)
        ''')
        
        self.conn.commit()
    
    def collect_price(self, source: str, item_id: str, url: Optional[str] = None,
                     selector: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Collect price data from a source.
        
        Args:
            source: Data source name (e.g., 'amazon', 'api', 'website')
            item_id: Unique identifier for the item
            url: URL to scrape or API endpoint
            selector: CSS selector for price element (for web scraping)
            api_key: API key if using an API source
            
        Returns:
            Dictionary with collected price data
        """
        try:
            if url and url.startswith('http'):
                # Web scraping mode
                if selector:
                    result = self._scrape_price(url, selector)
                else:
                    result = self._auto_detect_price(url)
            elif api_key:
                # API mode (placeholder for various APIs)
                result = self._fetch_from_api(source, item_id, api_key)
            else:
                return {
                    "success": False,
                    "error": "Either URL with selector or API key must be provided"
                }
            
            if not result["success"]:
                return result
            
            # Store in database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO price_data (source, item_id, item_name, price, currency, timestamp, url, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source,
                item_id,
                result.get("item_name", ""),
                result["price"],
                result.get("currency", "USD"),
                datetime.now().isoformat(),
                url or "",
                json.dumps(result.get("metadata", {}))
            ))
            self.conn.commit()
            
            return {
                "success": True,
                "source": source,
                "item_id": item_id,
                "price": result["price"],
                "currency": result.get("currency", "USD"),
                "timestamp": datetime.now().isoformat(),
                "item_name": result.get("item_name", "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def collect_multiple(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Collect price data for multiple items.
        
        Args:
            items: List of item dictionaries with source, item_id, url, etc.
            
        Returns:
            Dictionary with collection results
        """
        results = []
        successful = 0
        failed = 0
        
        for item in items:
            result = self.collect_price(
                source=item.get("source", "unknown"),
                item_id=item.get("item_id", ""),
                url=item.get("url"),
                selector=item.get("selector"),
                api_key=item.get("api_key")
            )
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        return {
            "success": True,
            "total_items": len(items),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_price_history(self, item_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get price history for an item.
        
        Args:
            item_id: Unique identifier for the item
            days: Number of days of history to retrieve
            
        Returns:
            Dictionary with price history
        """
        try:
            cursor = self.conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM price_data
                WHERE item_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (item_id, since_date))
            
            rows = cursor.fetchall()
            
            if not rows:
                return {
                    "success": True,
                    "item_id": item_id,
                    "count": 0,
                    "history": [],
                    "message": "No price history found"
                }
            
            history = []
            prices = []
            
            for row in rows:
                entry = dict(row)
                history.append({
                    "timestamp": entry["timestamp"],
                    "price": entry["price"],
                    "currency": entry["currency"],
                    "source": entry["source"]
                })
                prices.append(entry["price"])
            
            # Calculate statistics
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            current_price = prices[-1]
            
            return {
                "success": True,
                "item_id": item_id,
                "count": len(history),
                "history": history,
                "statistics": {
                    "current_price": current_price,
                    "average_price": round(avg_price, 2),
                    "min_price": min_price,
                    "max_price": max_price,
                    "price_range": round(max_price - min_price, 2),
                    "volatility": round((max_price - min_price) / avg_price * 100, 2) if avg_price > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_price_alerts(self, item_id: str, threshold_low: Optional[float] = None,
                        threshold_high: Optional[float] = None) -> Dict[str, Any]:
        """
        Check if current price triggers alerts.
        
        Args:
            item_id: Unique identifier for the item
            threshold_low: Alert if price drops below this
            threshold_high: Alert if price rises above this
            
        Returns:
            Dictionary with alert status
        """
        try:
            cursor = self.conn.cursor()
            
            # Get latest price
            cursor.execute('''
                SELECT * FROM price_data
                WHERE item_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (item_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "error": "No price data found for item"
                }
            
            current_price = row["price"]
            alerts = []
            
            if threshold_low and current_price < threshold_low:
                alerts.append({
                    "type": "low",
                    "message": f"Price dropped below ${threshold_low}",
                    "current_price": current_price,
                    "threshold": threshold_low
                })
            
            if threshold_high and current_price > threshold_high:
                alerts.append({
                    "type": "high",
                    "message": f"Price rose above ${threshold_high}",
                    "current_price": current_price,
                    "threshold": threshold_high
                })
            
            return {
                "success": True,
                "item_id": item_id,
                "current_price": current_price,
                "alerts_triggered": len(alerts) > 0,
                "alerts": alerts
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _scrape_price(self, url: str, selector: str) -> Dict[str, Any]:
        """Scrape price from a webpage using CSS selector."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find price element
            element = soup.select_one(selector)
            
            if not element:
                return {
                    "success": False,
                    "error": f"Price element not found with selector: {selector}"
                }
            
            # Extract price
            price_text = element.get_text(strip=True)
            price = self._extract_price_from_text(price_text)
            
            if price is None:
                return {
                    "success": False,
                    "error": f"Could not extract price from text: {price_text}"
                }
            
            return {
                "success": True,
                "price": price,
                "currency": "USD",  # Could be improved with currency detection
                "raw_text": price_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _auto_detect_price(self, url: str) -> Dict[str, Any]:
        """Auto-detect price on a webpage."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common price selectors
            price_selectors = [
                '[class*="price"]',
                '[id*="price"]',
                '[itemprop="price"]',
                '.product-price',
                '#price',
                'span.price',
                'div.price'
            ]
            
            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text(strip=True)
                    price = self._extract_price_from_text(price_text)
                    if price is not None:
                        return {
                            "success": True,
                            "price": price,
                            "currency": "USD",
                            "raw_text": price_text,
                            "selector_used": selector
                        }
            
            return {
                "success": False,
                "error": "Could not auto-detect price on page"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _fetch_from_api(self, source: str, item_id: str, api_key: str) -> Dict[str, Any]:
        """Fetch price from API (placeholder for various APIs)."""
        # This is a placeholder - would need specific API implementations
        return {
            "success": False,
            "error": "API integration not yet implemented"
        }
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract numeric price from text."""
        # Remove common currency symbols and commas
        cleaned = re.sub(r'[^\d.]', '', text)
        
        try:
            return float(cleaned)
        except:
            return None
    
    def __del__(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "collect_price",
            "description": "Collect current price data for an item from a source",
            "parameters": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Data source name"},
                    "item_id": {"type": "string", "description": "Unique identifier for the item"},
                    "url": {"type": "string", "description": "URL to scrape or API endpoint"},
                    "selector": {"type": "string", "description": "CSS selector for price element"},
                    "api_key": {"type": "string", "description": "API key if using API source"}
                },
                "required": ["source", "item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_history",
            "description": "Get historical price data for an item with statistics",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Unique identifier for the item"},
                    "days": {"type": "integer", "description": "Number of days of history", "default": 30}
                },
                "required": ["item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_alerts",
            "description": "Check if current price triggers any alerts",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Unique identifier for the item"},
                    "threshold_low": {"type": "number", "description": "Alert if price drops below"},
                    "threshold_high": {"type": "number", "description": "Alert if price rises above"}
                },
                "required": ["item_id"]
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "price_data_collector",
    "description": "OpenAI-compatible price data collector with historical tracking",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "collect_price",
        "collect_multiple",
        "get_price_history",
        "get_price_alerts"
    ],
    "requirements": ["requests", "beautifulsoup4", "sqlite3"],
    "safety_features": [
        "Database persistence",
        "Price validation",
        "Error handling",
        "Request timeout"
    ]
}
