#!/usr/bin/env python3
"""
Delegation Manager Tool

Manages task delegation between agents in multi-agent systems with tracking,
accountability, and progress monitoring.

OpenAI Compatible: Yes
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status types."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DelegationManagerTool:
    """
    Delegation management for multi-agent systems.
    
    Features:
    - Task delegation with clear scope
    - Capability matching
    - Delegation chain tracking
    - Progress monitoring
    - Escalation handling
    - Feedback collection
    """
    
    def __init__(self, db_path: str = "./delegation_manager.db"):
        """
        Initialize delegation manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
        
        logger.info(f"DelegationManager initialized: db={db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create delegations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delegations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    delegator_id TEXT NOT NULL,
                    delegatee_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    requirements TEXT,
                    success_criteria TEXT,
                    created_at TEXT NOT NULL,
                    deadline TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    progress_percent REAL DEFAULT 0,
                    result TEXT,
                    feedback TEXT,
                    parent_delegation_id INTEGER,
                    FOREIGN KEY (parent_delegation_id) REFERENCES delegations(id)
                )
            ''')
            
            # Create progress updates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS progress_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    delegation_id INTEGER NOT NULL,
                    reported_by TEXT NOT NULL,
                    progress_percent REAL NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    blockers TEXT,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (delegation_id) REFERENCES delegations(id)
                )
            ''')
            
            # Create agent capabilities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_capabilities (
                    agent_id TEXT NOT NULL,
                    capability TEXT NOT NULL,
                    proficiency REAL DEFAULT 0.5,
                    verified BOOLEAN DEFAULT 0,
                    PRIMARY KEY (agent_id, capability)
                )
            ''')
            
            self.conn.commit()
            logger.info("Delegation database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def register_capability(self, agent_id: str, capability: str, 
                           proficiency: float = 0.5, verified: bool = False) -> Dict[str, Any]:
        """
        Register an agent's capability.
        
        Args:
            agent_id: Agent identifier
            capability: Capability name
            proficiency: Proficiency level (0.0 to 1.0)
            verified: Whether capability is verified
            
        Returns:
            Success status
        """
        try:
            proficiency = max(0.0, min(1.0, proficiency))
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agent_capabilities (agent_id, capability, proficiency, verified)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, capability, proficiency, verified))
            
            self.conn.commit()
            
            return {
                "success": True,
                "agent_id": agent_id,
                "capability": capability,
                "proficiency": proficiency
            }
            
        except Exception as e:
            logger.error(f"Error registering capability: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_capable_agents(self, required_capabilities: List[str], 
                           min_proficiency: float = 0.5) -> Dict[str, Any]:
        """
        Find agents with required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            min_proficiency: Minimum proficiency level
            
        Returns:
            List of matching agents
        """
        try:
            cursor = self.conn.cursor()
            
            # Find agents with all required capabilities
            placeholders = ','.join(['?' for _ in required_capabilities])
            sql = f'''
                SELECT agent_id, COUNT(DISTINCT capability) as capability_count,
                       AVG(proficiency) as avg_proficiency
                FROM agent_capabilities
                WHERE capability IN ({placeholders})
                AND proficiency >= ?
                GROUP BY agent_id
                HAVING capability_count = ?
                ORDER BY avg_proficiency DESC
            '''
            
            params = required_capabilities + [min_proficiency, len(required_capabilities)]
            cursor.execute(sql, params)
            
            agents = []
            for row in cursor.fetchall():
                # Get detailed capabilities
                cursor.execute('''
                    SELECT capability, proficiency, verified
                    FROM agent_capabilities
                    WHERE agent_id = ? AND capability IN ({})
                '''.format(placeholders), [row['agent_id']] + required_capabilities)
                
                capabilities = [dict(cap) for cap in cursor.fetchall()]
                
                agents.append({
                    "agent_id": row['agent_id'],
                    "avg_proficiency": row['avg_proficiency'],
                    "capabilities": capabilities
                })
            
            return {
                "success": True,
                "required_capabilities": required_capabilities,
                "matching_agents": agents,
                "count": len(agents)
            }
            
        except Exception as e:
            logger.error(f"Error finding capable agents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delegate_task(self, task_id: str, title: str, description: str,
                     delegator_id: str, delegatee_id: str, priority: str = "medium",
                     requirements: Optional[List[str]] = None, 
                     success_criteria: Optional[List[str]] = None,
                     deadline_hours: Optional[int] = None,
                     parent_delegation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Delegate a task to an agent.
        
        Args:
            task_id: Unique task identifier
            title: Task title
            description: Detailed description
            delegator_id: Agent delegating the task
            delegatee_id: Agent receiving the task
            priority: Task priority
            requirements: List of requirements
            success_criteria: List of success criteria
            deadline_hours: Hours until deadline
            parent_delegation_id: Parent delegation (for sub-tasks)
            
        Returns:
            Delegation details
        """
        try:
            # Validate priority
            if priority not in [p.value for p in TaskPriority]:
                return {
                    "success": False,
                    "error": f"Invalid priority: {priority}"
                }
            
            deadline = None
            if deadline_hours:
                deadline = (datetime.now() + timedelta(hours=deadline_hours)).isoformat()
            
            requirements_json = json.dumps(requirements or [])
            success_criteria_json = json.dumps(success_criteria or [])
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO delegations (task_id, title, description, delegator_id, delegatee_id,
                                       status, priority, requirements, success_criteria, 
                                       created_at, deadline, parent_delegation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, title, description, delegator_id, delegatee_id,
                  TaskStatus.PENDING.value, priority, requirements_json, success_criteria_json,
                  datetime.now().isoformat(), deadline, parent_delegation_id))
            
            delegation_id = cursor.lastrowid
            self.conn.commit()
            
            logger.info(f"Task {task_id} delegated from {delegator_id} to {delegatee_id}")
            
            return {
                "success": True,
                "delegation_id": delegation_id,
                "task_id": task_id,
                "delegator_id": delegator_id,
                "delegatee_id": delegatee_id,
                "priority": priority,
                "deadline": deadline,
                "status": TaskStatus.PENDING.value
            }
            
        except sqlite3.IntegrityError:
            return {
                "success": False,
                "error": f"Task {task_id} already exists"
            }
        except Exception as e:
            logger.error(f"Error delegating task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def accept_delegation(self, task_id: str, delegatee_id: str) -> Dict[str, Any]:
        """
        Accept a delegated task and start work.
        
        Args:
            task_id: Task identifier
            delegatee_id: Agent accepting the task
            
        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE delegations 
                SET status = ?, started_at = ?
                WHERE task_id = ? AND delegatee_id = ? AND status = ?
            ''', (TaskStatus.IN_PROGRESS.value, datetime.now().isoformat(), 
                  task_id, delegatee_id, TaskStatus.PENDING.value))
            
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or already accepted"
                }
            
            self.conn.commit()
            
            return {
                "success": True,
                "task_id": task_id,
                "status": TaskStatus.IN_PROGRESS.value,
                "started_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error accepting delegation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_progress(self, task_id: str, reported_by: str, progress_percent: float,
                       status: Optional[str] = None, message: Optional[str] = None,
                       blockers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update task progress.
        
        Args:
            task_id: Task identifier
            reported_by: Agent reporting progress
            progress_percent: Progress percentage (0-100)
            status: Optional status update
            message: Progress message
            blockers: List of blockers
            
        Returns:
            Success status
        """
        try:
            progress_percent = max(0.0, min(100.0, progress_percent))
            
            cursor = self.conn.cursor()
            
            # Get current delegation
            cursor.execute('SELECT id, status FROM delegations WHERE task_id = ?', (task_id,))
            delegation = cursor.fetchone()
            
            if not delegation:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            current_status = status or delegation['status']
            
            # Update delegation progress
            cursor.execute('''
                UPDATE delegations 
                SET progress_percent = ?, status = ?
                WHERE task_id = ?
            ''', (progress_percent, current_status, task_id))
            
            # Record progress update
            blockers_json = json.dumps(blockers or [])
            cursor.execute('''
                INSERT INTO progress_updates (delegation_id, reported_by, progress_percent, 
                                             status, message, blockers, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (delegation['id'], reported_by, progress_percent, current_status, 
                  message, blockers_json, datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Check if escalation needed
            if blockers:
                logger.warning(f"Task {task_id} has blockers: {blockers}")
            
            return {
                "success": True,
                "task_id": task_id,
                "progress_percent": progress_percent,
                "status": current_status,
                "has_blockers": bool(blockers)
            }
            
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_delegation(self, task_id: str, delegatee_id: str, 
                           result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark delegation as completed.
        
        Args:
            task_id: Task identifier
            delegatee_id: Agent completing the task
            result: Task result
            
        Returns:
            Success status
        """
        try:
            result_json = json.dumps(result)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE delegations 
                SET status = ?, completed_at = ?, progress_percent = 100, result = ?
                WHERE task_id = ? AND delegatee_id = ?
            ''', (TaskStatus.COMPLETED.value, datetime.now().isoformat(), 
                  result_json, task_id, delegatee_id))
            
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or not assigned to {delegatee_id}"
                }
            
            self.conn.commit()
            
            # Calculate duration
            cursor.execute('''
                SELECT created_at, started_at, completed_at 
                FROM delegations WHERE task_id = ?
            ''', (task_id,))
            times = cursor.fetchone()
            
            if times['started_at']:
                started = datetime.fromisoformat(times['started_at'])
                completed = datetime.fromisoformat(times['completed_at'])
                duration = (completed - started).total_seconds()
            else:
                duration = 0
            
            return {
                "success": True,
                "task_id": task_id,
                "status": TaskStatus.COMPLETED.value,
                "duration_seconds": duration,
                "completed_at": times['completed_at']
            }
            
        except Exception as e:
            logger.error(f"Error completing delegation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def provide_feedback(self, task_id: str, feedback_from: str, 
                        feedback_text: str, rating: Optional[float] = None) -> Dict[str, Any]:
        """
        Provide feedback on completed delegation.
        
        Args:
            task_id: Task identifier
            feedback_from: Agent providing feedback
            feedback_text: Feedback content
            rating: Optional rating (0-5)
            
        Returns:
            Success status
        """
        try:
            feedback_data = {
                "from": feedback_from,
                "text": feedback_text,
                "rating": rating,
                "timestamp": datetime.now().isoformat()
            }
            feedback_json = json.dumps(feedback_data)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE delegations 
                SET feedback = ?
                WHERE task_id = ? AND status = ?
            ''', (feedback_json, task_id, TaskStatus.COMPLETED.value))
            
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found or not completed"
                }
            
            self.conn.commit()
            
            return {
                "success": True,
                "task_id": task_id,
                "feedback_provided": True
            }
            
        except Exception as e:
            logger.error(f"Error providing feedback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_delegation(self, task_id: str, include_progress: bool = False) -> Dict[str, Any]:
        """
        Get delegation details.
        
        Args:
            task_id: Task identifier
            include_progress: Include progress history
            
        Returns:
            Delegation details
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM delegations WHERE task_id = ?', (task_id,))
            delegation = cursor.fetchone()
            
            if not delegation:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            delegation_dict = dict(delegation)
            delegation_dict['requirements'] = json.loads(delegation_dict['requirements'])
            delegation_dict['success_criteria'] = json.loads(delegation_dict['success_criteria'])
            if delegation_dict['result']:
                delegation_dict['result'] = json.loads(delegation_dict['result'])
            if delegation_dict['feedback']:
                delegation_dict['feedback'] = json.loads(delegation_dict['feedback'])
            
            if include_progress:
                cursor.execute('''
                    SELECT * FROM progress_updates 
                    WHERE delegation_id = ?
                    ORDER BY updated_at
                ''', (delegation['id'],))
                
                updates = []
                for row in cursor.fetchall():
                    update = dict(row)
                    update['blockers'] = json.loads(update['blockers'])
                    updates.append(update)
                
                delegation_dict['progress_history'] = updates
            
            return {
                "success": True,
                "delegation": delegation_dict
            }
            
        except Exception as e:
            logger.error(f"Error getting delegation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_delegations(self, agent_id: Optional[str] = None, 
                        status: Optional[str] = None,
                        role: str = "both", limit: int = 50) -> Dict[str, Any]:
        """
        List delegations.
        
        Args:
            agent_id: Filter by agent (delegator or delegatee)
            status: Filter by status
            role: Filter by role (delegator, delegatee, both)
            limit: Maximum results
            
        Returns:
            List of delegations
        """
        try:
            cursor = self.conn.cursor()
            
            sql = 'SELECT * FROM delegations WHERE 1=1'
            params = []
            
            if agent_id:
                if role == "delegator":
                    sql += ' AND delegator_id = ?'
                    params.append(agent_id)
                elif role == "delegatee":
                    sql += ' AND delegatee_id = ?'
                    params.append(agent_id)
                else:  # both
                    sql += ' AND (delegator_id = ? OR delegatee_id = ?)'
                    params.extend([agent_id, agent_id])
            
            if status:
                sql += ' AND status = ?'
                params.append(status)
            
            sql += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            
            delegations = []
            for row in cursor.fetchall():
                delegation = dict(row)
                delegation['requirements'] = json.loads(delegation['requirements'])
                delegation['success_criteria'] = json.loads(delegation['success_criteria'])
                delegations.append(delegation)
            
            return {
                "success": True,
                "count": len(delegations),
                "delegations": delegations
            }
            
        except Exception as e:
            logger.error(f"Error listing delegations: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Delegation database connection closed")


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "delegate_task",
            "description": "Delegate a task to another agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Unique task identifier"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "delegator_id": {"type": "string", "description": "Agent delegating the task"},
                    "delegatee_id": {"type": "string", "description": "Agent receiving the task"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Task priority"
                    },
                    "requirements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of requirements"
                    },
                    "deadline_hours": {"type": "integer", "description": "Hours until deadline"}
                },
                "required": ["task_id", "title", "description", "delegator_id", "delegatee_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_progress",
            "description": "Update progress on a delegated task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "reported_by": {"type": "string", "description": "Agent reporting progress"},
                    "progress_percent": {
                        "type": "number",
                        "description": "Progress percentage (0-100)",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "message": {"type": "string", "description": "Progress message"},
                    "blockers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of blockers"
                    }
                },
                "required": ["task_id", "reported_by", "progress_percent"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_delegation",
            "description": "Mark a delegated task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "delegatee_id": {"type": "string", "description": "Agent completing the task"},
                    "result": {
                        "type": "object",
                        "description": "Task result"
                    }
                },
                "required": ["task_id", "delegatee_id", "result"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_capable_agents",
            "description": "Find agents with required capabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "required_capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of required capabilities"
                    },
                    "min_proficiency": {
                        "type": "number",
                        "description": "Minimum proficiency level (0-1)"
                    }
                },
                "required": ["required_capabilities"]
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
        manager = DelegationManagerTool(db_path=db_path)
        
        # Register capabilities
        print("\n=== Registering Capabilities ===")
        manager.register_capability("agent-001", "code_analysis", proficiency=0.9, verified=True)
        manager.register_capability("agent-001", "python", proficiency=0.95, verified=True)
        manager.register_capability("agent-002", "security_audit", proficiency=0.85, verified=True)
        
        # Find capable agents
        print("\n=== Finding Capable Agents ===")
        result = manager.find_capable_agents(["code_analysis", "python"], min_proficiency=0.8)
        print(json.dumps(result, indent=2))
        
        # Delegate task
        print("\n=== Delegating Task ===")
        result = manager.delegate_task(
            task_id="task-001",
            title="Analyze module for security issues",
            description="Perform security analysis on auth module",
            delegator_id="coordinator-001",
            delegatee_id="agent-002",
            priority="high",
            requirements=["security_audit", "python"],
            deadline_hours=48
        )
        print(json.dumps(result, indent=2))
        
        # Accept delegation
        print("\n=== Accepting Delegation ===")
        result = manager.accept_delegation("task-001", "agent-002")
        print(json.dumps(result, indent=2))
        
        # Update progress
        print("\n=== Updating Progress ===")
        result = manager.update_progress(
            task_id="task-001",
            reported_by="agent-002",
            progress_percent=50,
            message="Completed initial scan, found 3 issues"
        )
        print(json.dumps(result, indent=2))
        
        # Complete delegation
        print("\n=== Completing Delegation ===")
        result = manager.complete_delegation(
            task_id="task-001",
            delegatee_id="agent-002",
            result={
                "issues_found": 3,
                "severity": ["medium", "low", "low"],
                "report_url": "/reports/task-001.pdf"
            }
        )
        print(json.dumps(result, indent=2))
        
        manager.close()
        
    finally:
        os.unlink(db_path)
        print(f"\nCleaned up temporary database: {db_path}")
