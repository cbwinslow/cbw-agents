# Quick Start Guide - CBW Agents

## Overview

This guide will help you quickly get started with the expanded CBW Agents system featuring 169 tools, 133 agents, 17 crews, and advanced autonomous systems.

## Installation

```bash
# Clone the repository
git clone https://github.com/cbwinslow/cbw-agents.git
cd cbw-agents

# Install Python dependencies (if needed)
pip install -r requirements.txt
```

## Directory Structure

```
cbw-agents/
├── tools/          # 169 OpenAI-compatible tools
├── agents/         # 133 agent configurations
├── crews/          # 17 crew/team configurations
├── advanced/       # Advanced systems and algorithms
├── rules/          # Agent behavior rules
└── examples/       # Usage examples
```

## Quick Examples

### 1. Using a Knowledge Graph Tool

```python
from tools.knowledge_graph import KnowledgeGraphTool

# Initialize
kg = KnowledgeGraphTool()

# Add entities
kg.add_entity("Python", "programming_language")
kg.add_entity("AI", "technology_domain")

# Add relationships
kg.add_relationship("Python", "AI", "used_in", strength=0.9)

# Query
result = kg.query_entity("Python", include_relationships=True)
print(result)
```

### 2. Setting Up a Continuous Agent Runtime

```python
from advanced.continuous_agent_runtime import ContinuousAgentRuntime
import time

# Define work function
def agent_work():
    print(f"Agent working at {time.time()}")
    time.sleep(1)

# Define health check
def health_check():
    return True  # Agent is healthy

# Initialize runtime
runtime = ContinuousAgentRuntime("my-agent", check_interval=60)
runtime.register_health_check(health_check, "basic_health")

# Start continuous operation
runtime.start(agent_work)

# Run for a while
time.sleep(300)  # 5 minutes

# Stop gracefully
runtime.stop()
print(runtime.get_status())
```

### 3. Democratic Decision Making

```python
from advanced.democratic_voting_engine import DemocraticVotingEngine, VotingMethod

# Initialize engine
engine = DemocraticVotingEngine()

# Create proposal
proposal = engine.create_proposal(
    proposal_id="deploy-001",
    title="Choose deployment strategy",
    options=["blue-green", "canary", "rolling"],
    voting_method=VotingMethod.SIMPLE_MAJORITY,
    quorum=0.6
)

# Agents cast votes
engine.cast_vote("deploy-001", "agent-1", "blue-green")
engine.cast_vote("deploy-001", "agent-2", "canary")
engine.cast_vote("deploy-001", "agent-3", "blue-green")
engine.cast_vote("deploy-001", "agent-4", "blue-green")

# Tally votes
result = engine.tally_votes("deploy-001")
print(f"Winner: {result['winner']} with {result['percentage']:.1f}%")
```

### 4. Self-Learning Agent

```python
from advanced.self_learning_engine import SelfLearningEngine

# Initialize learning engine
learner = SelfLearningEngine("learning-agent-001")

# Record experiences
learner.record_experience(
    task_type="code_review",
    action="analyze_code",
    outcome="found_3_issues",
    success=True,
    metrics={"issues_found": 3, "time_taken": 45}
)

# Acquire skills
learner.acquire_skill("python", initial_level=3)
learner.practice_skill("python", success=True)
learner.practice_skill("python", success=True)

# Get improvement suggestions
suggestions = learner.suggest_improvement()
print("Improvement suggestions:", suggestions)

# Get learning summary
summary = learner.get_learning_summary()
print("Learning summary:", summary)
```

### 5. Hierarchical Memory System

```python
from tools.hierarchical_memory import HierarchicalMemoryTool

# Initialize memory
memory = HierarchicalMemoryTool()

# Store memories at different levels
memory.store_memory(
    "Python is great for AI",
    level="working",
    context="programming",
    importance=0.7
)

memory.store_memory(
    "Deep learning revolutionized AI",
    level="long_term",
    context="technology",
    importance=0.9
)

memory.store_memory(
    "Neural networks are inspired by brain",
    level="semantic",
    context="knowledge",
    importance=0.85
)

# Retrieve memories
results = memory.retrieve_memory(
    level="semantic",
    min_importance=0.8,
    limit=10
)

print(f"Found {results['count']} memories")
for mem in results['memories']:
    print(f"- {mem['content']} (importance: {mem['importance']})")

# Get memory statistics
stats = memory.get_memory_stats()
print("Memory stats:", stats)
```

### 6. Loading an Agent Configuration

```python
import json

# Load agent configuration
with open('agents/machine_learning_engineer_agent.json') as f:
    agent_config = json.load(f)

print(f"Agent: {agent_config['agent_name']}")
print(f"Type: {agent_config['agent_type']}")
print(f"Tools: {', '.join(agent_config['tools'])}")
print(f"Capabilities: {', '.join(agent_config['capabilities'])}")
```

### 7. Loading a Crew Configuration

```python
import json

# Load crew configuration
with open('crews/democratic_research_crew.json') as f:
    crew_config = json.load(f)

print(f"Crew: {crew_config['crew_name']}")
print(f"Type: {crew_config['crew_type']}")
print(f"Process: {crew_config['process']['type']}")
print(f"Members: {len(crew_config.get('team_members', []))}")
```

## Advanced Use Cases

### Creating an Autonomous Self-Managing Team

