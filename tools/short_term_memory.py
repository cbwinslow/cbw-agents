#!/usr/bin/env python3
"""
Short-Term Memory Tool

Manages working memory for AI agents, including context window management,
temporary data storage, and automatic cleanup.

OpenAI Compatible: Yes
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShortTermMemoryTool:
    """
    Short-term memory management for AI agents.
    
    Features:
    - Context window management
    - Conversation tracking
    - Task-specific memory
    - Automatic cleanup
    - Memory size limits
    """
    
    def __init__(self, max_context_tokens: int = 4000, max_tasks: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            max_context_tokens: Maximum tokens for conversation context
            max_tasks: Maximum number of active tasks to track
        """
        self.max_context_tokens = max_context_tokens
        self.max_tasks = max_tasks
        
        # Conversation context
        self.conversation = deque(maxlen=50)
        self.conversation_tokens = 0
        
        # Task-specific memory
        self.active_tasks = {}
        
        # Temporary data store
        self.temp_data = {}
        
        logger.info(f"ShortTermMemory initialized: max_context={max_context_tokens} tokens, max_tasks={max_tasks}")
    
    def add_to_conversation(self, role: str, content: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add message to conversation context.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Success status and conversation info
        """
        try:
            # Estimate tokens (rough: 4 chars per token)
            tokens = len(content) // 4
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "tokens": tokens,
                "metadata": metadata or {}
            }
            
            self.conversation.append(message)
            self.conversation_tokens += tokens
            
            # Prune if exceeding limit
            while self.conversation_tokens > self.max_context_tokens and len(self.conversation) > 1:
                removed = self.conversation.popleft()
                self.conversation_tokens -= removed["tokens"]
            
            return {
                "success": True,
                "conversation_length": len(self.conversation),
                "total_tokens": self.conversation_tokens,
                "message_added": {
                    "role": role,
                    "tokens": tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error adding to conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_conversation_context(self, max_messages: Optional[int] = None) -> Dict[str, Any]:
        """
        Get recent conversation context.
        
        Args:
            max_messages: Maximum number of messages to return (default: all)
            
        Returns:
            Conversation messages and stats
        """
        try:
            messages = list(self.conversation)
            
            if max_messages:
                messages = messages[-max_messages:]
            
            return {
                "success": True,
                "messages": messages,
                "total_messages": len(self.conversation),
                "total_tokens": self.conversation_tokens,
                "returned_messages": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_conversation(self) -> Dict[str, Any]:
        """
        Clear all conversation context.
        
        Returns:
            Success status
        """
        try:
            cleared_count = len(self.conversation)
            cleared_tokens = self.conversation_tokens
            
            self.conversation.clear()
            self.conversation_tokens = 0
            
            return {
                "success": True,
                "cleared_messages": cleared_count,
                "cleared_tokens": cleared_tokens
            }
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start tracking a new task.
        
        Args:
            task_id: Unique task identifier
            task_data: Task information and context
            
        Returns:
            Success status and task info
        """
        try:
            if task_id in self.active_tasks:
                return {
                    "success": False,
                    "error": f"Task {task_id} already exists"
                }
            
            # Enforce task limit
            if len(self.active_tasks) >= self.max_tasks:
                # Remove oldest task
                oldest_task = min(
                    self.active_tasks.items(),
                    key=lambda x: x[1]["started_at"]
                )
                del self.active_tasks[oldest_task[0]]
                logger.warning(f"Removed oldest task {oldest_task[0]} to make room")
            
            self.active_tasks[task_id] = {
                "task_data": task_data,
                "started_at": datetime.now().isoformat(),
                "working_memory": {},
                "updates": []
            }
            
            return {
                "success": True,
                "task_id": task_id,
                "active_tasks_count": len(self.active_tasks)
            }
            
        except Exception as e:
            logger.error(f"Error starting task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_task_memory(self, task_id: str, key: str, value: Any) -> Dict[str, Any]:
        """
        Update task working memory.
        
        Args:
            task_id: Task identifier
            key: Memory key
            value: Value to store
            
        Returns:
            Success status
        """
        try:
            if task_id not in self.active_tasks:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            self.active_tasks[task_id]["working_memory"][key] = value
            self.active_tasks[task_id]["updates"].append({
                "timestamp": datetime.now().isoformat(),
                "key": key,
                "action": "update"
            })
            
            return {
                "success": True,
                "task_id": task_id,
                "key": key
            }
            
        except Exception as e:
            logger.error(f"Error updating task memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_task_memory(self, task_id: str, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get task working memory.
        
        Args:
            task_id: Task identifier
            key: Specific key to retrieve (None for all)
            
        Returns:
            Task memory data
        """
        try:
            if task_id not in self.active_tasks:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            memory = self.active_tasks[task_id]["working_memory"]
            
            if key:
                if key not in memory:
                    return {
                        "success": False,
                        "error": f"Key {key} not found in task memory"
                    }
                return {
                    "success": True,
                    "task_id": task_id,
                    "key": key,
                    "value": memory[key]
                }
            else:
                return {
                    "success": True,
                    "task_id": task_id,
                    "working_memory": memory,
                    "started_at": self.active_tasks[task_id]["started_at"],
                    "update_count": len(self.active_tasks[task_id]["updates"])
                }
            
        except Exception as e:
            logger.error(f"Error getting task memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Mark task as complete and clean up working memory.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task summary
        """
        try:
            if task_id not in self.active_tasks:
                return {
                    "success": False,
                    "error": f"Task {task_id} not found"
                }
            
            task = self.active_tasks.pop(task_id)
            task["completed_at"] = datetime.now().isoformat()
            
            # Calculate duration
            started = datetime.fromisoformat(task["started_at"])
            completed = datetime.fromisoformat(task["completed_at"])
            duration = (completed - started).total_seconds()
            
            return {
                "success": True,
                "task_id": task_id,
                "duration_seconds": duration,
                "update_count": len(task["updates"]),
                "memory_keys": list(task["working_memory"].keys())
            }
            
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def store_temp_data(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        Store temporary data with optional TTL.
        
        Args:
            key: Data key
            value: Data value
            ttl_seconds: Time-to-live in seconds (None for no expiration)
            
        Returns:
            Success status
        """
        try:
            expiry = None
            if ttl_seconds:
                expiry = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
            
            self.temp_data[key] = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "expires_at": expiry
            }
            
            return {
                "success": True,
                "key": key,
                "expires_at": expiry
            }
            
        except Exception as e:
            logger.error(f"Error storing temp data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_temp_data(self, key: str) -> Dict[str, Any]:
        """
        Retrieve temporary data.
        
        Args:
            key: Data key
            
        Returns:
            Data value if found and not expired
        """
        try:
            if key not in self.temp_data:
                return {
                    "success": False,
                    "error": f"Key {key} not found"
                }
            
            item = self.temp_data[key]
            
            # Check expiration
            if item["expires_at"]:
                expiry = datetime.fromisoformat(item["expires_at"])
                if datetime.now() > expiry:
                    del self.temp_data[key]
                    return {
                        "success": False,
                        "error": f"Key {key} has expired"
                    }
            
            return {
                "success": True,
                "key": key,
                "value": item["value"],
                "created_at": item["created_at"],
                "expires_at": item["expires_at"]
            }
            
        except Exception as e:
            logger.error(f"Error getting temp data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_expired(self) -> Dict[str, Any]:
        """
        Clean up expired temporary data.
        
        Returns:
            Cleanup statistics
        """
        try:
            now = datetime.now()
            expired_keys = []
            
            for key, item in list(self.temp_data.items()):
                if item["expires_at"]:
                    expiry = datetime.fromisoformat(item["expires_at"])
                    if now > expiry:
                        expired_keys.append(key)
                        del self.temp_data[key]
            
            return {
                "success": True,
                "cleaned_count": len(expired_keys),
                "cleaned_keys": expired_keys
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Memory usage stats
        """
        try:
            return {
                "success": True,
                "conversation": {
                    "messages": len(self.conversation),
                    "tokens": self.conversation_tokens,
                    "max_tokens": self.max_context_tokens,
                    "usage_percent": (self.conversation_tokens / self.max_context_tokens) * 100
                },
                "tasks": {
                    "active": len(self.active_tasks),
                    "max_tasks": self.max_tasks,
                    "usage_percent": (len(self.active_tasks) / self.max_tasks) * 100,
                    "task_ids": list(self.active_tasks.keys())
                },
                "temp_data": {
                    "keys": len(self.temp_data),
                    "keys_list": list(self.temp_data.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_all(self) -> Dict[str, Any]:
        """
        Clear all short-term memory.
        
        Returns:
            Cleanup statistics
        """
        try:
            stats = {
                "conversation_messages": len(self.conversation),
                "active_tasks": len(self.active_tasks),
                "temp_data_keys": len(self.temp_data)
            }
            
            self.conversation.clear()
            self.conversation_tokens = 0
            self.active_tasks.clear()
            self.temp_data.clear()
            
            return {
                "success": True,
                "cleared": stats
            }
            
        except Exception as e:
            logger.error(f"Error clearing all memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_to_conversation",
            "description": "Add a message to the conversation context",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["user", "assistant", "system"],
                        "description": "The role of the message sender"
                    },
                    "content": {
                        "type": "string",
                        "description": "The message content"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata for the message"
                    }
                },
                "required": ["role", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversation_context",
            "description": "Get recent conversation messages",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_messages": {
                        "type": "integer",
                        "description": "Maximum number of messages to return"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_task",
            "description": "Start tracking a new task in working memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Unique identifier for the task"
                    },
                    "task_data": {
                        "type": "object",
                        "description": "Task information and context"
                    }
                },
                "required": ["task_id", "task_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_memory",
            "description": "Update task working memory with a key-value pair",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier"
                    },
                    "key": {
                        "type": "string",
                        "description": "Memory key"
                    },
                    "value": {
                        "description": "Value to store"
                    }
                },
                "required": ["task_id", "key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_memory",
            "description": "Retrieve task working memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier"
                    },
                    "key": {
                        "type": "string",
                        "description": "Specific key to retrieve (omit for all)"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark task as complete and clean up its working memory",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Task identifier"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_temp_data",
            "description": "Store temporary data with optional expiration",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Data key"
                    },
                    "value": {
                        "description": "Data value"
                    },
                    "ttl_seconds": {
                        "type": "integer",
                        "description": "Time-to-live in seconds (optional)"
                    }
                },
                "required": ["key", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_temp_data",
            "description": "Retrieve temporary data by key",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Data key"
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_memory_stats",
            "description": "Get memory usage statistics",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


if __name__ == "__main__":
    # Example usage
    memory = ShortTermMemoryTool()
    
    # Add conversation messages
    print("\n=== Adding Conversation Messages ===")
    result = memory.add_to_conversation("user", "Hello, can you help me with a task?")
    print(json.dumps(result, indent=2))
    
    result = memory.add_to_conversation("assistant", "Of course! I'd be happy to help. What task do you need assistance with?")
    print(json.dumps(result, indent=2))
    
    # Start a task
    print("\n=== Starting Task ===")
    result = memory.start_task("task-001", {
        "description": "Analyze codebase",
        "priority": "high"
    })
    print(json.dumps(result, indent=2))
    
    # Update task memory
    print("\n=== Updating Task Memory ===")
    result = memory.update_task_memory("task-001", "files_analyzed", 15)
    print(json.dumps(result, indent=2))
    
    result = memory.update_task_memory("task-001", "issues_found", ["import-error", "unused-variable"])
    print(json.dumps(result, indent=2))
    
    # Get task memory
    print("\n=== Getting Task Memory ===")
    result = memory.get_task_memory("task-001")
    print(json.dumps(result, indent=2))
    
    # Store temp data
    print("\n=== Storing Temporary Data ===")
    result = memory.store_temp_data("api_response", {"status": "ok", "data": [1, 2, 3]}, ttl_seconds=300)
    print(json.dumps(result, indent=2))
    
    # Get memory stats
    print("\n=== Memory Statistics ===")
    result = memory.get_memory_stats()
    print(json.dumps(result, indent=2))
    
    # Complete task
    print("\n=== Completing Task ===")
    result = memory.complete_task("task-001")
    print(json.dumps(result, indent=2))
