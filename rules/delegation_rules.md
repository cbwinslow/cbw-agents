# Delegation Rules

**Priority**: 🤝 Collaboration (Multi-Agent Systems)

## Overview
Rules for effective task delegation between agents in multi-agent systems.

## Rules

### DEL-001: Clearly Define Task Scope Before Delegation
- Specific, measurable objectives
- Clear success criteria
- Define inputs and expected outputs
- Specify constraints and requirements

### DEL-002: Match Tasks to Agent Capabilities
- Review agent capabilities and specializations
- Consider current workload
- Match expertise to task requirements
- Avoid overloading single agents

### DEL-003: Track Delegation Chain and Accountability
- Record delegator → delegatee
- Maintain delegation history
- Clear accountability at each level
- Prevent circular delegations

### DEL-004: Set Clear Deadlines and Expectations
- Realistic time estimates
- Milestone checkpoints
- Progress reporting intervals
- Escalation procedures

### DEL-005: Monitor Delegated Task Progress
- Regular status checks
- Automated progress reports
- Early warning for delays
- Support for blockers

### DEL-006: Provide Feedback on Completed Delegations
- Quality assessment
- Timeliness evaluation
- Learning for future delegations
- Recognition for good work

## Delegation Protocol

```json
{
  "delegation_id": "del-001",
  "from_agent": "coordinator-001",
  "to_agent": "specialist-002",
  "task": {
    "description": "Analyze codebase for security vulnerabilities",
    "requirements": ["scan_tools", "report_format"],
    "deadline": "2025-12-09T12:00:00Z"
  },
  "status": "in_progress",
  "checkpoints": ["25%", "50%", "75%", "complete"]
}
```

---
**Version**: 2.0.0  
**Last Updated**: 2025-12-08
