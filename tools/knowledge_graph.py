#!/usr/bin/env python3
"""
Knowledge Graph Tool

Manages a graph-based knowledge representation system with relationships,
entity extraction, and graph querying capabilities.

OpenAI Compatible: Yes
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphTool:
    """
    Graph-based knowledge management system.
    
    Features:
    - Entity management
    - Relationship tracking
    - Graph traversal
    - Query and search
    - Knowledge inference
    """
    
    def __init__(self, db_path: str = "./knowledge_graph.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
        logger.info(f"KnowledgeGraph initialized: db={db_path}")
    
    def _initialize_database(self):
        """Initialize database with entities and relationships."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT NOT NULL,
                properties TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                properties TEXT,
                strength REAL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            )
        ''')
        
        self.conn.commit()
    
    def add_entity(self, name: str, entity_type: str, properties: Optional[Dict] = None) -> Dict[str, Any]:
        """Add an entity to the knowledge graph."""
        try:
            cursor = self.conn.cursor()
            props_json = json.dumps(properties or {})
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO entities (name, entity_type, properties, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, entity_type, props_json, now, now))
            
            self.conn.commit()
            entity_id = cursor.lastrowid
            
            return {
                "success": True,
                "entity_id": entity_id,
                "name": name,
                "entity_type": entity_type
            }
        except Exception as e:
            logger.error(f"Error adding entity: {e}")
            return {"success": False, "error": str(e)}
    
    def add_relationship(self, source_name: str, target_name: str, 
                        relationship_type: str, strength: float = 1.0,
                        properties: Optional[Dict] = None) -> Dict[str, Any]:
        """Add a relationship between two entities."""
        try:
            cursor = self.conn.cursor()
            
            # Get entity IDs
            cursor.execute('SELECT id FROM entities WHERE name = ?', (source_name,))
            source = cursor.fetchone()
            cursor.execute('SELECT id FROM entities WHERE name = ?', (target_name,))
            target = cursor.fetchone()
            
            if not source or not target:
                return {"success": False, "error": "Source or target entity not found"}
            
            props_json = json.dumps(properties or {})
            
            cursor.execute('''
                INSERT INTO relationships (source_id, target_id, relationship_type, strength, properties, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (source['id'], target['id'], relationship_type, strength, props_json, datetime.now().isoformat()))
            
            self.conn.commit()
            
            return {
                "success": True,
                "source": source_name,
                "target": target_name,
                "relationship": relationship_type,
                "strength": strength
            }
        except Exception as e:
            logger.error(f"Error adding relationship: {e}")
            return {"success": False, "error": str(e)}
    
    def query_entity(self, name: str, include_relationships: bool = True) -> Dict[str, Any]:
        """Query an entity and its relationships."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM entities WHERE name = ?', (name,))
            entity = cursor.fetchone()
            
            if not entity:
                return {"success": False, "error": f"Entity '{name}' not found"}
            
            result = dict(entity)
            result['properties'] = json.loads(result['properties'])
            
            if include_relationships:
                # Get outgoing relationships
                cursor.execute('''
                    SELECT r.*, e.name as target_name, e.entity_type as target_type
                    FROM relationships r
                    JOIN entities e ON r.target_id = e.id
                    WHERE r.source_id = ?
                ''', (entity['id'],))
                result['outgoing'] = [dict(row) for row in cursor.fetchall()]
                
                # Get incoming relationships
                cursor.execute('''
                    SELECT r.*, e.name as source_name, e.entity_type as source_type
                    FROM relationships r
                    JOIN entities e ON r.source_id = e.id
                    WHERE r.target_id = ?
                ''', (entity['id'],))
                result['incoming'] = [dict(row) for row in cursor.fetchall()]
            
            return {"success": True, "entity": result}
        except Exception as e:
            logger.error(f"Error querying entity: {e}")
            return {"success": False, "error": str(e)}
    
    def find_path(self, source_name: str, target_name: str, max_depth: int = 5) -> Dict[str, Any]:
        """Find shortest path between two entities."""
        try:
            cursor = self.conn.cursor()
            
            # Get entity IDs
            cursor.execute('SELECT id FROM entities WHERE name = ?', (source_name,))
            source = cursor.fetchone()
            cursor.execute('SELECT id FROM entities WHERE name = ?', (target_name,))
            target = cursor.fetchone()
            
            if not source or not target:
                return {"success": False, "error": "Source or target entity not found"}
            
            # BFS to find shortest path
            visited = set()
            queue = [(source['id'], [source['id']])]
            
            while queue:
                current_id, path = queue.pop(0)
                
                if current_id == target['id']:
                    # Reconstruct path with entity names
                    path_names = []
                    for entity_id in path:
                        cursor.execute('SELECT name FROM entities WHERE id = ?', (entity_id,))
                        path_names.append(cursor.fetchone()['name'])
                    
                    return {
                        "success": True,
                        "path": path_names,
                        "length": len(path_names) - 1
                    }
                
                if len(path) >= max_depth:
                    continue
                
                if current_id in visited:
                    continue
                
                visited.add(current_id)
                
                # Get neighbors
                cursor.execute('''
                    SELECT target_id FROM relationships WHERE source_id = ?
                    UNION
                    SELECT source_id FROM relationships WHERE target_id = ?
                ''', (current_id, current_id))
                
                for row in cursor.fetchall():
                    neighbor_id = row[0]
                    if neighbor_id not in visited:
                        queue.append((neighbor_id, path + [neighbor_id]))
            
            return {"success": True, "path": None, "message": "No path found"}
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return {"success": False, "error": str(e)}
    
    def get_neighbors(self, name: str, relationship_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all neighboring entities."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM entities WHERE name = ?', (name,))
            entity = cursor.fetchone()
            
            if not entity:
                return {"success": False, "error": f"Entity '{name}' not found"}
            
            sql = '''
                SELECT DISTINCT e.name, e.entity_type, r.relationship_type
                FROM relationships r
                JOIN entities e ON (r.target_id = e.id OR r.source_id = e.id)
                WHERE (r.source_id = ? OR r.target_id = ?)
                AND e.id != ?
            '''
            
            params = [entity['id'], entity['id'], entity['id']]
            
            if relationship_type:
                sql += ' AND r.relationship_type = ?'
                params.append(relationship_type)
            
            cursor.execute(sql, params)
            neighbors = [dict(row) for row in cursor.fetchall()]
            
            return {"success": True, "neighbors": neighbors, "count": len(neighbors)}
        except Exception as e:
            logger.error(f"Error getting neighbors: {e}")
            return {"success": False, "error": str(e)}


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_entity",
            "description": "Add an entity to the knowledge graph",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name"},
                    "entity_type": {"type": "string", "description": "Type of entity"},
                    "properties": {"type": "object", "description": "Additional properties"}
                },
                "required": ["name", "entity_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_relationship",
            "description": "Add a relationship between two entities",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_name": {"type": "string", "description": "Source entity name"},
                    "target_name": {"type": "string", "description": "Target entity name"},
                    "relationship_type": {"type": "string", "description": "Type of relationship"},
                    "strength": {"type": "number", "description": "Relationship strength (0-1)"}
                },
                "required": ["source_name", "target_name", "relationship_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_entity",
            "description": "Query an entity and its relationships",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name"},
                    "include_relationships": {"type": "boolean", "description": "Include relationships"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_path",
            "description": "Find shortest path between two entities",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_name": {"type": "string", "description": "Source entity"},
                    "target_name": {"type": "string", "description": "Target entity"},
                    "max_depth": {"type": "integer", "description": "Maximum path length"}
                },
                "required": ["source_name", "target_name"]
            }
        }
    }
]


if __name__ == "__main__":
    # Example usage
    import tempfile
    import os
    
    db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    db_path = db_file.name
    db_file.close()
    
    try:
        kg = KnowledgeGraphTool(db_path=db_path)
        
        # Add entities
        print("=== Adding Entities ===")
        kg.add_entity("Python", "programming_language", {"paradigm": "multi-paradigm"})
        kg.add_entity("AI", "technology_domain", {"field": "computer_science"})
        kg.add_entity("Machine Learning", "technology", {"subset_of": "AI"})
        
        # Add relationships
        print("\n=== Adding Relationships ===")
        kg.add_relationship("Python", "AI", "used_in", strength=0.9)
        kg.add_relationship("Python", "Machine Learning", "used_in", strength=0.95)
        kg.add_relationship("Machine Learning", "AI", "part_of", strength=1.0)
        
        # Query entity
        print("\n=== Query Entity ===")
        result = kg.query_entity("Python")
        print(json.dumps(result, indent=2))
        
        # Find path
        print("\n=== Find Path ===")
        result = kg.find_path("Python", "AI")
        print(json.dumps(result, indent=2))
        
    finally:
        os.unlink(db_path)
        print(f"\nCleaned up: {db_path}")
