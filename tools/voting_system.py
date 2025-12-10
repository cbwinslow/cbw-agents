#!/usr/bin/env python3
"""
Voting System Tool

Implements democratic voting mechanisms for multi-agent systems with support for
multiple voting strategies, quorum requirements, and consensus building.

OpenAI Compatible: Yes
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VotingStrategy(Enum):
    """Voting strategy types."""
    SIMPLE_MAJORITY = "simple_majority"  # 51%
    SUPERMAJORITY_TWO_THIRDS = "supermajority_2/3"  # 66.67%
    SUPERMAJORITY_THREE_QUARTERS = "supermajority_3/4"  # 75%
    UNANIMOUS = "unanimous"  # 100%
    WEIGHTED = "weighted"  # Weighted by agent expertise/role
    RANKED_CHOICE = "ranked_choice"  # Ranked choice voting


class VoteChoice(Enum):
    """Standard vote choices."""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


class VotingSystemTool:
    """
    Democratic voting system for multi-agent collaboration.
    
    Features:
    - Multiple voting strategies
    - Quorum requirements
    - Vote weighting by expertise
    - Audit trail
    - Tie-breaking mechanisms
    - Consensus tracking
    """
    
    def __init__(self, db_path: str = "./voting_system.db"):
        """
        Initialize voting system.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
        
        logger.info(f"VotingSystem initialized: db={db_path}")
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create proposals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    proposal_type TEXT,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    deadline TEXT,
                    voting_strategy TEXT NOT NULL,
                    quorum_percent REAL NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    decided_at TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create votes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposal_id INTEGER NOT NULL,
                    agent_id TEXT NOT NULL,
                    vote_choice TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    reasoning TEXT,
                    voted_at TEXT NOT NULL,
                    FOREIGN KEY (proposal_id) REFERENCES proposals(id),
                    UNIQUE(proposal_id, agent_id)
                )
            ''')
            
            # Create agents table (for tracking eligible voters)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT,
                    expertise_areas TEXT,
                    default_weight REAL DEFAULT 1.0,
                    active BOOLEAN DEFAULT 1,
                    registered_at TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
            logger.info("Voting database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def register_agent(self, agent_id: str, name: str, role: Optional[str] = None,
                      expertise_areas: Optional[List[str]] = None, 
                      default_weight: float = 1.0) -> Dict[str, Any]:
        """
        Register an agent as an eligible voter.
        
        Args:
            agent_id: Unique agent identifier
            name: Agent name
            role: Agent role in the system
            expertise_areas: List of expertise areas
            default_weight: Default voting weight
            
        Returns:
            Success status
        """
        try:
            expertise_json = json.dumps(expertise_areas or [])
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agents (id, name, role, expertise_areas, default_weight, registered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (agent_id, name, role, expertise_json, default_weight, datetime.now().isoformat()))
            
            self.conn.commit()
            
            return {
                "success": True,
                "agent_id": agent_id,
                "name": name,
                "default_weight": default_weight
            }
            
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_proposal(self, title: str, description: str, created_by: str,
                       voting_strategy: str = "simple_majority", quorum_percent: float = 51.0,
                       deadline_hours: Optional[int] = None, proposal_type: str = "general",
                       metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a new proposal for voting.
        
        Args:
            title: Proposal title
            description: Detailed description
            created_by: Agent ID creating the proposal
            voting_strategy: Voting strategy to use
            quorum_percent: Minimum participation percentage
            deadline_hours: Hours until voting closes (None for no deadline)
            proposal_type: Type of proposal
            metadata: Additional metadata
            
        Returns:
            Proposal ID and details
        """
        try:
            # Validate voting strategy
            if voting_strategy not in [s.value for s in VotingStrategy]:
                return {
                    "success": False,
                    "error": f"Invalid voting strategy: {voting_strategy}"
                }
            
            deadline = None
            if deadline_hours:
                deadline = (datetime.now() + timedelta(hours=deadline_hours)).isoformat()
            
            metadata_json = json.dumps(metadata or {})
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO proposals (title, description, proposal_type, created_by, created_at,
                                     deadline, voting_strategy, quorum_percent, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, proposal_type, created_by, datetime.now().isoformat(),
                  deadline, voting_strategy, quorum_percent, "open", metadata_json))
            
            proposal_id = cursor.lastrowid
            self.conn.commit()
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "title": title,
                "voting_strategy": voting_strategy,
                "quorum_percent": quorum_percent,
                "deadline": deadline,
                "status": "open"
            }
            
        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cast_vote(self, proposal_id: int, agent_id: str, vote_choice: str,
                  reasoning: Optional[str] = None, weight_override: Optional[float] = None) -> Dict[str, Any]:
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: Proposal identifier
            agent_id: Agent casting the vote
            vote_choice: Vote choice (yes, no, abstain)
            reasoning: Explanation for the vote
            weight_override: Override default vote weight
            
        Returns:
            Success status
        """
        try:
            # Validate proposal exists and is open
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
            proposal = cursor.fetchone()
            
            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }
            
            if proposal['status'] != 'open':
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} is {proposal['status']}, not accepting votes"
                }
            
            # Check deadline
            if proposal['deadline']:
                deadline = datetime.fromisoformat(proposal['deadline'])
                if datetime.now() > deadline:
                    return {
                        "success": False,
                        "error": "Voting deadline has passed"
                    }
            
            # Validate vote choice
            if vote_choice not in [c.value for c in VoteChoice]:
                return {
                    "success": False,
                    "error": f"Invalid vote choice: {vote_choice}"
                }
            
            # Get agent weight
            cursor.execute('SELECT default_weight FROM agents WHERE id = ?', (agent_id,))
            agent = cursor.fetchone()
            weight = weight_override if weight_override is not None else (agent['default_weight'] if agent else 1.0)
            
            # Cast vote (insert or update)
            cursor.execute('''
                INSERT OR REPLACE INTO votes (proposal_id, agent_id, vote_choice, weight, reasoning, voted_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (proposal_id, agent_id, vote_choice, weight, reasoning, datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Check if we should tally
            tally_result = self._check_and_tally(proposal_id)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "agent_id": agent_id,
                "vote_choice": vote_choice,
                "weight": weight,
                "auto_tallied": tally_result is not None,
                "tally_result": tally_result
            }
            
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_and_tally(self, proposal_id: int) -> Optional[Dict[str, Any]]:
        """Check if quorum reached and tally if appropriate."""
        try:
            cursor = self.conn.cursor()
            
            # Get proposal details
            cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
            proposal = cursor.fetchone()
            
            if proposal['status'] != 'open':
                return None
            
            # Count eligible voters
            cursor.execute('SELECT COUNT(*) as count FROM agents WHERE active = 1')
            total_eligible = cursor.fetchone()['count']
            
            # Count votes
            cursor.execute('SELECT COUNT(*) as count FROM votes WHERE proposal_id = ?', (proposal_id,))
            total_votes = cursor.fetchone()['count']
            
            # Check quorum
            participation = (total_votes / total_eligible * 100) if total_eligible > 0 else 0
            
            # Check if deadline passed
            deadline_passed = False
            if proposal['deadline']:
                deadline = datetime.fromisoformat(proposal['deadline'])
                deadline_passed = datetime.now() > deadline
            
            # Tally if quorum reached or deadline passed
            if participation >= proposal['quorum_percent'] or deadline_passed:
                return self.tally_votes(proposal_id)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking quorum: {e}")
            return None
    
    def tally_votes(self, proposal_id: int) -> Dict[str, Any]:
        """
        Tally votes and determine result.
        
        Args:
            proposal_id: Proposal identifier
            
        Returns:
            Vote tally and result
        """
        try:
            cursor = self.conn.cursor()
            
            # Get proposal
            cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
            proposal = cursor.fetchone()
            
            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }
            
            # Get all votes
            cursor.execute('''
                SELECT vote_choice, weight, reasoning, agent_id
                FROM votes WHERE proposal_id = ?
            ''', (proposal_id,))
            votes = cursor.fetchall()
            
            # Tally by strategy
            strategy = proposal['voting_strategy']
            
            if strategy == VotingStrategy.WEIGHTED.value:
                result = self._tally_weighted(votes)
            elif strategy == VotingStrategy.RANKED_CHOICE.value:
                result = self._tally_ranked_choice(votes)
            else:
                result = self._tally_standard(votes, strategy)
            
            # Update proposal with result
            cursor.execute('''
                UPDATE proposals 
                SET status = ?, result = ?, decided_at = ?
                WHERE id = ?
            ''', ('decided', result['decision'], datetime.now().isoformat(), proposal_id))
            
            self.conn.commit()
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "title": proposal['title'],
                "voting_strategy": strategy,
                "total_votes": len(votes),
                "tally": result,
                "decision": result['decision']
            }
            
        except Exception as e:
            logger.error(f"Error tallying votes: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _tally_standard(self, votes: List[sqlite3.Row], strategy: str) -> Dict[str, Any]:
        """Tally votes using standard strategies."""
        yes_count = sum(1 for v in votes if v['vote_choice'] == VoteChoice.YES.value)
        no_count = sum(1 for v in votes if v['vote_choice'] == VoteChoice.NO.value)
        abstain_count = sum(1 for v in votes if v['vote_choice'] == VoteChoice.ABSTAIN.value)
        
        total_votes = yes_count + no_count  # Abstains don't count towards total
        
        if total_votes == 0:
            return {
                "decision": "no_quorum",
                "yes": 0,
                "no": 0,
                "abstain": abstain_count,
                "yes_percent": 0,
                "no_percent": 0
            }
        
        yes_percent = (yes_count / total_votes) * 100
        no_percent = (no_count / total_votes) * 100
        
        # Determine threshold based on strategy
        thresholds = {
            VotingStrategy.SIMPLE_MAJORITY.value: 50.0,
            VotingStrategy.SUPERMAJORITY_TWO_THIRDS.value: 66.67,
            VotingStrategy.SUPERMAJORITY_THREE_QUARTERS.value: 75.0,
            VotingStrategy.UNANIMOUS.value: 100.0
        }
        
        threshold = thresholds.get(strategy, 50.0)
        decision = "approved" if yes_percent > threshold else "rejected"
        
        return {
            "decision": decision,
            "yes": yes_count,
            "no": no_count,
            "abstain": abstain_count,
            "yes_percent": yes_percent,
            "no_percent": no_percent,
            "threshold": threshold
        }
    
    def _tally_weighted(self, votes: List[sqlite3.Row]) -> Dict[str, Any]:
        """Tally votes with weighting."""
        yes_weight = sum(v['weight'] for v in votes if v['vote_choice'] == VoteChoice.YES.value)
        no_weight = sum(v['weight'] for v in votes if v['vote_choice'] == VoteChoice.NO.value)
        abstain_weight = sum(v['weight'] for v in votes if v['vote_choice'] == VoteChoice.ABSTAIN.value)
        
        total_weight = yes_weight + no_weight
        
        if total_weight == 0:
            return {
                "decision": "no_quorum",
                "yes_weight": 0,
                "no_weight": 0,
                "abstain_weight": abstain_weight
            }
        
        yes_percent = (yes_weight / total_weight) * 100
        decision = "approved" if yes_percent > 50.0 else "rejected"
        
        return {
            "decision": decision,
            "yes_weight": yes_weight,
            "no_weight": no_weight,
            "abstain_weight": abstain_weight,
            "yes_percent": yes_percent,
            "no_percent": (no_weight / total_weight) * 100
        }
    
    def _tally_ranked_choice(self, votes: List[sqlite3.Row]) -> Dict[str, Any]:
        """Tally ranked choice votes (simplified)."""
        # Simplified: treat as weighted vote based on reasoning strength
        return self._tally_weighted(votes)
    
    def get_proposal(self, proposal_id: int, include_votes: bool = False) -> Dict[str, Any]:
        """
        Get proposal details.
        
        Args:
            proposal_id: Proposal identifier
            include_votes: Include individual votes
            
        Returns:
            Proposal details
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM proposals WHERE id = ?', (proposal_id,))
            proposal = cursor.fetchone()
            
            if not proposal:
                return {
                    "success": False,
                    "error": f"Proposal {proposal_id} not found"
                }
            
            proposal_dict = dict(proposal)
            proposal_dict['metadata'] = json.loads(proposal_dict['metadata'])
            
            # Get vote summary
            cursor.execute('''
                SELECT COUNT(*) as count, vote_choice
                FROM votes WHERE proposal_id = ?
                GROUP BY vote_choice
            ''', (proposal_id,))
            vote_summary = {row['vote_choice']: row['count'] for row in cursor.fetchall()}
            
            proposal_dict['vote_summary'] = vote_summary
            
            if include_votes:
                cursor.execute('''
                    SELECT v.*, a.name as agent_name
                    FROM votes v
                    LEFT JOIN agents a ON v.agent_id = a.id
                    WHERE v.proposal_id = ?
                    ORDER BY v.voted_at
                ''', (proposal_id,))
                votes = [dict(row) for row in cursor.fetchall()]
                proposal_dict['votes'] = votes
            
            return {
                "success": True,
                "proposal": proposal_dict
            }
            
        except Exception as e:
            logger.error(f"Error getting proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_proposals(self, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        List proposals.
        
        Args:
            status: Filter by status (open, decided, closed)
            limit: Maximum results
            
        Returns:
            List of proposals
        """
        try:
            cursor = self.conn.cursor()
            
            sql = 'SELECT * FROM proposals'
            params = []
            
            if status:
                sql += ' WHERE status = ?'
                params.append(status)
            
            sql += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(sql, params)
            proposals = []
            
            for row in cursor.fetchall():
                proposal = dict(row)
                proposal['metadata'] = json.loads(proposal['metadata'])
                proposals.append(proposal)
            
            return {
                "success": True,
                "count": len(proposals),
                "proposals": proposals
            }
            
        except Exception as e:
            logger.error(f"Error listing proposals: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Voting database connection closed")


# OpenAI Function Definitions
OPENAI_FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_proposal",
            "description": "Create a new proposal for democratic voting",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Proposal title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "created_by": {"type": "string", "description": "Agent ID creating the proposal"},
                    "voting_strategy": {
                        "type": "string",
                        "enum": ["simple_majority", "supermajority_2/3", "supermajority_3/4", "unanimous", "weighted"],
                        "description": "Voting strategy to use"
                    },
                    "quorum_percent": {"type": "number", "description": "Minimum participation percentage"},
                    "deadline_hours": {"type": "integer", "description": "Hours until voting closes"}
                },
                "required": ["title", "description", "created_by"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cast_vote",
            "description": "Cast a vote on a proposal",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "integer", "description": "Proposal identifier"},
                    "agent_id": {"type": "string", "description": "Agent casting the vote"},
                    "vote_choice": {
                        "type": "string",
                        "enum": ["yes", "no", "abstain"],
                        "description": "Vote choice"
                    },
                    "reasoning": {"type": "string", "description": "Explanation for the vote"}
                },
                "required": ["proposal_id", "agent_id", "vote_choice"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tally_votes",
            "description": "Tally votes and determine result for a proposal",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "integer", "description": "Proposal identifier"}
                },
                "required": ["proposal_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_proposal",
            "description": "Get proposal details and voting status",
            "parameters": {
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "integer", "description": "Proposal identifier"},
                    "include_votes": {"type": "boolean", "description": "Include individual votes"}
                },
                "required": ["proposal_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_proposals",
            "description": "List proposals with optional status filter",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["open", "decided", "closed"],
                        "description": "Filter by status"
                    },
                    "limit": {"type": "integer", "description": "Maximum results"}
                }
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
        voting = VotingSystemTool(db_path=db_path)
        
        # Register agents
        print("\n=== Registering Agents ===")
        voting.register_agent("agent-001", "Code Analyzer", role="specialist", expertise_areas=["code"], default_weight=1.2)
        voting.register_agent("agent-002", "Security Expert", role="specialist", expertise_areas=["security"], default_weight=1.5)
        voting.register_agent("agent-003", "Generalist", role="generalist", default_weight=1.0)
        
        # Create proposal
        print("\n=== Creating Proposal ===")
        result = voting.create_proposal(
            title="Adopt new coding standard",
            description="Should we adopt PEP 8 coding standard for all Python code?",
            created_by="agent-001",
            voting_strategy="supermajority_2/3",
            quorum_percent=66.0,
            deadline_hours=24
        )
        print(json.dumps(result, indent=2))
        proposal_id = result['proposal_id']
        
        # Cast votes
        print("\n=== Casting Votes ===")
        result = voting.cast_vote(proposal_id, "agent-001", "yes", reasoning="Improves code consistency")
        print(json.dumps(result, indent=2))
        
        result = voting.cast_vote(proposal_id, "agent-002", "yes", reasoning="Good practice for maintainability")
        print(json.dumps(result, indent=2))
        
        result = voting.cast_vote(proposal_id, "agent-003", "yes", reasoning="I agree with the experts")
        print(json.dumps(result, indent=2))
        
        # Get proposal with votes
        print("\n=== Proposal Details ===")
        result = voting.get_proposal(proposal_id, include_votes=True)
        print(json.dumps(result, indent=2))
        
        voting.close()
        
    finally:
        os.unlink(db_path)
        print(f"\nCleaned up temporary database: {db_path}")
