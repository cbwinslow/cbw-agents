#!/usr/bin/env python3
"""
RabbitMQ Integration Tool

Provides message queue communication for multi-agent systems using RabbitMQ.
Supports asynchronous messaging, pub/sub patterns, and reliable delivery.

OpenAI Compatible: Yes
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """RabbitMQ exchange types."""
    DIRECT = "direct"
    TOPIC = "topic"
    FANOUT = "fanout"
    HEADERS = "headers"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 5
    HIGH = 8
    URGENT = 10


class RabbitMQIntegrationTool:
    """
    RabbitMQ integration for multi-agent communication.
    
    Features:
    - Message publishing and consumption
    - Multiple exchange types
    - Message acknowledgment
    - Dead letter handling
    - Priority queues
    - Message persistence
    
    Note: This is a mock implementation for demonstration.
    In production, use pika or similar RabbitMQ client library.
    """
    
    def __init__(self, host: str = "localhost", port: int = 5672,
                 username: str = "guest", password: str = "guest",
                 virtual_host: str = "/"):
        """
        Initialize RabbitMQ connection.
        
        Args:
            host: RabbitMQ host
            port: RabbitMQ port
            username: Username for authentication
            password: Password for authentication
            virtual_host: Virtual host
        """
        self.host = host
        self.port = port
        self.username = username
        self.virtual_host = virtual_host
        self.connected = False
        
        # Mock storage for demonstration
        self.exchanges = {}
        self.queues = {}
        self.bindings = {}
        self.messages = {}
        
        logger.info(f"RabbitMQIntegration initialized: {host}:{port}/{virtual_host}")
        
        # In production, establish actual RabbitMQ connection here
        self._mock_connect()
    
    def _mock_connect(self):
        """
        Mock connection for demonstration purposes only.
        
        NOTE: This is a mock implementation. For production use:
        1. Install pika: pip install pika
        2. Replace this with actual RabbitMQ connection using pika
        3. Update all methods to use pika's channel operations
        
        Example production connection:
            import pika
            credentials = pika.PlainCredentials(self.username, password)
            parameters = pika.ConnectionParameters(
                host=self.host, port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        """
        self.connected = True
        logger.info("Connected to RabbitMQ (mock implementation - not for production)")
    
    def create_exchange(self, exchange_name: str, exchange_type: str = "topic",
                       durable: bool = True, auto_delete: bool = False) -> Dict[str, Any]:
        """
        Create an exchange.
        
        Args:
            exchange_name: Exchange name
            exchange_type: Exchange type (direct, topic, fanout, headers)
            durable: Survive broker restart
            auto_delete: Delete when no longer in use
            
        Returns:
            Success status
        """
        try:
            if exchange_type not in [e.value for e in ExchangeType]:
                return {
                    "success": False,
                    "error": f"Invalid exchange type: {exchange_type}"
                }
            
            self.exchanges[exchange_name] = {
                "type": exchange_type,
                "durable": durable,
                "auto_delete": auto_delete,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created exchange: {exchange_name} ({exchange_type})")
            
            return {
                "success": True,
                "exchange_name": exchange_name,
                "exchange_type": exchange_type,
                "durable": durable
            }
            
        except Exception as e:
            logger.error(f"Error creating exchange: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_queue(self, queue_name: str, durable: bool = True,
                    exclusive: bool = False, auto_delete: bool = False,
                    max_priority: Optional[int] = 10,
                    dead_letter_exchange: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a queue.
        
        Args:
            queue_name: Queue name
            durable: Survive broker restart
            exclusive: Used by only one connection
            auto_delete: Delete when no consumers
            max_priority: Maximum message priority
            dead_letter_exchange: Exchange for rejected messages
            
        Returns:
            Success status
        """
        try:
            self.queues[queue_name] = {
                "durable": durable,
                "exclusive": exclusive,
                "auto_delete": auto_delete,
                "max_priority": max_priority,
                "dead_letter_exchange": dead_letter_exchange,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
            
            logger.info(f"Created queue: {queue_name}")
            
            return {
                "success": True,
                "queue_name": queue_name,
                "durable": durable,
                "max_priority": max_priority
            }
            
        except Exception as e:
            logger.error(f"Error creating queue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def bind_queue(self, queue_name: str, exchange_name: str,
                  routing_key: str = "") -> Dict[str, Any]:
        """
        Bind queue to exchange with routing key.
        
        Args:
            queue_name: Queue name
            exchange_name: Exchange name
            routing_key: Routing key pattern
            
        Returns:
            Success status
        """
        try:
            if queue_name not in self.queues:
                return {
                    "success": False,
                    "error": f"Queue {queue_name} not found"
                }
            
            if exchange_name not in self.exchanges:
                return {
                    "success": False,
                    "error": f"Exchange {exchange_name} not found"
                }
            
            binding_key = f"{exchange_name}:{queue_name}:{routing_key}"
            self.bindings[binding_key] = {
                "queue": queue_name,
                "exchange": exchange_name,
                "routing_key": routing_key,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Bound queue {queue_name} to exchange {exchange_name} with key {routing_key}")
            
            return {
                "success": True,
                "queue_name": queue_name,
                "exchange_name": exchange_name,
                "routing_key": routing_key
            }
            
        except Exception as e:
            logger.error(f"Error binding queue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def publish_message(self, exchange_name: str, routing_key: str,
                       message: Dict[str, Any], priority: int = 5,
                       persistent: bool = True, 
                       headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Publish a message to an exchange.
        
        Args:
            exchange_name: Exchange name
            routing_key: Routing key
            message: Message payload
            priority: Message priority (0-10)
            persistent: Message survives broker restart
            headers: Optional message headers
            
        Returns:
            Success status and message ID
        """
        try:
            if exchange_name not in self.exchanges:
                return {
                    "success": False,
                    "error": f"Exchange {exchange_name} not found"
                }
            
            message_id = str(uuid.uuid4())
            message_envelope = {
                "message_id": message_id,
                "exchange": exchange_name,
                "routing_key": routing_key,
                "payload": message,
                "priority": priority,
                "persistent": persistent,
                "headers": headers or {},
                "timestamp": datetime.now().isoformat(),
                "delivered": False,
                "acknowledged": False
            }
            
            # Route message to bound queues
            exchange_type = self.exchanges[exchange_name]["type"]
            delivered_to = []
            
            for binding_key, binding in self.bindings.items():
                if binding["exchange"] == exchange_name:
                    if self._matches_routing(routing_key, binding["routing_key"], exchange_type):
                        queue_name = binding["queue"]
                        self.queues[queue_name]["messages"].append(message_envelope)
                        delivered_to.append(queue_name)
            
            self.messages[message_id] = message_envelope
            
            logger.info(f"Published message {message_id} to exchange {exchange_name}, delivered to {len(delivered_to)} queues")
            
            return {
                "success": True,
                "message_id": message_id,
                "exchange": exchange_name,
                "routing_key": routing_key,
                "delivered_to": delivered_to,
                "timestamp": message_envelope["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _matches_routing(self, routing_key: str, pattern: str, exchange_type: str) -> bool:
        """Check if routing key matches pattern."""
        if exchange_type == ExchangeType.FANOUT.value:
            return True
        elif exchange_type == ExchangeType.DIRECT.value:
            return routing_key == pattern
        elif exchange_type == ExchangeType.TOPIC.value:
            # Simple topic matching (simplified)
            if pattern == "#":
                return True
            if pattern == routing_key:
                return True
            # More complex topic matching would go here
            return False
        return False
    
    def consume_message(self, queue_name: str, auto_ack: bool = False) -> Dict[str, Any]:
        """
        Consume a message from a queue.
        
        Args:
            queue_name: Queue name
            auto_ack: Automatically acknowledge message
            
        Returns:
            Message or None if queue empty
        """
        try:
            if queue_name not in self.queues:
                return {
                    "success": False,
                    "error": f"Queue {queue_name} not found"
                }
            
            messages = self.queues[queue_name]["messages"]
            
            if not messages:
                return {
                    "success": True,
                    "message": None,
                    "queue_empty": True
                }
            
            # Sort by priority
            messages.sort(key=lambda m: m["priority"], reverse=True)
            
            message = messages.pop(0)
            
            if auto_ack:
                message["acknowledged"] = True
                message["delivered"] = True
            
            logger.info(f"Consumed message {message['message_id']} from queue {queue_name}")
            
            return {
                "success": True,
                "message": message,
                "queue_name": queue_name,
                "remaining_messages": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Error consuming message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def acknowledge_message(self, message_id: str) -> Dict[str, Any]:
        """
        Acknowledge message delivery.
        
        Args:
            message_id: Message identifier
            
        Returns:
            Success status
        """
        try:
            if message_id not in self.messages:
                return {
                    "success": False,
                    "error": f"Message {message_id} not found"
                }
            
            self.messages[message_id]["acknowledged"] = True
            self.messages[message_id]["delivered"] = True
            
            logger.info(f"Acknowledged message {message_id}")
            
            return {
                "success": True,
                "message_id": message_id,
                "acknowledged": True
            }
            
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reject_message(self, message_id: str, requeue: bool = False) -> Dict[str, Any]:
        """
        Reject a message.
        
        Args:
            message_id: Message identifier
            requeue: Requeue the message
            
        Returns:
            Success status
        """
        try:
            if message_id not in self.messages:
                return {
                    "success": False,
                    "error": f"Message {message_id} not found"
                }
            
            message = self.messages[message_id]
            
            if requeue:
                # Put back in queue
                for queue_name, queue_data in self.queues.items():
                    if any(m["message_id"] == message_id for m in queue_data["messages"]):
                        queue_data["messages"].append(message)
                        break
                logger.info(f"Rejected and requeued message {message_id}")
            else:
                # Send to dead letter exchange if configured
                logger.info(f"Rejected message {message_id} (not requeued)")
            
            return {
                "success": True,
                "message_id": message_id,
                "requeued": requeue
            }
            
        except Exception as e:
            logger.error(f"Error rejecting message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_queue_info(self, queue_name: str) -> Dict[str, Any]:
        """
        Get queue information.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Queue information
        """
        try:
            if queue_name not in self.queues:
                return {
                    "success": False,
                    "error": f"Queue {queue_name} not found"
                }
            
            queue = self.queues[queue_name]
            
            return {
                "success": True,
                "queue_name": queue_name,
                "message_count": len(queue["messages"]),
                "durable": queue["durable"],
                "exclusive": queue["exclusive"],
                "auto_delete": queue["auto_delete"],
                "max_priority": queue["max_priority"],
                "created_at": queue["created_at"]
            }
            
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def purge_queue(self, queue_name: str) -> Dict[str, Any]:
        """
        Remove all messages from a queue.
        
        Args:
            queue_name: Queue name
            
        Returns:
            Success status and message count
        """
        try:
            if queue_name not in self.queues:
                return {
                    "success": False,
                    "error": f"Queue {queue_name} not found"
                }
            
            message_count = len(self.queues[queue_name]["messages"])
            self.queues[queue_name]["messages"].clear()
            
            logger.info(f"Purged {message_count} messages from queue {queue_name}")
            
            return {
                "success": True,
                "queue_name": queue_name,
                "messages_purged": message_count
            }
            
        except Exception as e:
            logger.error(f"Error purging queue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close RabbitMQ connection."""
        self.connected = False
        logger.info("RabbitMQ connection closed (mock)")


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "publish_message",
            "description": "Publish a message to RabbitMQ exchange",
            "parameters": {
                "type": "object",
                "properties": {
                    "exchange_name": {"type": "string", "description": "Exchange name"},
                    "routing_key": {"type": "string", "description": "Routing key"},
                    "message": {"type": "object", "description": "Message payload"},
                    "priority": {
                        "type": "integer",
                        "description": "Message priority (0-10)",
                        "minimum": 0,
                        "maximum": 10
                    },
                    "persistent": {"type": "boolean", "description": "Message survives broker restart"}
                },
                "required": ["exchange_name", "routing_key", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consume_message",
            "description": "Consume a message from a queue",
            "parameters": {
                "type": "object",
                "properties": {
                    "queue_name": {"type": "string", "description": "Queue name"},
                    "auto_ack": {"type": "boolean", "description": "Automatically acknowledge message"}
                },
                "required": ["queue_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_queue",
            "description": "Create a RabbitMQ queue",
            "parameters": {
                "type": "object",
                "properties": {
                    "queue_name": {"type": "string", "description": "Queue name"},
                    "durable": {"type": "boolean", "description": "Survive broker restart"},
                    "max_priority": {"type": "integer", "description": "Maximum message priority"}
                },
                "required": ["queue_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_queue_info",
            "description": "Get information about a queue",
            "parameters": {
                "type": "object",
                "properties": {
                    "queue_name": {"type": "string", "description": "Queue name"}
                },
                "required": ["queue_name"]
            }
        }
    }
]


if __name__ == "__main__":
    # Example usage
    rabbit = RabbitMQIntegrationTool()
    
    # Create exchange
    print("\n=== Creating Exchange ===")
    result = rabbit.create_exchange("agent.tasks", exchange_type="topic", durable=True)
    print(json.dumps(result, indent=2))
    
    # Create queues
    print("\n=== Creating Queues ===")
    result = rabbit.create_queue("agent.001.tasks", durable=True, max_priority=10)
    print(json.dumps(result, indent=2))
    
    result = rabbit.create_queue("agent.002.tasks", durable=True, max_priority=10)
    print(json.dumps(result, indent=2))
    
    # Bind queues
    print("\n=== Binding Queues ===")
    result = rabbit.bind_queue("agent.001.tasks", "agent.tasks", routing_key="agent.001.#")
    print(json.dumps(result, indent=2))
    
    result = rabbit.bind_queue("agent.002.tasks", "agent.tasks", routing_key="agent.002.#")
    print(json.dumps(result, indent=2))
    
    # Publish message
    print("\n=== Publishing Message ===")
    result = rabbit.publish_message(
        exchange_name="agent.tasks",
        routing_key="agent.001.task",
        message={
            "task_id": "task-001",
            "action": "analyze_code",
            "parameters": {"file": "main.py"}
        },
        priority=8,
        persistent=True
    )
    print(json.dumps(result, indent=2))
    
    # Consume message
    print("\n=== Consuming Message ===")
    result = rabbit.consume_message("agent.001.tasks", auto_ack=False)
    print(json.dumps(result, indent=2))
    
    if result["success"] and result.get("message"):
        message_id = result["message"]["message_id"]
        
        # Acknowledge message
        print("\n=== Acknowledging Message ===")
        ack_result = rabbit.acknowledge_message(message_id)
        print(json.dumps(ack_result, indent=2))
    
    # Get queue info
    print("\n=== Queue Information ===")
    result = rabbit.get_queue_info("agent.001.tasks")
    print(json.dumps(result, indent=2))
    
    rabbit.close()
