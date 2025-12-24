#!/usr/bin/env python3
"""
Self-Learning Engine

Autonomous learning system that enables agents to learn from experience,
improve performance, and acquire new skills.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelfLearningEngine:
    """
    Self-learning and improvement system.
    
    Features:
    - Experience tracking
    - Performance analysis
    - Skill acquisition
    - Strategy optimization
    - Knowledge synthesis
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.experiences = []
        self.skills = {}
        self.performance_history = defaultdict(list)
        self.learning_rate = 0.1
        self.strategies = {}
        
        logger.info(f"SelfLearningEngine initialized for {agent_id}")
    
    def record_experience(self, task_type: str, action: str, 
                         outcome: str, success: bool, 
                         metrics: Optional[Dict] = None) -> Dict[str, Any]:
        """Record an experience for learning"""
        
        experience = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "action": action,
            "outcome": outcome,
            "success": success,
            "metrics": metrics or {}
        }
        
        self.experiences.append(experience)
        self.performance_history[task_type].append(1 if success else 0)
        
        # Trigger learning if enough experiences
        if len(self.experiences) % 10 == 0:
            self._analyze_and_learn()
        
        logger.info(f"Experience recorded: {task_type} - {'success' if success else 'failure'}")
        
        return {"success": True, "experience_id": len(self.experiences) - 1}
    
    def assess_skill(self, skill_name: str) -> Dict[str, Any]:
        """Assess current skill level"""
        
        if skill_name not in self.skills:
            return {
                "skill": skill_name,
                "level": 0,
                "proficiency": "novice",
                "experiences": 0
            }
        
        skill = self.skills[skill_name]
        proficiency = self._calculate_proficiency(skill["level"])
        
        return {
            "skill": skill_name,
            "level": skill["level"],
            "proficiency": proficiency,
            "experiences": skill["experience_count"],
            "last_practiced": skill.get("last_practiced")
        }
    
    def suggest_improvement(self) -> List[Dict[str, Any]]:
        """Suggest areas for improvement"""
        
        suggestions = []
        
        # Analyze performance by task type
        for task_type, results in self.performance_history.items():
            if len(results) >= 5:
                success_rate = statistics.mean(results)
                
                if success_rate < 0.7:
                    suggestions.append({
                        "area": task_type,
                        "current_performance": success_rate,
                        "target_performance": 0.9,
                        "priority": "high" if success_rate < 0.5 else "medium",
                        "recommendation": f"Practice {task_type} more frequently"
                    })
        
        # Identify skills that need development
        for skill_name, skill_data in self.skills.items():
            if skill_data["level"] < 5:
                suggestions.append({
                    "area": skill_name,
                    "current_level": skill_data["level"],
                    "target_level": 10,
                    "priority": "medium",
                    "recommendation": f"Increase proficiency in {skill_name}"
                })
        
        return suggestions
    
    def acquire_skill(self, skill_name: str, initial_level: int = 1):
        """Acquire a new skill"""
        
        self.skills[skill_name] = {
            "level": initial_level,
            "experience_count": 0,
            "acquired_at": datetime.now().isoformat(),
            "last_practiced": datetime.now().isoformat()
        }
        
        logger.info(f"Acquired new skill: {skill_name}")
        
        return {"success": True, "skill": skill_name, "level": initial_level}
    
    def practice_skill(self, skill_name: str, success: bool):
        """Practice a skill and update proficiency"""
        
        if skill_name not in self.skills:
            self.acquire_skill(skill_name)
        
        skill = self.skills[skill_name]
        skill["experience_count"] += 1
        skill["last_practiced"] = datetime.now().isoformat()
        
        # Update skill level based on success
        if success:
            skill["level"] += self.learning_rate
        else:
            skill["level"] = max(0, skill["level"] - self.learning_rate * 0.5)
        
        logger.info(f"Practiced {skill_name}: level now {skill['level']:.2f}")
    
    def _analyze_and_learn(self):
        """Analyze experiences and extract learnings"""
        
        logger.info("Analyzing experiences for learning")
        
        # Group experiences by task type
        task_outcomes = defaultdict(lambda: {"success": 0, "failure": 0})
        
        for exp in self.experiences[-50:]:  # Last 50 experiences
            task_type = exp["task_type"]
            if exp["success"]:
                task_outcomes[task_type]["success"] += 1
            else:
                task_outcomes[task_type]["failure"] += 1
        
        # Update strategies based on outcomes
        for task_type, outcomes in task_outcomes.items():
            total = outcomes["success"] + outcomes["failure"]
            success_rate = outcomes["success"] / total if total > 0 else 0
            
            if task_type not in self.strategies:
                self.strategies[task_type] = {
                    "approach": "default",
                    "success_rate": success_rate
                }
            else:
                # Update success rate with exponential moving average
                old_rate = self.strategies[task_type]["success_rate"]
                self.strategies[task_type]["success_rate"] = (
                    old_rate * 0.7 + success_rate * 0.3
                )
        
        logger.info(f"Learning complete. Strategies updated for {len(self.strategies)} task types")
    
    def _calculate_proficiency(self, level: float) -> str:
        """Calculate proficiency level from numeric level"""
        
        if level < 2:
            return "novice"
        elif level < 5:
            return "beginner"
        elif level < 8:
            return "intermediate"
        elif level < 12:
            return "advanced"
        else:
            return "expert"
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning progress"""
        
        return {
            "agent_id": self.agent_id,
            "total_experiences": len(self.experiences),
            "skills_acquired": len(self.skills),
            "strategies_developed": len(self.strategies),
            "average_performance": {
                task: statistics.mean(results)
                for task, results in self.performance_history.items()
                if results
            },
            "top_skills": sorted(
                self.skills.items(),
                key=lambda x: x[1]["level"],
                reverse=True
            )[:5]
        }


if __name__ == "__main__":
    engine = SelfLearningEngine("learning-agent-001")
    
    # Record some experiences
    engine.record_experience("code_review", "analyze", "found_issues", True, {"issues": 3})
    engine.record_experience("code_review", "analyze", "no_issues", True)
    engine.record_experience("testing", "run_tests", "all_passed", True, {"tests": 50})
    
    # Acquire and practice skills
    engine.acquire_skill("python", initial_level=3)
    engine.practice_skill("python", success=True)
    engine.practice_skill("python", success=True)
    
    # Get suggestions
    suggestions = engine.suggest_improvement()
    print("Suggestions:", json.dumps(suggestions, indent=2))
    
    # Get summary
    summary = engine.get_learning_summary()
    print("\nSummary:", json.dumps(summary, indent=2))
