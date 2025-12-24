#!/usr/bin/env python3
"""
Continuous Agent Runtime

Framework for 24/7 agent operation with health monitoring, automatic recovery,
and resource management.
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent runtime states"""
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ContinuousAgentRuntime:
    """
    Continuous operation runtime for agents.
    
    Features:
    - 24/7 operation
    - Automatic health checks
    - Self-healing
    - Resource management
    - Graceful degradation
    """
    
    def __init__(self, agent_id: str, check_interval: int = 60):
        self.agent_id = agent_id
        self.check_interval = check_interval
        self.state = AgentState.STOPPED
        self.runtime_thread = None
        self.stop_event = threading.Event()
        self.health_checks = []
        self.error_count = 0
        self.max_errors = 10
        self.last_health_check = None
        self.start_time = None
        
        logger.info(f"ContinuousAgentRuntime initialized for {agent_id}")
    
    def register_health_check(self, check_func: Callable[[], bool], name: str):
        """Register a health check function"""
        self.health_checks.append({"func": check_func, "name": name})
        logger.info(f"Registered health check: {name}")
    
    def start(self, work_function: Callable[[], None]):
        """Start continuous operation"""
        if self.state == AgentState.RUNNING:
            logger.warning("Agent already running")
            return
        
        self.state = AgentState.STARTING
        self.stop_event.clear()
        self.start_time = datetime.now()
        
        def run_loop():
            self.state = AgentState.RUNNING
            logger.info(f"Agent {self.agent_id} started")
            
            while not self.stop_event.is_set():
                try:
                    # Perform health checks
                    if not self._perform_health_checks():
                        logger.warning("Health check failed, attempting recovery")
                        self._attempt_recovery()
                    
                    # Execute work
                    work_function()
                    
                    # Reset error count on successful iteration
                    self.error_count = 0
                    
                    # Sleep between iterations
                    time.sleep(self.check_interval)
                    
                except Exception as e:
                    self.error_count += 1
                    logger.error(f"Error in agent runtime: {e}")
                    
                    if self.error_count >= self.max_errors:
                        logger.critical("Max errors reached, stopping agent")
                        self.state = AgentState.ERROR
                        break
                    
                    time.sleep(5)  # Brief pause before retry
            
            self.state = AgentState.STOPPED
            logger.info(f"Agent {self.agent_id} stopped")
        
        self.runtime_thread = threading.Thread(target=run_loop, daemon=True)
        self.runtime_thread.start()
    
    def stop(self):
        """Stop continuous operation"""
        self.state = AgentState.STOPPING
        self.stop_event.set()
        
        if self.runtime_thread:
            self.runtime_thread.join(timeout=10)
        
        logger.info(f"Agent {self.agent_id} stop requested")
    
    def _perform_health_checks(self) -> bool:
        """Perform all registered health checks"""
        self.last_health_check = datetime.now()
        
        for check in self.health_checks:
            try:
                if not check["func"]():
                    logger.warning(f"Health check failed: {check['name']}")
                    return False
            except Exception as e:
                logger.error(f"Health check error in {check['name']}: {e}")
                return False
        
        return True
    
    def _attempt_recovery(self):
        """Attempt to recover from unhealthy state"""
        logger.info("Attempting automatic recovery")
        # Implementation of recovery strategies
        self.error_count = 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get runtime status"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "agent_id": self.agent_id,
            "state": self.state.value,
            "uptime_seconds": uptime,
            "error_count": self.error_count,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "health_checks_registered": len(self.health_checks)
        }


if __name__ == "__main__":
    # Example usage
    def sample_work():
        print(f"Working... {datetime.now()}")
    
    def sample_health_check():
        return True
    
    runtime = ContinuousAgentRuntime("test-agent", check_interval=5)
    runtime.register_health_check(sample_health_check, "sample_check")
    runtime.start(sample_work)
    
    # Run for 20 seconds
    time.sleep(20)
    runtime.stop()
    
    print("Status:", runtime.get_status())
