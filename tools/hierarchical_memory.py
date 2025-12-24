#!/usr/bin/env python3
"""
Hierarchical Memory Tool

Implements a hierarchical memory system with multiple levels of abstraction,
automatic summarization, and context-aware retrieval.

OpenAI Compatible: Yes
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HierarchicalMemoryTool:
    """
    Multi-level hierarchical memory system.
    
    Levels:
    1. Working Memory (immediate, temporary)
    2. Short-term Memory (recent, contextual)
    3. Long-term Memory (summarized, persistent)
    4. Semantic Memory (concepts, knowledge)
    5. Episodic Memory (events, experiences)
    """
    
    def __init__(self, db_path: str = "./hierarchical_memory.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
        logger.info(f"HierarchicalMemory initialized: db={db_path}")
    
    def _initialize_database(self):
        """Initialize database with memory hierarchy."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_hierarchy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                context TEXT,
                parent_id INTEGER,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_accessed TEXT,
                promoted_at TEXT,
                metadata TEXT,
                FOREIGN KEY (parent_id) REFERENCES memory_hierarchy(id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_level ON memory_hierarchy(level)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_parent ON memory_hierarchy(parent_id)
        ''')
        
        self.conn.commit()
    
    def store_memory(self, content: str, level: str = "working",
                    context: Optional[str] = None, importance: float = 0.5,
                    parent_id: Optional[int] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Store a memory at specified hierarchy level."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat()
            
            # Generate summary for higher levels
            summary = self._generate_summary(content) if level in ["long_term", "semantic"] else None
            
            cursor.execute('''
                INSERT INTO memory_hierarchy 
                (level, content, summary, context, parent_id, importance, created_at, last_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (level, content, summary, context, parent_id, importance, now, now, 
                  json.dumps(metadata or {})))
            
            memory_id = cursor.lastrowid
            self.conn.commit()
            
            # Auto-promote if importance is high
            if importance >= 0.8 and level == "working":
                self._promote_memory(memory_id, "short_term")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "level": level,
                "importance": importance
            }
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return {"success": False, "error": str(e)}
    
    def retrieve_memory(self, level: Optional[str] = None, 
                       context: Optional[str] = None,
                       min_importance: float = 0.0,
                       limit: int = 10) -> Dict[str, Any]:
        """Retrieve memories from hierarchy."""
        try:
            cursor = self.conn.cursor()
            
            sql = 'SELECT * FROM memory_hierarchy WHERE importance >= ?'
            params = [min_importance]
            
            if level:
                sql += ' AND level = ?'
                params.append(level)
            
            if context:
                sql += ' AND context LIKE ?'
                params.append(f'%{context}%')
            
            sql += ' ORDER BY importance DESC, last_accessed DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            memories = []
            
            for row in cursor.fetchall():
                memory = dict(row)
                memory['metadata'] = json.loads(memory['metadata'])
                
                # Update access count
                cursor.execute('''
                    UPDATE memory_hierarchy 
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), memory['id']))
                
                memories.append(memory)
            
            self.conn.commit()
            
            return {
                "success": True,
                "memories": memories,
                "count": len(memories)
            }
        except Exception as e:
            logger.error(f"Error retrieving memory: {e}")
            return {"success": False, "error": str(e)}
    
    def promote_memory(self, memory_id: int, target_level: str) -> Dict[str, Any]:
        """Manually promote memory to higher level."""
        return self._promote_memory(memory_id, target_level)
    
    def _promote_memory(self, memory_id: int, target_level: str) -> Dict[str, Any]:
        """Internal promotion logic."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM memory_hierarchy WHERE id = ?', (memory_id,))
            memory = cursor.fetchone()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            # Create summarized version at higher level
            summary = self._generate_summary(memory['content'])
            
            cursor.execute('''
                UPDATE memory_hierarchy
                SET level = ?, summary = ?, promoted_at = ?
                WHERE id = ?
            ''', (target_level, summary, datetime.now().isoformat(), memory_id))
            
            self.conn.commit()
            
            return {
                "success": True,
                "memory_id": memory_id,
                "from_level": memory['level'],
                "to_level": target_level
            }
        except Exception as e:
            logger.error(f"Error promoting memory: {e}")
            return {"success": False, "error": str(e)}
    
    def consolidate_memories(self, level: str = "short_term", 
                           time_window_hours: int = 24) -> Dict[str, Any]:
        """Consolidate related memories into higher-level abstractions."""
        try:
            cursor = self.conn.cursor()
            
            cutoff = (datetime.now() - timedelta(hours=time_window_hours)).isoformat()
            
            cursor.execute('''
                SELECT * FROM memory_hierarchy 
                WHERE level = ? AND created_at >= ?
                ORDER BY created_at
            ''', (level, cutoff))
            
            memories = cursor.fetchall()
            
            if len(memories) < 3:
                return {
                    "success": True,
                    "consolidated": 0,
                    "message": "Not enough memories to consolidate"
                }
            
            # Group by context and create consolidated memory
            context_groups = {}
            for memory in memories:
                ctx = memory['context'] or 'general'
                if ctx not in context_groups:
                    context_groups[ctx] = []
                context_groups[ctx].append(memory)
            
            consolidated_count = 0
            for context, group in context_groups.items():
                if len(group) >= 3:
                    # Create consolidated memory
                    contents = [m['content'] for m in group]
                    consolidated_content = self._consolidate_content(contents)
                    avg_importance = sum(m['importance'] for m in group) / len(group)
                    
                    cursor.execute('''
                        INSERT INTO memory_hierarchy
                        (level, content, summary, context, importance, created_at, last_accessed, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', ('long_term', consolidated_content, 
                          self._generate_summary(consolidated_content),
                          context, avg_importance, datetime.now().isoformat(),
                          datetime.now().isoformat(), 
                          json.dumps({"consolidated_from": len(group)})))
                    
                    consolidated_count += 1
            
            self.conn.commit()
            
            return {
                "success": True,
                "consolidated": consolidated_count,
                "total_memories_processed": len(memories)
            }
        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_summary(self, content: str, max_length: int = 100) -> str:
        """Generate summary of content."""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def _consolidate_content(self, contents: List[str]) -> str:
        """Consolidate multiple contents into one."""
        return " | ".join(contents[:5])  # Take first 5 for consolidation
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory hierarchy."""
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            for level in ["working", "short_term", "long_term", "semantic", "episodic"]:
                cursor.execute('''
                    SELECT COUNT(*) as count, AVG(importance) as avg_importance,
                           AVG(access_count) as avg_access
                    FROM memory_hierarchy WHERE level = ?
                ''', (level,))
                row = cursor.fetchone()
                stats[level] = dict(row)
            
            return {"success": True, "stats": stats}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"success": False, "error": str(e)}


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Store a memory at specified hierarchy level",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Memory content"},
                    "level": {
                        "type": "string",
                        "enum": ["working", "short_term", "long_term", "semantic", "episodic"],
                        "description": "Memory hierarchy level"
                    },
                    "context": {"type": "string", "description": "Context of the memory"},
                    "importance": {"type": "number", "description": "Importance score (0-1)"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_memory",
            "description": "Retrieve memories from hierarchy",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "string", "description": "Filter by level"},
                    "context": {"type": "string", "description": "Filter by context"},
                    "min_importance": {"type": "number", "description": "Minimum importance"},
                    "limit": {"type": "integer", "description": "Max results"}
                }
            }
        }
    }
]


if __name__ == "__main__":
    import tempfile
    import os
    
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    try:
        hm = HierarchicalMemoryTool(db_path=db_path)
        
        print("=== Storing Memories ===")
        hm.store_memory("Python is great", "working", context="programming", importance=0.7)
        hm.store_memory("AI is transforming tech", "short_term", context="technology", importance=0.9)
        
        print("\n=== Retrieving Memories ===")
        result = hm.retrieve_memory(min_importance=0.5)
        print(json.dumps(result, indent=2))
        
        print("\n=== Memory Stats ===")
        result = hm.get_memory_stats()
        print(json.dumps(result, indent=2))
        
    finally:
        os.unlink(db_path)
