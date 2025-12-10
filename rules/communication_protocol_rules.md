# Communication Protocol Rules

**Priority**: 🤝 Collaboration (Multi-Agent Systems)

## Overview
Rules for structured communication between agents in multi-agent systems.

## Rules

### PROT-001: Use Standardized Message Formats
- JSON schema for all messages
- Required fields: sender, recipient, timestamp, message_type
- Version all message formats
- Validate messages against schema

### PROT-002: Implement Heartbeat Mechanisms
- Regular heartbeat messages (every 30s)
- Detect failed/unresponsive agents
- Auto-recovery procedures
- Health status reporting

### PROT-003: Handle Message Ordering and Delivery
- Sequence numbers for messages
- Acknowledge receipt
- Retry failed deliveries
- Handle out-of-order messages

### PROT-004: Implement Message Acknowledgment
- Send ACK for received messages
- Track unacknowledged messages
- Resend if no ACK within timeout
- Log delivery failures

### PROT-005: Use RabbitMQ for Async Communication
- Queue per agent or agent role
- Topic exchanges for broadcast
- Dead letter queues for failed messages
- Persistent messages for critical data

### PROT-006: Encrypt Sensitive Inter-Agent Messages
- TLS for all connections
- Message-level encryption for sensitive data
- Key rotation policies
- Audit encrypted communications

## Message Format

```json
{
  "message_id": "msg-12345",
  "version": "2.0",
  "timestamp": "2025-12-08T12:00:00Z",
  "sender": "agent-001",
  "recipient": "agent-002",
  "message_type": "task_delegation",
  "priority": "high",
  "payload": {
    "task_id": "task-789",
    "action": "execute",
    "parameters": {}
  },
  "requires_ack": true
}
```

## RabbitMQ Integration

### Exchange Types
- **Direct**: Point-to-point messaging
- **Topic**: Pattern-based routing
- **Fanout**: Broadcast to all

### Queue Naming
- `agent.{agent_id}.tasks`
- `agent.{agent_id}.responses`
- `broadcast.all`
- `broadcast.{role}`

---
**Version**: 2.0.0  
**Last Updated**: 2025-12-08
