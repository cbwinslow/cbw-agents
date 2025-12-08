# Memory Management Rules

**Priority**: 🔒 Critical (Must Follow)

These rules ensure efficient memory usage, prevent memory leaks, and maintain system stability in AI agent operations.

## Overview

AI agents must manage both short-term (working memory) and long-term (persistent memory) effectively. Poor memory management can lead to system instability, performance degradation, and data loss.

## Core Principles

1. **Allocate Responsibly**: Only allocate what you need
2. **Release Promptly**: Free resources as soon as possible
3. **Monitor Continuously**: Track memory usage
4. **Archive Strategically**: Move old data to long-term storage
5. **Clean Thoroughly**: Implement comprehensive cleanup

## Memory Types

### Short-Term Memory (Working Memory)

**Purpose**: Active task context, current conversation, temporary data

**Characteristics**:
- Fast access
- Limited capacity
- Volatile (lost on restart)
- High-priority cleanup

**Use Cases**:
- Current conversation context
- Active task state
- Temporary calculations
- Session data

### Long-Term Memory (Persistent Memory)

**Purpose**: Historical data, learned patterns, knowledge base

**Characteristics**:
- Slower access
- Large capacity
- Persistent (survives restart)
- Structured storage

**Use Cases**:
- Conversation history
- Learned preferences
- Knowledge accumulation
- Audit trails

## Rules

### MEM-001: Always Release Allocated Resources

**Description**: Every allocated resource must be released when no longer needed.

**Requirements**:
- Use context managers (`with` statements)
- Implement cleanup in `finally` blocks
- Close file handles, database connections, network sockets
- Release memory allocations
- Clean up temporary files

**Example - Correct**:
```python
# ✅ CORRECT - Using context manager
with open('file.txt', 'r') as f:
    data = f.read()
    # File automatically closed

# ✅ CORRECT - Manual cleanup with try/finally
connection = None
try:
    connection = database.connect()
    result = connection.query("SELECT * FROM table")
finally:
    if connection:
        connection.close()
```

**Example - Violation**:
```python
# ❌ NEVER DO THIS - Resource leak
f = open('file.txt', 'r')
data = f.read()
# File never closed!
```

### MEM-002: Monitor Memory Usage Continuously

**Description**: Track memory consumption and take action before limits are reached.

**Requirements**:
- Monitor working memory size
- Set memory thresholds
- Implement memory alerts
- Log memory usage patterns
- Trigger cleanup when approaching limits

**Example - Correct**:
```python
# ✅ CORRECT
import psutil
from typing import Dict, Any

class MemoryMonitor:
    def __init__(self, threshold_mb: int = 500):
        self.threshold_mb = threshold_mb
    
    def check_memory(self) -> Dict[str, Any]:
        """Check current memory usage."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        return {
            "memory_mb": memory_mb,
            "threshold_mb": self.threshold_mb,
            "needs_cleanup": memory_mb > self.threshold_mb,
            "usage_percent": (memory_mb / self.threshold_mb) * 100
        }
    
    def should_cleanup(self) -> bool:
        """Check if cleanup is needed."""
        return self.check_memory()["needs_cleanup"]

# Usage
monitor = MemoryMonitor(threshold_mb=500)
if monitor.should_cleanup():
    # Trigger cleanup
    memory_manager.cleanup_old_data()
```

### MEM-003: Implement Cleanup in Error Paths

**Description**: Ensure resources are cleaned up even when errors occur.

**Requirements**:
- Use try/finally blocks
- Implement context managers
- Clean up in exception handlers
- Don't rely on garbage collection alone
- Test error paths for leaks

**Example - Correct**:
```python
# ✅ CORRECT
class ShortTermMemory:
    def __init__(self):
        self.context = {}
        self.temp_files = []
    
    def process_task(self, task_data):
        temp_file = None
        try:
            # Create temporary file
            temp_file = self._create_temp_file()
            self.temp_files.append(temp_file)
            
            # Process task
            result = self._process(task_data, temp_file)
            return result
            
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            raise
            
        finally:
            # Always cleanup, even on error
            self._cleanup_temp_files()
    
    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")
        self.temp_files.clear()
```

