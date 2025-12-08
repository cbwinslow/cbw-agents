#!/usr/bin/env python3
"""
Task Decomposer Tool

Breaks down complex tasks into smaller, manageable subtasks with dependencies
and execution order. Essential for multi-agent problem solving.

OpenAI Compatible: Yes
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class DependencyType(Enum):
    """Dependency types between tasks."""
    REQUIRED = "required"  # Must complete before
    OPTIONAL = "optional"  # Should complete before but not required
    PARALLEL = "parallel"  # Can run in parallel


class TaskDecomposerTool:
    """
    Task decomposition and dependency management.
    
    Features:
    - Hierarchical task breakdown
    - Dependency tracking
    - Execution order determination
    - Complexity estimation
    - Parallel task identification
    - Critical path analysis
    """
    
    def __init__(self, db_path: str = "./task_decomposer.db"):
        """
        Initialize task decomposer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
        
        logger.info(f"TaskDecomposer initialized: db={db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    parent_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    complexity TEXT NOT NULL,
                    estimated_hours REAL,
                    required_capabilities TEXT,
                    acceptance_criteria TEXT,
                    created_at TEXT NOT NULL,
                    depth_level INTEGER DEFAULT 0
                )
            ''')
            
            # Create dependencies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    depends_on_task_id TEXT NOT NULL,
                    dependency_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(task_id, depends_on_task_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(task_id)
                )
            ''')
            
            self.conn.commit()
            logger.info("Task decomposer database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def decompose_task(self, task_id: str, title: str, description: str,
                      complexity: str = "complex", 
                      decomposition_strategy: str = "hierarchical") -> Dict[str, Any]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Detailed description
            complexity: Task complexity
            decomposition_strategy: Strategy to use (hierarchical, sequential, parallel)
            
        Returns:
            Decomposed subtasks
        """
        try:
            # Validate complexity
            if complexity not in [c.value for c in TaskComplexity]:
                return {
                    "success": False,
                    "error": f"Invalid complexity: {complexity}"
                }
            
            # Create parent task
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task_id, parent_id, title, description, complexity, created_at, depth_level)
                VALUES (?, NULL, ?, ?, ?, ?, 0)
            ''', (task_id, title, description, complexity, datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Generate subtasks based on strategy
            if decomposition_strategy == "hierarchical":
                subtasks = self._decompose_hierarchical(task_id, description, complexity)
            elif decomposition_strategy == "sequential":
                subtasks = self._decompose_sequential(task_id, description)
            elif decomposition_strategy == "parallel":
                subtasks = self._decompose_parallel(task_id, description)
            else:
                subtasks = self._decompose_hierarchical(task_id, description, complexity)
            
            return {
                "success": True,
                "task_id": task_id,
                "title": title,
                "complexity": complexity,
                "subtasks": subtasks,
                "total_subtasks": len(subtasks),
                "decomposition_strategy": decomposition_strategy
            }
            
        except Exception as e:
            logger.error(f"Error decomposing task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _decompose_hierarchical(self, parent_id: str, description: str, 
                               complexity: str) -> List[Dict[str, Any]]:
        """
        Decompose task hierarchically.
        
        This is a simplified heuristic decomposition. In practice, this would
        use LLM reasoning or more sophisticated algorithms.
        """
        subtasks = []
        
        # Determine number of subtasks based on complexity
        # These values represent typical project phases and can be adjusted
        # Simple: 2 phases (design, implement)
        # Moderate: 3 phases (design, implement, test)
        # Complex: 5 phases (research, design, implement, test, document)
        # Very Complex: 8 phases (full SDLC)
        SUBTASK_COUNT_BY_COMPLEXITY = {
            TaskComplexity.SIMPLE.value: 2,
            TaskComplexity.MODERATE.value: 3,
            TaskComplexity.COMPLEX.value: 5,
            TaskComplexity.VERY_COMPLEX.value: 8
        }
        num_subtasks = SUBTASK_COUNT_BY_COMPLEXITY.get(complexity, 3)
        
        # Common task phases
        phases = [
            "research_and_planning",
            "design_and_architecture",
            "implementation_core",
            "implementation_features",
            "testing_and_validation",
            "documentation",
            "review_and_refinement",
            "deployment_and_monitoring"
        ]
        
        for i in range(min(num_subtasks, len(phases))):
            subtask_id = f"{parent_id}.{i+1}"
            phase = phases[i]
            
            subtask = {
                "task_id": subtask_id,
                "parent_id": parent_id,
                "title": f"{phase.replace('_', ' ').title()}",
                "description": f"Complete the {phase.replace('_', ' ')} phase",
                "complexity": TaskComplexity.MODERATE.value,
                "estimated_hours": 4.0,
                "depth_level": 1
            }
            
            # Add to database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (task_id, parent_id, title, description, complexity, 
                                 estimated_hours, created_at, depth_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subtask_id, parent_id, subtask["title"], subtask["description"],
                  subtask["complexity"], subtask["estimated_hours"], 
                  datetime.now().isoformat(), 1))
            
            # Add dependencies (sequential by default)
            if i > 0:
                prev_subtask_id = f"{parent_id}.{i}"
                self.add_dependency(subtask_id, prev_subtask_id, DependencyType.REQUIRED.value)
            
            subtasks.append(subtask)
        
        self.conn.commit()
        return subtasks
    
    def _decompose_sequential(self, parent_id: str, description: str) -> List[Dict[str, Any]]:
        """Decompose into sequential steps."""
        return self._decompose_hierarchical(parent_id, description, TaskComplexity.MODERATE.value)
    
    def _decompose_parallel(self, parent_id: str, description: str) -> List[Dict[str, Any]]:
        """Decompose into parallel tasks."""
        subtasks = self._decompose_hierarchical(parent_id, description, TaskComplexity.MODERATE.value)
        
        # Remove dependencies to make them parallel
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM dependencies 
            WHERE task_id IN (SELECT task_id FROM tasks WHERE parent_id = ?)
        ''', (parent_id,))
        self.conn.commit()
        
        return subtasks
    
    def add_dependency(self, task_id: str, depends_on_task_id: str,
                      dependency_type: str = "required") -> Dict[str, Any]:
        """
        Add dependency between tasks.
        
        Args:
            task_id: Task that has the dependency
            depends_on_task_id: Task that must be completed first
            dependency_type: Type of dependency
            
        Returns:
            Success status
        """
        try:
            # Validate dependency type
            if dependency_type not in [d.value for d in DependencyType]:
                return {
                    "success": False,
                    "error": f"Invalid dependency type: {dependency_type}"
                }
            
            # Check for circular dependencies
            if self._creates_cycle(task_id, depends_on_task_id):
                return {
                    "success": False,
                    "error": "This dependency would create a circular reference"
                }
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO dependencies (task_id, depends_on_task_id, dependency_type, created_at)
                VALUES (?, ?, ?, ?)
            ''', (task_id, depends_on_task_id, dependency_type, datetime.now().isoformat()))
            
            self.conn.commit()
            
            return {
                "success": True,
                "task_id": task_id,
                "depends_on": depends_on_task_id,
                "dependency_type": dependency_type
            }
            
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": "Dependency already exists"
            }
        except Exception as e:
            logger.error(f"Error adding dependency: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _creates_cycle(self, from_task: str, to_task: str) -> bool:
        """Check if adding dependency would create a cycle."""
        visited = set()
        
        def has_path(start: str, end: str) -> bool:
            if start == end:
                return True
            if start in visited:
                return False
            
            visited.add(start)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT depends_on_task_id FROM dependencies WHERE task_id = ?
            ''', (start,))
            
            for row in cursor.fetchall():
                if has_path(row['depends_on_task_id'], end):
                    return True
            
            return False
        
        # Check if to_task already has path to from_task
        return has_path(to_task, from_task)
    
    def get_execution_order(self, parent_task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution order for tasks respecting dependencies.
        
        Args:
            parent_task_id: Get order for subtasks of this parent (None for all)
            
        Returns:
            Ordered task list and parallel groups
        """
        try:
            cursor = self.conn.cursor()
            
            # Get all tasks
            if parent_task_id:
                cursor.execute('''
                    SELECT task_id FROM tasks WHERE parent_id = ?
                ''', (parent_task_id,))
            else:
                cursor.execute('''
                    SELECT task_id FROM tasks WHERE parent_id IS NULL
                ''')
            
            task_ids = [row['task_id'] for row in cursor.fetchall()]
            
            if not task_ids:
                return {
                    "success": True,
                    "execution_order": [],
                    "parallel_groups": []
                }
            
            # Build dependency graph
            graph = {tid: [] for tid in task_ids}
            in_degree = {tid: 0 for tid in task_ids}
            
            for task_id in task_ids:
                cursor.execute('''
                    SELECT depends_on_task_id FROM dependencies 
                    WHERE task_id = ? AND dependency_type = ?
                ''', (task_id, DependencyType.REQUIRED.value))
                
                for row in cursor.fetchall():
                    dep_id = row['depends_on_task_id']
                    if dep_id in graph:
                        graph[dep_id].append(task_id)
                        in_degree[task_id] += 1
            
            # Topological sort with level detection
            levels = []
            current_level = [tid for tid in task_ids if in_degree[tid] == 0]
            
            while current_level:
                levels.append(current_level[:])
                next_level = []
                
                for task_id in current_level:
                    for dependent in graph[task_id]:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_level.append(dependent)
                
                current_level = next_level
            
            # Flatten for execution order
            execution_order = [tid for level in levels for tid in level]
            
            return {
                "success": True,
                "execution_order": execution_order,
                "parallel_groups": levels,
                "total_levels": len(levels)
            }
            
        except Exception as e:
            logger.error(f"Error getting execution order: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task_tree(self, root_task_id: str) -> Dict[str, Any]:
        """
        Get hierarchical task tree.
        
        Args:
            root_task_id: Root task identifier
            
        Returns:
            Task tree structure
        """
        try:
            cursor = self.conn.cursor()
            
            def build_tree(task_id: str) -> Dict[str, Any]:
                # Get task details
                cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
                task = cursor.fetchone()
                
                if not task:
                    return None
                
                task_dict = dict(task)
                
                # Get dependencies
                cursor.execute('''
                    SELECT depends_on_task_id, dependency_type 
                    FROM dependencies WHERE task_id = ?
                ''', (task_id,))
                task_dict['dependencies'] = [dict(row) for row in cursor.fetchall()]
                
                # Get children
                cursor.execute('SELECT task_id FROM tasks WHERE parent_id = ?', (task_id,))
                children_ids = [row['task_id'] for row in cursor.fetchall()]
                
                task_dict['children'] = [build_tree(cid) for cid in children_ids]
                
                return task_dict
            
            tree = build_tree(root_task_id)
            
            if not tree:
                return {
                    "success": False,
                    "error": f"Task {root_task_id} not found"
                }
            
            return {
                "success": True,
                "task_tree": tree
            }
            
        except Exception as e:
            logger.error(f"Error getting task tree: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def estimate_total_effort(self, task_id: str) -> Dict[str, Any]:
        """
        Estimate total effort for task and all subtasks.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Effort estimation
        """
        try:
            cursor = self.conn.cursor()
            
            # Get all subtasks recursively
            cursor.execute('''
                WITH RECURSIVE task_hierarchy AS (
                    SELECT task_id, estimated_hours FROM tasks WHERE task_id = ?
                    UNION ALL
                    SELECT t.task_id, t.estimated_hours
                    FROM tasks t
                    INNER JOIN task_hierarchy th ON t.parent_id = th.task_id
                )
                SELECT SUM(estimated_hours) as total_hours, COUNT(*) as task_count
                FROM task_hierarchy
            ''', (task_id,))
            
            result = cursor.fetchone()
            total_hours = result['total_hours'] or 0
            task_count = result['task_count']
            
            # Get critical path
            execution_order = self.get_execution_order(task_id)
            critical_path_length = execution_order.get('total_levels', 0) if execution_order['success'] else 0
            
            return {
                "success": True,
                "task_id": task_id,
                "total_estimated_hours": total_hours,
                "total_tasks": task_count,
                "critical_path_length": critical_path_length,
                "estimated_days": round(total_hours / 8, 1)
            }
            
        except Exception as e:
            logger.error(f"Error estimating effort: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Task decomposer database connection closed")


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "decompose_task",
            "description": "Break down a complex task into subtasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Unique task identifier"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Detailed task description"},
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "moderate", "complex", "very_complex"],
                        "description": "Task complexity level"
                    },
                    "decomposition_strategy": {
                        "type": "string",
                        "enum": ["hierarchical", "sequential", "parallel"],
                        "description": "Decomposition strategy"
                    }
                },
                "required": ["task_id", "title", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_dependency",
            "description": "Add dependency between two tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task that has the dependency"},
                    "depends_on_task_id": {"type": "string", "description": "Task that must complete first"},
                    "dependency_type": {
                        "type": "string",
                        "enum": ["required", "optional", "parallel"],
                        "description": "Type of dependency"
                    }
                },
                "required": ["task_id", "depends_on_task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_execution_order",
            "description": "Get optimal execution order respecting dependencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_task_id": {"type": "string", "description": "Parent task to get order for"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_total_effort",
            "description": "Estimate total effort for task and subtasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"}
                },
                "required": ["task_id"]
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
        decomposer = TaskDecomposerTool(db_path=db_path)
        
        # Decompose a complex task
        print("\n=== Decomposing Task ===")
        result = decomposer.decompose_task(
            task_id="proj-001",
            title="Build Multi-Agent System",
            description="Build a democratic multi-agent system with voting and delegation",
            complexity="very_complex",
            decomposition_strategy="hierarchical"
        )
        print(json.dumps(result, indent=2))
        
        # Get execution order
        print("\n=== Execution Order ===")
        result = decomposer.get_execution_order("proj-001")
        print(json.dumps(result, indent=2))
        
        # Estimate effort
        print("\n=== Effort Estimation ===")
        result = decomposer.estimate_total_effort("proj-001")
        print(json.dumps(result, indent=2))
        
        # Get task tree
        print("\n=== Task Tree ===")
        result = decomposer.get_task_tree("proj-001")
        print(json.dumps(result, indent=2))
        
        decomposer.close()
        
    finally:
        os.unlink(db_path)
        print(f"\nCleaned up temporary database: {db_path}")
