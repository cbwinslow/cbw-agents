#!/usr/bin/env python3
"""
Long-Term Memory Tool

Manages persistent memory for AI agents, including historical data storage,
knowledge base, and memory retrieval with vector embeddings.

OpenAI Compatible: Yes
"""

import json
import sqlite3
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LongTermMemoryTool:
    """
    Long-term persistent memory management for AI agents.
    
    Features:
    - Persistent storage using SQLite
    - Memory indexing and search
    - Importance-based retention
    - Memory archival
    - Full-text search
    - Tag-based organization
    """
    
    def __init__(self, db_path: str = "./long_term_memory.db", max_entries: int = 10000):
        """
        Initialize long-term memory.
        
        Args:
            db_path: Path to SQLite database
            max_entries: Maximum number of entries before pruning
        """
        self.db_path = db_path
        self.max_entries = max_entries
        self.conn = None
        self._initialize_database()
        
        logger.info(f"LongTermMemory initialized: db={db_path}, max_entries={max_entries}")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create memories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_type TEXT,
                    importance REAL DEFAULT 0.5,
                    context TEXT,
                    tags TEXT,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    archived BOOLEAN DEFAULT 0
                )
            ''')
            
            # Create full-text search index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    content, context, tags, content=memories, content_rowid=id
                )
            ''')
            
            # Create triggers to keep FTS in sync
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, content, context, tags)
                    VALUES (new.id, new.content, new.context, new.tags);
                END;
            ''')
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    DELETE FROM memories_fts WHERE rowid = old.id;
                END;
            ''')
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                    UPDATE memories_fts SET content = new.content, context = new.context, tags = new.tags
                    WHERE rowid = old.id;
                END;
            ''')
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def store(self, content: str, content_type: str = "general", importance: float = 0.5,
              context: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Store a memory in long-term storage.
        
        Args:
            content: Memory content
            content_type: Type of content (general, conversation, knowledge, etc.)
            importance: Importance score (0.0 to 1.0)
            context: Contextual information
            tags: List of tags for organization
            
        Returns:
            Success status and memory ID
        """
        try:
            # Validate importance
            importance = max(0.0, min(1.0, importance))
            
            # Convert tags to JSON
            tags_json = json.dumps(tags or [])
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO memories (content, content_type, importance, context, tags, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (content, content_type, importance, context, tags_json, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            memory_id = cursor.lastrowid
            self.conn.commit()
            
            # Check if pruning needed
            self._prune_if_needed()
            
            return {
                "success": True,
                "memory_id": memory_id,
                "content_type": content_type,
                "importance": importance
            }
            
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def retrieve(self, memory_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Memory data
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM memories WHERE id = ?
            ''', (memory_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "error": f"Memory {memory_id} not found"
                }
            
            # Update access tracking
            cursor.execute('''
                UPDATE memories 
                SET last_accessed = ?, access_count = access_count + 1
                WHERE id = ?
            ''', (datetime.now().isoformat(), memory_id))
            self.conn.commit()
            
            memory = dict(row)
            memory['tags'] = json.loads(memory['tags']) if memory['tags'] else []
            
            return {
                "success": True,
                "memory": memory
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search(self, query: str, content_type: Optional[str] = None,
               min_importance: float = 0.0, tags: Optional[List[str]] = None,
               limit: int = 10) -> Dict[str, Any]:
        """
        Search memories using full-text search.
        
        Args:
            query: Search query
            content_type: Filter by content type
            min_importance: Minimum importance score
            tags: Filter by tags (any match)
            limit: Maximum results to return
            
        Returns:
            Matching memories
        """
        try:
            cursor = self.conn.cursor()
            
            # Build query
            sql = '''
                SELECT m.*, rank
                FROM memories m
                JOIN memories_fts ON m.id = memories_fts.rowid
                WHERE memories_fts MATCH ?
                AND m.importance >= ?
            '''
            params = [query, min_importance]
            
            if content_type:
                sql += ' AND m.content_type = ?'
                params.append(content_type)
            
            if tags:
                # Check if any tag matches
                tag_conditions = ' OR '.join(['m.tags LIKE ?' for _ in tags])
                sql += f' AND ({tag_conditions})'
                params.extend([f'%{tag}%' for tag in tags])
            
            sql += ' ORDER BY rank, m.importance DESC, m.last_accessed DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory = dict(row)
                memory['tags'] = json.loads(memory['tags']) if memory['tags'] else []
                memories.append(memory)
            
            return {
                "success": True,
                "query": query,
                "count": len(memories),
                "memories": memories
            }
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_by_tags(self, tags: List[str], match_all: bool = False, limit: int = 50) -> Dict[str, Any]:
        """
        Retrieve memories by tags.
        
        Args:
            tags: List of tags to search for
            match_all: If True, memory must have all tags; if False, any tag matches
            limit: Maximum results to return
            
        Returns:
            Matching memories
        """
        try:
            cursor = self.conn.cursor()
            
            if match_all:
                # All tags must match
                conditions = ' AND '.join(['tags LIKE ?' for _ in tags])
                sql = f'''
                    SELECT * FROM memories 
                    WHERE {conditions}
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                '''
                params = [f'%{tag}%' for tag in tags] + [limit]
            else:
                # Any tag matches
                conditions = ' OR '.join(['tags LIKE ?' for _ in tags])
                sql = f'''
                    SELECT * FROM memories 
                    WHERE {conditions}
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                '''
                params = [f'%{tag}%' for tag in tags] + [limit]
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory = dict(row)
                memory['tags'] = json.loads(memory['tags']) if memory['tags'] else []
                memories.append(memory)
            
            return {
                "success": True,
                "tags": tags,
                "match_all": match_all,
                "count": len(memories),
                "memories": memories
            }
            
        except Exception as e:
            logger.error(f"Error getting memories by tags: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_recent(self, days: int = 7, content_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get recent memories.
        
        Args:
            days: Number of days to look back
            content_type: Filter by content type
            limit: Maximum results
            
        Returns:
            Recent memories
        """
        try:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor = self.conn.cursor()
            sql = '''
                SELECT * FROM memories 
                WHERE created_at >= ?
            '''
            params = [cutoff]
            
            if content_type:
                sql += ' AND content_type = ?'
                params.append(content_type)
            
            sql += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory = dict(row)
                memory['tags'] = json.loads(memory['tags']) if memory['tags'] else []
                memories.append(memory)
            
            return {
                "success": True,
                "days": days,
                "count": len(memories),
                "memories": memories
            }
            
        except Exception as e:
            logger.error(f"Error getting recent memories: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_importance(self, memory_id: int, importance: float) -> Dict[str, Any]:
        """
        Update memory importance score.
        
        Args:
            memory_id: Memory identifier
            importance: New importance score (0.0 to 1.0)
            
        Returns:
            Success status
        """
        try:
            importance = max(0.0, min(1.0, importance))
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE memories SET importance = ? WHERE id = ?
            ''', (importance, memory_id))
            
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Memory {memory_id} not found"
                }
            
            self.conn.commit()
            
            return {
                "success": True,
                "memory_id": memory_id,
                "importance": importance
            }
            
        except Exception as e:
            logger.error(f"Error updating importance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete(self, memory_id: int) -> Dict[str, Any]:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory identifier
            
        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM memories WHERE id = ?', (memory_id,))
            
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Memory {memory_id} not found"
                }
            
            self.conn.commit()
            
            return {
                "success": True,
                "memory_id": memory_id
            }
            
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prune_if_needed(self):
        """Prune old/low-importance memories if limit exceeded."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM memories WHERE archived = 0')
            count = cursor.fetchone()['count']
            
            if count > self.max_entries:
                # Calculate how many to remove
                to_remove = count - self.max_entries
                
                # Remove lowest importance, least accessed memories
                cursor.execute('''
                    DELETE FROM memories 
                    WHERE id IN (
                        SELECT id FROM memories 
                        WHERE archived = 0
                        ORDER BY importance ASC, access_count ASC, last_accessed ASC
                        LIMIT ?
                    )
                ''', (to_remove,))
                
                self.conn.commit()
                logger.info(f"Pruned {to_remove} memories")
                
        except Exception as e:
            logger.error(f"Error pruning memories: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory storage statistics.
        
        Returns:
            Storage statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Total count
            cursor.execute('SELECT COUNT(*) as count FROM memories')
            total_count = cursor.fetchone()['count']
            
            # By content type
            cursor.execute('''
                SELECT content_type, COUNT(*) as count 
                FROM memories 
                GROUP BY content_type
            ''')
            by_type = {row['content_type']: row['count'] for row in cursor.fetchall()}
            
            # Importance distribution
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN importance >= 0.8 THEN 'high'
                        WHEN importance >= 0.5 THEN 'medium'
                        ELSE 'low'
                    END as category,
                    COUNT(*) as count
                FROM memories
                GROUP BY category
            ''')
            by_importance = {row['category']: row['count'] for row in cursor.fetchall()}
            
            # Recent activity
            cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('SELECT COUNT(*) as count FROM memories WHERE created_at >= ?', (cutoff,))
            recent_count = cursor.fetchone()['count']
            
            return {
                "success": True,
                "total_memories": total_count,
                "max_entries": self.max_entries,
                "usage_percent": (total_count / self.max_entries) * 100,
                "by_content_type": by_type,
                "by_importance": by_importance,
                "recent_7days": recent_count
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Store information in long-term memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to remember"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Type of content (general, conversation, knowledge, etc.)"
                    },
                    "importance": {
                        "type": "number",
                        "description": "Importance score from 0.0 to 1.0",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "context": {
                        "type": "string",
                        "description": "Contextual information about the memory"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for organizing the memory"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memories",
            "description": "Search long-term memory using full-text search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Filter by content type"
                    },
                    "min_importance": {
                        "type": "number",
                        "description": "Minimum importance score"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memories_by_tags",
            "description": "Retrieve memories by their tags",
            "parameters": {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to search for"
                    },
                    "match_all": {
                        "type": "boolean",
                        "description": "If true, memory must have all tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results"
                    }
                },
                "required": ["tags"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_memories",
            "description": "Get memories from recent days",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of days to look back"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Filter by content type"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_stats",
            "description": "Get statistics about long-term memory storage",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


if __name__ == "__main__":
    # Example usage
    import tempfile
    import os
    
    # Use temporary database for testing
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    try:
        memory = LongTermMemoryTool(db_path=db_path, max_entries=100)
        
        # Store some memories
        print("\n=== Storing Memories ===")
        result = memory.store(
            content="Python is a high-level programming language",
            content_type="knowledge",
            importance=0.8,
            context="Programming languages discussion",
            tags=["python", "programming", "knowledge"]
        )
        print(json.dumps(result, indent=2))
        
        result = memory.store(
            content="User prefers detailed explanations",
            content_type="preference",
            importance=0.9,
            tags=["user-preference", "communication"]
        )
        print(json.dumps(result, indent=2))
        
        # Search memories
        print("\n=== Searching Memories ===")
        result = memory.search("python programming", limit=5)
        print(json.dumps(result, indent=2))
        
        # Get by tags
        print("\n=== Getting by Tags ===")
        result = memory.get_by_tags(["python"], limit=10)
        print(json.dumps(result, indent=2))
        
        # Get stats
        print("\n=== Memory Statistics ===")
        result = memory.get_stats()
        print(json.dumps(result, indent=2))
        
        memory.close()
        
    finally:
        # Clean up
        os.unlink(db_path)
        print(f"\nCleaned up temporary database: {db_path}")