### MEM-004: Use Context Managers for Resource Handling

**Description**: Prefer context managers for automatic resource management.

**Requirements**:
- Implement `__enter__` and `__exit__` for custom resources
- Use `contextlib` for simple cases
- Chain context managers when needed
- Handle exceptions in `__exit__`

**Example - Correct**:
```python
# ✅ CORRECT
from contextlib import contextmanager
import json

@contextmanager
def memory_context(memory_manager, context_name):
    """Context manager for memory operations."""
    # Setup
    memory_manager.push_context(context_name)
    try:
        yield memory_manager
    finally:
        # Cleanup - always executes
        memory_manager.pop_context()
        memory_manager.cleanup_if_needed()

# Usage
with memory_context(memory_manager, "task_001") as mem:
    mem.store("key", "value")
    # Context automatically cleaned up
```

### MEM-005: Limit Long-Term Memory Storage

**Description**: Implement retention policies and prevent unbounded growth of long-term memory.

**Requirements**:
- Set maximum storage limits
- Implement retention policies
- Archive or delete old data
- Prioritize important memories
- Implement memory pruning

**Example - Correct**:
```python
# ✅ CORRECT
from datetime import datetime, timedelta
from typing import List, Dict, Any

class LongTermMemory:
    def __init__(self, max_entries: int = 10000, retention_days: int = 90):
        self.max_entries = max_entries
        self.retention_days = retention_days
        self.storage = []
    
    def store(self, entry: Dict[str, Any]):
        """Store entry with automatic pruning."""
        # Add timestamp
        entry['timestamp'] = datetime.now().isoformat()
        entry['importance'] = entry.get('importance', 0.5)
        
        # Add to storage
        self.storage.append(entry)
        
        # Prune if needed
        if len(self.storage) > self.max_entries:
            self._prune_old_entries()
    
    def _prune_old_entries(self):
        """Remove old or low-importance entries."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        # Sort by importance and recency
        self.storage.sort(
            key=lambda x: (x['importance'], x['timestamp']),
            reverse=True
        )
        
        # Keep only max_entries most important
        self.storage = self.storage[:self.max_entries]
        
        # Remove entries older than retention period (unless high importance)
        self.storage = [
            entry for entry in self.storage
            if (datetime.fromisoformat(entry['timestamp']) > cutoff_date
                or entry['importance'] > 0.8)
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_entries": len(self.storage),
            "max_entries": self.max_entries,
            "usage_percent": (len(self.storage) / self.max_entries) * 100,
            "oldest_entry": min(e['timestamp'] for e in self.storage) if self.storage else None
        }
```

### MEM-006: Implement Memory Archival Strategies

**Description**: Archive old but potentially useful data to cheaper, slower storage.

**Requirements**:
- Define archival criteria (age, importance, access frequency)
- Implement archive storage mechanism
- Support archive retrieval when needed
- Compress archived data
- Maintain archive index

