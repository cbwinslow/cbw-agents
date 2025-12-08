"""
Bookmarks Manager Tool (OpenAI-Compatible)
Manages web bookmarks with tagging, search, and organization features.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
import hashlib

class BookmarksManagerTool:
    """
    OpenAI-compatible bookmarks manager with tagging and search capabilities.
    Stores bookmarks in SQLite database for persistent storage.
    """
    
    def __init__(self, db_path: str = "./bookmarks.db"):
        """
        Initialize bookmarks manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database and create tables."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create bookmarks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                domain TEXT,
                created_at TEXT,
                updated_at TEXT,
                visit_count INTEGER DEFAULT 0,
                last_visited TEXT,
                favorite BOOLEAN DEFAULT 0,
                archived BOOLEAN DEFAULT 0
            )
        ''')
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TEXT
            )
        ''')
        
        # Create bookmark_tags junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmark_tags (
                bookmark_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
                PRIMARY KEY (bookmark_id, tag_id)
            )
        ''')
        
        # Create folders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                parent_id INTEGER,
                created_at TEXT,
                FOREIGN KEY (parent_id) REFERENCES folders (id) ON DELETE CASCADE
            )
        ''')
        
        # Create bookmark_folders junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmark_folders (
                bookmark_id INTEGER,
                folder_id INTEGER,
                FOREIGN KEY (bookmark_id) REFERENCES bookmarks (id) ON DELETE CASCADE,
                FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE CASCADE,
                PRIMARY KEY (bookmark_id, folder_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_bookmark(self, url: str, title: Optional[str] = None, 
                    description: Optional[str] = None, tags: Optional[List[str]] = None,
                    folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new bookmark.
        
        Args:
            url: URL to bookmark
            title: Page title
            description: Bookmark description
            tags: List of tags
            folder: Folder name to organize bookmark
            
        Returns:
            Dictionary with operation result
        """
        try:
            cursor = self.conn.cursor()
            
            # Extract domain
            domain = urlparse(url).netloc
            
            now = datetime.now().isoformat()
            
            # Insert bookmark
            cursor.execute('''
                INSERT INTO bookmarks (url, title, description, domain, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, title, description, domain, now, now))
            
            bookmark_id = cursor.lastrowid
            
            # Add tags if provided
            if tags:
                for tag_name in tags:
                    tag_id = self._get_or_create_tag(tag_name)
                    cursor.execute('''
                        INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id)
                        VALUES (?, ?)
                    ''', (bookmark_id, tag_id))
            
            # Add to folder if provided
            if folder:
                folder_id = self._get_or_create_folder(folder)
                cursor.execute('''
                    INSERT OR IGNORE INTO bookmark_folders (bookmark_id, folder_id)
                    VALUES (?, ?)
                ''', (bookmark_id, folder_id))
            
            self.conn.commit()
            
            return {
                "success": True,
                "bookmark_id": bookmark_id,
                "url": url,
                "message": "Bookmark added successfully"
            }
            
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": "Bookmark with this URL already exists"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_bookmarks(self, query: Optional[str] = None, tags: Optional[List[str]] = None,
                        folder: Optional[str] = None, favorite: Optional[bool] = None) -> Dict[str, Any]:
        """
        Search bookmarks.
        
        Args:
            query: Search query (searches title, description, URL)
            tags: Filter by tags
            folder: Filter by folder
            favorite: Filter by favorite status
            
        Returns:
            Dictionary with search results
        """
        try:
            cursor = self.conn.cursor()
            
            sql = "SELECT DISTINCT b.* FROM bookmarks b"
            conditions = []
            params = []
            
            if tags:
                sql += " JOIN bookmark_tags bt ON b.id = bt.bookmark_id"
                sql += " JOIN tags t ON bt.tag_id = t.id"
                conditions.append(f"t.name IN ({','.join('?' * len(tags))})")
                params.extend(tags)
            
            if folder:
                sql += " JOIN bookmark_folders bf ON b.id = bf.bookmark_id"
                sql += " JOIN folders f ON bf.folder_id = f.id"
                conditions.append("f.name = ?")
                params.append(folder)
            
            if query:
                conditions.append("(b.title LIKE ? OR b.description LIKE ? OR b.url LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if favorite is not None:
                conditions.append("b.favorite = ?")
                params.append(1 if favorite else 0)
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql += " ORDER BY b.created_at DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            bookmarks = []
            for row in rows:
                bookmark = dict(row)
                bookmark["tags"] = self._get_bookmark_tags(bookmark["id"])
                bookmark["folders"] = self._get_bookmark_folders(bookmark["id"])
                bookmarks.append(bookmark)
            
            return {
                "success": True,
                "count": len(bookmarks),
                "bookmarks": bookmarks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_bookmark(self, bookmark_id: int, **kwargs) -> Dict[str, Any]:
        """
        Update a bookmark.
        
        Args:
            bookmark_id: ID of bookmark to update
            **kwargs: Fields to update (title, description, tags, etc.)
            
        Returns:
            Dictionary with operation result
        """
        try:
            cursor = self.conn.cursor()
            
            # Update basic fields
            update_fields = []
            params = []
            
            for field in ['title', 'description', 'favorite', 'archived']:
                if field in kwargs:
                    update_fields.append(f"{field} = ?")
                    params.append(kwargs[field])
            
            if update_fields:
                update_fields.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(bookmark_id)
                
                sql = f"UPDATE bookmarks SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, params)
            
            # Update tags if provided
            if 'tags' in kwargs:
                # Remove existing tags
                cursor.execute("DELETE FROM bookmark_tags WHERE bookmark_id = ?", (bookmark_id,))
                
                # Add new tags
                for tag_name in kwargs['tags']:
                    tag_id = self._get_or_create_tag(tag_name)
                    cursor.execute('''
                        INSERT INTO bookmark_tags (bookmark_id, tag_id)
                        VALUES (?, ?)
                    ''', (bookmark_id, tag_id))
            
            self.conn.commit()
            
            return {
                "success": True,
                "bookmark_id": bookmark_id,
                "message": "Bookmark updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_bookmark(self, bookmark_id: int) -> Dict[str, Any]:
        """
        Delete a bookmark.
        
        Args:
            bookmark_id: ID of bookmark to delete
            
        Returns:
            Dictionary with operation result
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
            self.conn.commit()
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": "Bookmark deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Bookmark not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_tags(self) -> Dict[str, Any]:
        """
        Get all tags.
        
        Returns:
            Dictionary with all tags
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tags ORDER BY name")
            tags = [dict(row) for row in cursor.fetchall()]
            
            return {
                "success": True,
                "count": len(tags),
                "tags": tags
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_bookmarks(self, format: str = "json") -> Dict[str, Any]:
        """
        Export all bookmarks.
        
        Args:
            format: Export format ('json', 'html', 'csv')
            
        Returns:
            Dictionary with exported data
        """
        try:
            result = self.search_bookmarks()
            
            if not result["success"]:
                return result
            
            bookmarks = result["bookmarks"]
            
            if format == "json":
                return {
                    "success": True,
                    "format": "json",
                    "data": json.dumps(bookmarks, indent=2),
                    "count": len(bookmarks)
                }
            
            # Add support for other formats as needed
            return {
                "success": False,
                "error": f"Format '{format}' not yet supported"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_or_create_tag(self, tag_name: str) -> int:
        """Get or create a tag and return its ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            cursor.execute('''
                INSERT INTO tags (name, created_at)
                VALUES (?, ?)
            ''', (tag_name, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[int] = None) -> int:
        """Get or create a folder and return its ID."""
        cursor = self.conn.cursor()
        
        # Handle NULL comparison properly for SQLite
        if parent_id is None:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id IS NULL", 
                          (folder_name,))
        else:
            cursor.execute("SELECT id FROM folders WHERE name = ? AND parent_id = ?", 
                          (folder_name, parent_id))
        
        row = cursor.fetchone()
        
        if row:
            return row[0]
        else:
            cursor.execute('''
                INSERT INTO folders (name, parent_id, created_at)
                VALUES (?, ?, ?)
            ''', (folder_name, parent_id, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def _get_bookmark_tags(self, bookmark_id: int) -> List[str]:
        """Get tags for a bookmark."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN bookmark_tags bt ON t.id = bt.tag_id
            WHERE bt.bookmark_id = ?
        ''', (bookmark_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def _get_bookmark_folders(self, bookmark_id: int) -> List[str]:
        """Get folders for a bookmark."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT f.name FROM folders f
            JOIN bookmark_folders bf ON f.id = bf.folder_id
            WHERE bf.bookmark_id = ?
        ''', (bookmark_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def __del__(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

# OpenAI function definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_bookmark",
            "description": "Add a new bookmark with optional tags and folder organization",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to bookmark"},
                    "title": {"type": "string", "description": "Page title"},
                    "description": {"type": "string", "description": "Bookmark description"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags"},
                    "folder": {"type": "string", "description": "Folder name"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_bookmarks",
            "description": "Search bookmarks by query, tags, folder, or favorite status",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                    "folder": {"type": "string", "description": "Filter by folder"},
                    "favorite": {"type": "boolean", "description": "Filter by favorite status"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_bookmark",
            "description": "Delete a bookmark by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "bookmark_id": {"type": "integer", "description": "ID of bookmark to delete"}
                },
                "required": ["bookmark_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_bookmarks",
            "description": "Export all bookmarks in the specified format",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {"type": "string", "enum": ["json", "html", "csv"], "default": "json"}
                }
            }
        }
    }
]

# Tool metadata
TOOL_INFO = {
    "name": "bookmarks_manager",
    "description": "OpenAI-compatible bookmarks manager with tagging and search",
    "version": "1.0.0",
    "author": "CBW Agents",
    "openai_compatible": True,
    "capabilities": [
        "add_bookmark",
        "search_bookmarks",
        "update_bookmark",
        "delete_bookmark",
        "get_all_tags",
        "export_bookmarks"
    ],
    "requirements": ["sqlite3", "pathlib", "json"],
    "safety_features": [
        "SQLite database storage",
        "Data validation",
        "URL deduplication",
        "Error handling"
    ]
}
