"""
Agent Lifecycle Management

Manages the complete lifecycle of agents including creation, initialization,
execution, monitoring, and termination.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
import structlog

from src.core.agent import BaseAgent, AgentStatus, AgentConfig
import uuid

logger = structlog.get_logger(__name__)


class LifecyclePhase(str, Enum):
    """Lifecycle phases for agents and tasks."""
    CONCEPTION = "conception"
    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"
    APPROVAL = "approval"
    COMPLETION = "completion"
    ARCHIVED = "archived"


class LifecycleEvent(BaseModel):
    """Represents an event in the lifecycle."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phase: LifecyclePhase
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: Optional[str] = None
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentLifecycle:
    """
    Manages the complete lifecycle of an agent.
    
    Tracks the agent's journey from conception through termination,
    including all state transitions and key events.
    """
    
    def __init__(self, agent: BaseAgent):
        """Initialize lifecycle manager for an agent."""
        self.agent = agent
        self.current_phase = LifecyclePhase.CONCEPTION
        self.history: List[LifecycleEvent] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        self.logger = structlog.get_logger(__name__).bind(
            agent_id=agent.agent_id,
            agent_name=agent.name
        )
        
        # Record creation
        self._record_event(
            LifecyclePhase.CONCEPTION,
            "Agent lifecycle initialized"
        )
    
    def _record_event(
        self,
        phase: LifecyclePhase,
        description: str,
        actor: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a lifecycle event."""
        event = LifecycleEvent(
            phase=phase,
            actor=actor,
            description=description,
            metadata=metadata or {}
        )
        self.history.append(event)
        self.logger.info(
            "Lifecycle event",
            phase=phase.value,
            description=description
        )
    
    async def transition_to_planning(self) -> None:
        """Transition to planning phase."""
        if self.current_phase != LifecyclePhase.CONCEPTION:
            raise ValueError(f"Cannot transition to planning from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.PLANNING
        self._record_event(LifecyclePhase.PLANNING, "Entering planning phase")
    
    async def transition_to_preparation(self) -> None:
        """Transition to preparation phase."""
        if self.current_phase != LifecyclePhase.PLANNING:
            raise ValueError(f"Cannot transition to preparation from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.PREPARATION
        self._record_event(LifecyclePhase.PREPARATION, "Preparing agent for execution")
        
        # Initialize the agent
        await self.agent.initialize()
    
    async def transition_to_execution(self) -> None:
        """Transition to execution phase."""
        if self.current_phase != LifecyclePhase.PREPARATION:
            raise ValueError(f"Cannot transition to execution from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.EXECUTION
        self.started_at = datetime.utcnow()
        self._record_event(LifecyclePhase.EXECUTION, "Agent execution started")
        
        # Start the agent
        await self.agent.start()
    
    async def transition_to_review(self) -> None:
        """Transition to review phase."""
        if self.current_phase != LifecyclePhase.EXECUTION:
            raise ValueError(f"Cannot transition to review from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.REVIEW
        self._record_event(LifecyclePhase.REVIEW, "Entering review phase")
    
    async def transition_to_approval(self) -> None:
        """Transition to approval phase."""
        if self.current_phase != LifecyclePhase.REVIEW:
            raise ValueError(f"Cannot transition to approval from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.APPROVAL
        self._record_event(LifecyclePhase.APPROVAL, "Awaiting approval")
    
    async def transition_to_completion(self) -> None:
        """Transition to completion phase."""
        if self.current_phase not in [LifecyclePhase.APPROVAL, LifecyclePhase.EXECUTION]:
            raise ValueError(f"Cannot transition to completion from {self.current_phase}")
        
        self.current_phase = LifecyclePhase.COMPLETION
        self.completed_at = datetime.utcnow()
        self._record_event(LifecyclePhase.COMPLETION, "Agent lifecycle completed")
        
        # Stop the agent
        await self.agent.stop()
    
    def get_lifecycle_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's lifecycle."""
        duration = None
        if self.started_at and self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            duration = (datetime.utcnow() - self.started_at).total_seconds()
        
        return {
            "agent_id": self.agent.agent_id,
            "agent_name": self.agent.name,
            "current_phase": self.current_phase.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": duration,
            "event_count": len(self.history),
            "events": [
                {
                    "phase": event.phase.value,
                    "timestamp": event.timestamp.isoformat(),
                    "description": event.description
                }
                for event in self.history
            ]
        }