**Example - Correct**:
```python
# ✅ CORRECT
import gzip
import json
from pathlib import Path
from datetime import datetime, timedelta

class MemoryArchiver:
    def __init__(self, archive_dir: str = "./memory_archive"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(exist_ok=True)
    
    def should_archive(self, entry: Dict[str, Any]) -> bool:
        """Determine if entry should be archived."""
        # Archive if older than 30 days and low importance
        entry_date = datetime.fromisoformat(entry['timestamp'])
        age_days = (datetime.now() - entry_date).days
        
        return (age_days > 30 and entry['importance'] < 0.7)
    
    def archive_entry(self, entry: Dict[str, Any]) -> str:
        """Archive an entry to compressed storage."""
        # Create archive filename
        entry_id = entry.get('id', hash(str(entry)))
        archive_file = self.archive_dir / f"entry_{entry_id}.json.gz"
        
        # Compress and save
        data = json.dumps(entry).encode('utf-8')
        with gzip.open(archive_file, 'wb') as f:
            f.write(data)
        
        return str(archive_file)
    
    def retrieve_from_archive(self, entry_id: str) -> Dict[str, Any]:
        """Retrieve archived entry."""
        archive_file = self.archive_dir / f"entry_{entry_id}.json.gz"
        
        if not archive_file.exists():
            raise FileNotFoundError(f"Archived entry not found: {entry_id}")
        
        with gzip.open(archive_file, 'rb') as f:
            data = f.read()
        
        return json.loads(data.decode('utf-8'))
    
    def cleanup_old_archives(self, max_age_days: int = 180):
        """Remove archives older than specified age."""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for archive_file in self.archive_dir.glob("*.json.gz"):
            if datetime.fromtimestamp(archive_file.stat().st_mtime) < cutoff_date:
                archive_file.unlink()
```

## Memory Strategies

### Working Memory Management

**Size Limits**:
- Current conversation: ~4000 tokens
- Task context: ~2000 tokens
- Temporary data: ~1000 tokens
- Total working memory: ~8000 tokens

**Cleanup Triggers**:
- After task completion
- When memory threshold reached
- On conversation context switch
- On error or exception

**Example**:
```python
class WorkingMemory:
    MAX_CONTEXT_SIZE = 4000  # tokens
    MAX_TASK_SIZE = 2000  # tokens
    
    def __init__(self):
        self.conversation_context = []
        self.task_context = {}
        self.temp_data = {}
    
    def add_to_conversation(self, message: str):
        """Add message to conversation context."""
        self.conversation_context.append(message)
        
        # Prune if too large
        total_tokens = self._estimate_tokens(self.conversation_context)
        if total_tokens > self.MAX_CONTEXT_SIZE:
            self._prune_conversation()
    
    def _prune_conversation(self):
        """Keep only recent conversation context."""
        # Keep last N messages that fit in limit
        while len(self.conversation_context) > 1:
            tokens = self._estimate_tokens(self.conversation_context)
            if tokens <= self.MAX_CONTEXT_SIZE:
                break
            # Remove oldest message (except system messages)
            self.conversation_context.pop(0)
    
    def _estimate_tokens(self, messages: List[str]) -> int:
        """Estimate token count."""
        # Simple estimation: ~4 chars per token
        return sum(len(msg) for msg in messages) // 4
    
    def clear(self):
        """Clear all working memory."""
        self.conversation_context.clear()
        self.task_context.clear()
        self.temp_data.clear()
```

### Long-Term Memory Indexing

**Index Strategy**:
- Use vector embeddings for semantic search
- Maintain metadata index for quick filtering
- Implement full-text search for exact matches
- Cache frequently accessed memories

**Example**:
```python
from typing import List, Optional
import numpy as np

class LongTermMemoryIndex:
    def __init__(self):
        self.entries = []
        self.embeddings = []
        self.index = {}  # metadata index
    
    def add(self, entry: Dict[str, Any], embedding: np.ndarray):
        """Add entry with embedding."""
        entry_id = len(self.entries)
        entry['id'] = entry_id
        
        self.entries.append(entry)
        self.embeddings.append(embedding)
        
        # Update metadata index
        self._update_index(entry)
    
    def _update_index(self, entry: Dict[str, Any]):
        """Update metadata index."""
        # Index by tags
        for tag in entry.get('tags', []):
            if tag not in self.index:
                self.index[tag] = []
            self.index[tag].append(entry['id'])
    
    def search_semantic(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Search by semantic similarity."""
        if not self.embeddings:
            return []
        
        # Calculate cosine similarity
        embeddings_array = np.array(self.embeddings)
        similarities = np.dot(embeddings_array, query_embedding)
        
        # Get top-k most similar
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [self.entries[i] for i in top_indices]
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """Search by metadata tag."""
        entry_ids = self.index.get(tag, [])
        return [self.entries[i] for i in entry_ids]
```