```python
from advanced.continuous_agent_runtime import ContinuousAgentRuntime
from advanced.democratic_voting_engine import DemocraticVotingEngine
from advanced.self_learning_engine import SelfLearningEngine
from tools.hierarchical_memory import HierarchicalMemoryTool
import json

class AutonomousTeam:
    def __init__(self, team_id, agent_ids):
        self.team_id = team_id
        self.agent_ids = agent_ids
        
        # Initialize components
        self.runtime = ContinuousAgentRuntime(team_id)
        self.voting = DemocraticVotingEngine()
        self.learning = SelfLearningEngine(team_id)
        self.memory = HierarchicalMemoryTool()
        
        # Register health checks
        self.runtime.register_health_check(self._check_team_health, "team_health")
    
    def _check_team_health(self):
        # Check if team is functioning properly
        return True
    
    def work(self):
        # Main work loop
        # 1. Check for tasks
        # 2. Make decisions democratically
        # 3. Execute tasks
        # 4. Learn from outcomes
        # 5. Store knowledge
        pass
    
    def make_decision(self, proposal_id, title, options):
        # Create proposal
        self.voting.create_proposal(proposal_id, title, options)
        
        # Each agent votes
        for agent_id in self.agent_ids:
            # Agent evaluates options and votes
            vote = self._agent_evaluate(agent_id, options)
            self.voting.cast_vote(proposal_id, agent_id, vote)
        
        # Tally and return result
        return self.voting.tally_votes(proposal_id)
    
    def _agent_evaluate(self, agent_id, options):
        # Agent evaluation logic
        return options[0]  # Simplified
    
    def start(self):
        """Start autonomous team operation"""
        self.runtime.start(self.work)
        print(f"Team {self.team_id} started")
    
    def stop(self):
        """Stop team operation"""
        self.runtime.stop()
        print(f"Team {self.team_id} stopped")

# Usage
team = AutonomousTeam("dev-team-001", ["agent-1", "agent-2", "agent-3"])
team.start()

# Team runs autonomously, making decisions, learning, and improving
```

## Tool Categories Overview

### Knowledge Management (15 tools)
- Knowledge graphs, memory systems, semantic search
- Use for: Knowledge bases, information retrieval, learning

### Testing & QA (15 tools)
- Test automation, security scanning, coverage analysis
- Use for: Quality assurance, CI/CD, security

### Monitoring & Operations (15 tools)
- 24/7 monitoring, health checks, incident response
- Use for: Production operations, SRE, DevOps

### Task Management (14 tools)
- Scheduling, prioritization, workflow orchestration
- Use for: Project management, task coordination

### Communication & Collaboration (15 tools)
- A2A protocol, messaging, consensus building
- Use for: Multi-agent coordination, team collaboration

### Learning & Adaptation (15 tools)
- Skill tracking, performance analysis, improvement
- Use for: Agent development, continuous improvement

### Decision Support (15 tools)
- Multi-criteria decision making, risk assessment
- Use for: Strategic planning, option evaluation

### Data Intelligence (15 tools)
- Pattern recognition, trend forecasting, analysis
- Use for: Data science, analytics, insights

### Resource Management (15 tools)
- Allocation, budgeting, optimization
- Use for: Resource planning, cost control

### Security & Compliance (15 tools)
- Access control, encryption, threat detection
- Use for: Security, compliance, privacy

## Agent Categories Overview

### Specialized Domain (20 agents)
Engineers, scientists, architects, specialists

### Team Players (20 agents)
Facilitators, mentors, coordinators, leaders

### Task Management (15 agents)
Planners, trackers, organizers

### Democratic Voting (10 agents)
Coordinators, facilitators, moderators

### Memory Organization (10 agents)
Curators, organizers, indexers

### Testing & Monitoring (15 agents)
QA engineers, monitors, auditors

### Self-Improvement (5 agents)
Learners, analyzers, developers

### Research & Analysis (10 agents)
Researchers, analysts, reviewers

### Communication (10 agents)
Writers, translators, documenters

### Innovation (10 agents)
Innovators, designers, creators

## Best Practices

1. **Start Simple**: Begin with single tools/agents before building teams
2. **Use Hierarchical Memory**: Store important learnings in appropriate memory levels
3. **Enable Learning**: Always enable learning for continuous improvement
4. **Monitor Health**: Use health checks for production systems
5. **Democratic Decisions**: Use voting for important team decisions
6. **Document Context**: Store context in memory for future reference
7. **Test Thoroughly**: Use testing tools before deployment
8. **Monitor Continuously**: Use monitoring tools for production systems

## Troubleshooting

### Tool Import Issues
```python
# Make sure you're in the right directory
import sys
sys.path.append('/path/to/cbw-agents')

from tools.knowledge_graph import KnowledgeGraphTool
```

### Agent Configuration Loading
```python
import json
import os

# Use absolute path
config_path = os.path.join(os.path.dirname(__file__), 'agents', 'agent_name.json')
with open(config_path) as f:
    config = json.load(f)
```

### Database Permissions
```python
# For SQLite-based tools, ensure write permissions
import os
db_path = "./my_database.db"
os.chmod(os.path.dirname(db_path), 0o755)
```

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for more use cases
2. **Read Documentation**: Review `EXPANSION_SUMMARY.md` for detailed information
3. **Customize Agents**: Modify agent configurations for your needs
4. **Build Teams**: Create custom crew configurations
5. **Integrate Tools**: Combine tools for powerful workflows
6. **Monitor & Learn**: Enable monitoring and learning for production use

## Support

- **Documentation**: See `EXPANSION_SUMMARY.md`
- **Examples**: Check `examples/` directory
- **Issues**: Report on GitHub
- **Community**: Join discussions

## Version

**Version**: 2.0.0 (Major Expansion)
**Date**: 2025-12-23
**Components**: 320+ tools, agents, crews, and systems
