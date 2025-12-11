"""
State Management System

Provides centralized state management for agents and the swarm system.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field
import structlog
import uuid

logger = structlog.get_logger(__name__)


class StateType(str, Enum):
    """Types of state that can be managed."""
    AGENT = "agent"
    TASK = "task"
    SWARM = "swarm"
    COLLABORATION = "collaboration"
    SESSION = "session"


class StateChange(BaseModel):
    """Represents a change in state."""
    change_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state_type: StateType
    entity_id: str
    field: str
    old_value: Any = None
    new_value: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    changed_by: Optional[str] = None
    reason: Optional[str] = None


class StateSnapshot(BaseModel):
    """A snapshot of state at a point in time."""
    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state_type: StateType
    entity_id: str
    state_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateManager:
    """
    Centralized state management system.
    
    Manages state for all entities in the Q-BIT system including agents,
    tasks, swarms, and collaborations. Provides state tracking, history,
    and rollback capabilities.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self.states: Dict[str, Dict[str, Any]] = {}
        self.history: List[StateChange] = []
        self.snapshots: Dict[str, List[StateSnapshot]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        
        self.logger = structlog.get_logger(__name__)
        
        # Configuration
        self.max_history_size = 10000
        self.max_snapshots_per_entity = 100
    
    async def get_state(self, state_type: StateType, entity_id: str) -> Dict[str, Any]:
        """Get the current state of an entity."""
        key = f"{state_type.value}:{entity_id}"
        
        if key not in self.states:
            self.logger.warning(
                "State not found",
                state_type=state_type.value,
                entity_id=entity_id
            )
            return {}
        
        return self.states[key].copy()
    
    async def set_state(
        self,
        state_type: StateType,
        entity_id: str,
        state_data: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Set the complete state of an entity."""
        key = f"{state_type.value}:{entity_id}"
        
        # Get lock for this entity
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            old_state = self.states.get(key, {})
            
            # Record changes for each field
            for field, new_value in state_data.items():
                old_value = old_state.get(field)
                if old_value != new_value:
                    change = StateChange(
                        state_type=state_type,
                        entity_id=entity_id,
                        field=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=changed_by,
                        reason=reason
                    )
                    self.history.append(change)
            
            # Update state
            self.states[key] = state_data
            
            self.logger.info(
                "State updated",
                state_type=state_type.value,
                entity_id=entity_id,
                changed_by=changed_by
            )
            
            # Trim history if needed
            if len(self.history) > self.max_history_size:
                self.history = self.history[-self.max_history_size:]
    
    async def update_state(
        self,
        state_type: StateType,
        entity_id: str,
        updates: Dict[str, Any],
        changed_by: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Update specific fields in an entity's state."""
        key = f"{state_type.value}:{entity_id}"
        
        # Get lock for this entity
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            current_state = self.states.get(key, {})
            
            # Record changes
            for field, new_value in updates.items():
                old_value = current_state.get(field)
                if old_value != new_value:
                    change = StateChange(
                        state_type=state_type,
                        entity_id=entity_id,
                        field=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=changed_by,
                        reason=reason
                    )
                    self.history.append(change)
            
            # Update state
            current_state.update(updates)
            self.states[key] = current_state
            
            self.logger.info(
                "State updated",
                state_type=state_type.value,
                entity_id=entity_id,
                fields=list(updates.keys()),
                changed_by=changed_by
            )
            
            # Trim history if needed
            if len(self.history) > self.max_history_size:
                self.history = self.history[-self.max_history_size:]
    
    async def create_snapshot(
        self,
        state_type: StateType,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a snapshot of an entity's current state."""
        key = f"{state_type.value}:{entity_id}"
        
        if key not in self.states:
            raise ValueError(f"Cannot snapshot non-existent state: {key}")
        
        snapshot = StateSnapshot(
            state_type=state_type,
            entity_id=entity_id,
            state_data=self.states[key].copy(),
            metadata=metadata or {}
        )
        
        # Store snapshot
        if key not in self.snapshots:
            self.snapshots[key] = []
        
        self.snapshots[key].append(snapshot)
        
        # Trim snapshots if needed
        if len(self.snapshots[key]) > self.max_snapshots_per_entity:
            self.snapshots[key] = self.snapshots[key][-self.max_snapshots_per_entity:]
        
        self.logger.info(
            "Snapshot created",
            state_type=state_type.value,
            entity_id=entity_id,
            snapshot_id=snapshot.snapshot_id
        )
        
        return snapshot.snapshot_id
    
    async def restore_snapshot(
        self,
        snapshot_id: str,
        changed_by: Optional[str] = None
    ) -> None:
        """Restore state from a snapshot."""
        # Find the snapshot
        found_snapshot = None
        for snapshots in self.snapshots.values():
            for snapshot in snapshots:
                if snapshot.snapshot_id == snapshot_id:
                    found_snapshot = snapshot
                    break
            if found_snapshot:
                break
        
        if not found_snapshot:
            raise ValueError(f"Snapshot not found: {snapshot_id}")
        
        # Restore the state
        await self.set_state(
            found_snapshot.state_type,
            found_snapshot.entity_id,
            found_snapshot.state_data,
            changed_by=changed_by,
            reason=f"Restored from snapshot {snapshot_id}"
        )
        
        self.logger.info(
            "State restored from snapshot",
            snapshot_id=snapshot_id,
            state_type=found_snapshot.state_type.value,
            entity_id=found_snapshot.entity_id
        )
    
    async def get_history(
        self,
        state_type: Optional[StateType] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[StateChange]:
        """Get state change history."""
        filtered = self.history
        
        if state_type:
            filtered = [c for c in filtered if c.state_type == state_type]
        
        if entity_id:
            filtered = [c for c in filtered if c.entity_id == entity_id]
        
        return filtered[-limit:]
    
    async def clear_state(self, state_type: StateType, entity_id: str) -> None:
        """Clear the state of an entity."""
        key = f"{state_type.value}:{entity_id}"
        
        if key in self.states:
            del self.states[key]
            self.logger.info(
                "State cleared",
                state_type=state_type.value,
                entity_id=entity_id
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the state manager."""
        return {
            "total_states": len(self.states),
            "total_history_entries": len(self.history),
            "total_snapshots": sum(len(snapshots) for snapshots in self.snapshots.values()),
            "states_by_type": {
                state_type.value: len([k for k in self.states.keys() if k.startswith(state_type.value)])
                for state_type in StateType
            }
        }