## Memory Patterns

### Pattern 1: Conversation Memory

```python
class ConversationMemory:
    """Manages conversation history with automatic summarization."""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages = []
        self.summary = None
    
    def add_message(self, role: str, content: str):
        """Add message to conversation."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Summarize old messages if limit reached
        if len(self.messages) > self.max_messages:
            self._summarize_old_messages()
    
    def _summarize_old_messages(self):
        """Summarize and archive old messages."""
        # Take first half of messages
        old_messages = self.messages[:len(self.messages)//2]
        
        # Create summary (simplified - would use LLM in practice)
        self.summary = {
            "message_count": len(old_messages),
            "key_points": self._extract_key_points(old_messages),
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep only recent messages
        self.messages = self.messages[len(old_messages):]
    
    def get_context(self) -> List[Dict]:
        """Get conversation context for LLM."""
        context = []
        
        # Include summary if available
        if self.summary:
            context.append({
                "role": "system",
                "content": f"Previous conversation summary: {self.summary['key_points']}"
            })
        
        # Include recent messages
        context.extend(self.messages)
        
        return context
```

### Pattern 2: Task Memory

```python
class TaskMemory:
    """Manages task-specific memory with automatic cleanup."""
    
    def __init__(self):
        self.active_tasks = {}
        self.completed_tasks = []
    
    def start_task(self, task_id: str, task_data: Dict):
        """Start tracking a task."""
        self.active_tasks[task_id] = {
            "data": task_data,
            "started_at": datetime.now().isoformat(),
            "working_memory": {}
        }
    
    def update_task(self, task_id: str, key: str, value: Any):
        """Update task working memory."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["working_memory"][key] = value
    
    def complete_task(self, task_id: str, result: Any):
        """Complete and archive task."""
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            task["completed_at"] = datetime.now().isoformat()
            task["result"] = result
            
            # Archive to long-term memory
            self.completed_tasks.append(task)
            
            # Clean up working memory
            task["working_memory"] = None
    
    def cleanup_old_completed(self, max_age_hours: int = 24):
        """Remove old completed tasks."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        self.completed_tasks = [
            task for task in self.completed_tasks
            if datetime.fromisoformat(task["completed_at"]) > cutoff
        ]
```

## Monitoring and Alerts

### Memory Thresholds

```python
class MemoryAlerts:
    WARN_THRESHOLD = 0.7  # 70% usage
    CRITICAL_THRESHOLD = 0.9  # 90% usage
    
    def check_memory_status(self, current_mb: float, limit_mb: float) -> str:
        """Check memory status and return alert level."""
        usage_ratio = current_mb / limit_mb
        
        if usage_ratio >= self.CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif usage_ratio >= self.WARN_THRESHOLD:
            return "WARNING"
        else:
            return "OK"
```

## Best Practices

1. **Prefer streaming over loading**: Process data incrementally
2. **Use generators**: Avoid loading entire datasets into memory
3. **Implement pagination**: Break large operations into chunks
4. **Cache wisely**: Cache frequently used data, but with limits
5. **Profile regularly**: Identify memory hotspots
6. **Test cleanup**: Verify resources are released in tests

## Troubleshooting

### Memory Leak Detection

```bash
# Monitor process memory over time
watch -n 1 'ps aux | grep agent'

# Python memory profiling
pip install memory_profiler
python -m memory_profiler agent.py
```

### Common Issues

1. **Unclosed file handles**: Use context managers
2. **Circular references**: Use weak references or break cycles
3. **Large cached data**: Implement cache eviction
4. **Accumulated logs**: Rotate and compress logs
5. **Temporary files**: Clean up in finally blocks

---

**Version**: 2.0.0  
**Last Updated**: 2025-12-08  
**Priority**: 🔒 Critical  
**Compliance**: Mandatory
