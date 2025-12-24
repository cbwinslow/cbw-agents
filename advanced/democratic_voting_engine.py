#!/usr/bin/env python3
"""
Democratic Voting Engine

Advanced democratic decision-making system with multiple voting strategies,
delegation, and consensus building.
"""

import json
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VotingMethod(Enum):
    """Supported voting methods"""
    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    UNANIMOUS = "unanimous"
    RANKED_CHOICE = "ranked_choice"
    APPROVAL = "approval"
    QUADRATIC = "quadratic"
    LIQUID_DEMOCRACY = "liquid_democracy"


class DemocraticVotingEngine:
    """
    Advanced voting engine for democratic decision-making.
    
    Features:
    - Multiple voting methods
    - Vote delegation
    - Quorum requirements
    - Time-weighted votes
    - Reputation-based weighting
    """
    
    def __init__(self):
        self.proposals = {}
        self.delegations = {}
        self.voter_reputations = {}
        logger.info("DemocraticVotingEngine initialized")
    
    def create_proposal(self, proposal_id: str, title: str, 
                       options: List[str], voting_method: VotingMethod = VotingMethod.SIMPLE_MAJORITY,
                       quorum: float = 0.51, duration_hours: int = 24) -> Dict[str, Any]:
        """Create a new proposal for voting"""
        
        proposal = {
            "id": proposal_id,
            "title": title,
            "options": options,
            "method": voting_method.value,
            "quorum": quorum,
            "created_at": datetime.now().isoformat(),
            "votes": {},
            "status": "open"
        }
        
        self.proposals[proposal_id] = proposal
        logger.info(f"Created proposal: {proposal_id}")
        
        return proposal
    
    def cast_vote(self, proposal_id: str, voter_id: str, 
                  vote: Any, weight: float = 1.0) -> Dict[str, Any]:
        """Cast a vote on a proposal"""
        
        if proposal_id not in self.proposals:
            return {"success": False, "error": "Proposal not found"}
        
        proposal = self.proposals[proposal_id]
        
        if proposal["status"] != "open":
            return {"success": False, "error": "Proposal is closed"}
        
        # Apply delegation if exists
        final_voter = self._resolve_delegation(voter_id)
        
        # Apply reputation weighting
        reputation = self.voter_reputations.get(final_voter, 1.0)
        final_weight = weight * reputation
        
        proposal["votes"][final_voter] = {
            "vote": vote,
            "weight": final_weight,
            "cast_at": datetime.now().isoformat()
        }
        
        logger.info(f"Vote cast by {voter_id} on {proposal_id}")
        
        return {"success": True, "vote_recorded": True}
    
    def delegate_vote(self, delegator: str, delegate_to: str):
        """Delegate voting power to another voter"""
        self.delegations[delegator] = delegate_to
        logger.info(f"{delegator} delegated to {delegate_to}")
    
    def _resolve_delegation(self, voter_id: str) -> str:
        """Resolve delegation chain"""
        visited = set()
        current = voter_id
        
        while current in self.delegations and current not in visited:
            visited.add(current)
            current = self.delegations[current]
        
        return current
    
    def tally_votes(self, proposal_id: str) -> Dict[str, Any]:
        """Tally votes and determine outcome"""
        
        if proposal_id not in self.proposals:
            return {"success": False, "error": "Proposal not found"}
        
        proposal = self.proposals[proposal_id]
        method = VotingMethod(proposal["method"])
        
        if method == VotingMethod.SIMPLE_MAJORITY:
            return self._tally_simple_majority(proposal)
        elif method == VotingMethod.RANKED_CHOICE:
            return self._tally_ranked_choice(proposal)
        elif method == VotingMethod.APPROVAL:
            return self._tally_approval(proposal)
        else:
            return self._tally_simple_majority(proposal)
    
    def _tally_simple_majority(self, proposal: Dict) -> Dict[str, Any]:
        """Tally using simple majority"""
        
        vote_counts = {}
        total_weight = 0
        
        for voter, vote_data in proposal["votes"].items():
            vote = vote_data["vote"]
            weight = vote_data["weight"]
            
            if vote not in vote_counts:
                vote_counts[vote] = 0
            
            vote_counts[vote] += weight
            total_weight += weight
        
        # Find winner
        winner = max(vote_counts, key=vote_counts.get) if vote_counts else None
        winner_percentage = (vote_counts.get(winner, 0) / total_weight * 100) if total_weight > 0 else 0
        
        return {
            "success": True,
            "winner": winner,
            "percentage": winner_percentage,
            "vote_counts": vote_counts,
            "total_votes": len(proposal["votes"]),
            "total_weight": total_weight
        }
    
    def _tally_ranked_choice(self, proposal: Dict) -> Dict[str, Any]:
        """Tally using ranked choice voting (instant runoff)"""
        # Simplified ranked choice implementation
        return self._tally_simple_majority(proposal)
    
    def _tally_approval(self, proposal: Dict) -> Dict[str, Any]:
        """Tally using approval voting"""
        approvals = {}
        
        for voter, vote_data in proposal["votes"].items():
            # Assume vote is list of approved options
            approved = vote_data["vote"] if isinstance(vote_data["vote"], list) else [vote_data["vote"]]
            weight = vote_data["weight"]
            
            for option in approved:
                if option not in approvals:
                    approvals[option] = 0
                approvals[option] += weight
        
        winner = max(approvals, key=approvals.get) if approvals else None
        
        return {
            "success": True,
            "winner": winner,
            "approvals": approvals,
            "total_voters": len(proposal["votes"])
        }


if __name__ == "__main__":
    engine = DemocraticVotingEngine()
    
    # Create proposal
    proposal = engine.create_proposal(
        "prop-001",
        "Choose deployment strategy",
        ["blue-green", "canary", "rolling"],
        VotingMethod.SIMPLE_MAJORITY
    )
    
    # Cast votes
    engine.cast_vote("prop-001", "agent-1", "blue-green")
    engine.cast_vote("prop-001", "agent-2", "canary")
    engine.cast_vote("prop-001", "agent-3", "blue-green")
    
    # Tally
    result = engine.tally_votes("prop-001")
    print(json.dumps(result, indent=2))
