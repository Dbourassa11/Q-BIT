"""
Coordinator implementations for Q-BIT agent orchestration.

Provides multiple coordination strategies:
- CentralizedCoordinator: Single coordinator assigns all tasks
- HierarchicalClusters: Clustered coordinators with hierarchical distribution
- IndependentAgents: Agents self-assign from a shared pool
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class TaskStatus(Enum):
    """Status of a task in the system."""
    
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """A task to be executed by an agent.
    
    Attributes:
        task_id: Unique identifier for the task
        task_type: Type/category of the task
        priority: Task priority (higher = more urgent)
        requirements: Resource/capability requirements
        metadata: Additional task data
        status: Current task status
        assigned_to: ID of the agent assigned to this task
        created_at: Task creation timestamp
        completed_at: Task completion timestamp
    """
    
    task_id: str
    task_type: str
    priority: int = 0
    requirements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class CentralizedCoordinator:
    """Centralized coordinator that manages all task assignments.
    
    A single coordinator maintains a global view and assigns tasks to agents
    based on availability and capability matching.
    
    Args:
        max_queue_size: Maximum number of pending tasks
    """
    
    def __init__(self, max_queue_size: int = 10000) -> None:
        """Initialize the centralized coordinator."""
        self.max_queue_size = max_queue_size
        self._task_queue: List[Task] = []
        self._assigned_tasks: Dict[str, Task] = {}
        self._agent_capabilities: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def submit_task(self, task: Task) -> None:
        """Submit a task to the coordinator.
        
        Args:
            task: Task to be submitted
        
        Raises:
            ValueError: If queue is full
        """
        async with self._lock:
            if len(self._task_queue) >= self.max_queue_size:
                raise ValueError(
                    f"Task queue full (max: {self.max_queue_size})"
                )
            
            self._task_queue.append(task)
            # Sort by priority (highest first)
            self._task_queue.sort(key=lambda t: t.priority, reverse=True)
    
    async def register_agent(
        self,
        agent_id: str,
        capabilities: Dict[str, Any],
    ) -> None:
        """Register an agent with the coordinator.
        
        Args:
            agent_id: Unique agent identifier
            capabilities: Agent capabilities and resources
        """
        async with self._lock:
            self._agent_capabilities[agent_id] = capabilities
    
    async def assign_best(
        self,
        agent_id: str,
    ) -> Optional[Task]:
        """Assign the best matching task to an agent.
        
        Args:
            agent_id: ID of the agent requesting a task
        
        Returns:
            Task if available and agent is capable, None otherwise
        """
        async with self._lock:
            agent_caps = self._agent_capabilities.get(agent_id, {})
            
            # Find best matching task
            for i, task in enumerate(self._task_queue):
                if self._matches_requirements(agent_caps, task.requirements):
                    # Assign task
                    assigned_task = self._task_queue.pop(i)
                    assigned_task.status = TaskStatus.ASSIGNED
                    assigned_task.assigned_to = agent_id
                    self._assigned_tasks[assigned_task.task_id] = assigned_task
                    return assigned_task
            
            return None
    
    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
    ) -> None:
        """Mark a task as completed.
        
        Args:
            task_id: ID of the completed task
            success: Whether task completed successfully
        """
        async with self._lock:
            if task_id in self._assigned_tasks:
                task = self._assigned_tasks[task_id]
                task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
                task.completed_at = datetime.now(timezone.utc)
                del self._assigned_tasks[task_id]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics.
        
        Returns:
            Dictionary with queue sizes and status counts
        """
        async with self._lock:
            return {
                "pending_tasks": len(self._task_queue),
                "assigned_tasks": len(self._assigned_tasks),
                "registered_agents": len(self._agent_capabilities),
            }
    
    def _matches_requirements(
        self,
        capabilities: Dict[str, Any],
        requirements: Dict[str, Any],
    ) -> bool:
        """Check if agent capabilities match task requirements.
        
        Args:
            capabilities: Agent capabilities
            requirements: Task requirements
        
        Returns:
            True if agent can handle the task
        """
        # Simple matching: all required keys must exist and values must match or exceed
        for key, required_value in requirements.items():
            if key not in capabilities:
                return False
            
            cap_value = capabilities[key]
            # For numeric requirements, capability must be >= requirement
            if isinstance(required_value, (int, float)):
                if not isinstance(cap_value, (int, float)) or cap_value < required_value:
                    return False
            # For other types, exact match
            elif cap_value != required_value:
                return False
        
        return True


class HierarchicalClusters:
    """Hierarchical cluster coordinator for distributed task management.
    
    Organizes agents into clusters with local coordinators, enabling
    hierarchical task distribution and reduced coordination overhead.
    
    Args:
        num_clusters: Number of agent clusters
    """
    
    def __init__(self, num_clusters: int = 4) -> None:
        """Initialize hierarchical clusters."""
        self.num_clusters = num_clusters
        self._clusters: Dict[int, CentralizedCoordinator] = {
            i: CentralizedCoordinator() for i in range(num_clusters)
        }
        self._agent_to_cluster: Dict[str, int] = {}
        self._lock = asyncio.Lock()
    
    async def register_agent(
        self,
        agent_id: str,
        capabilities: Dict[str, Any],
        cluster_id: Optional[int] = None,
    ) -> int:
        """Register an agent to a cluster.
        
        Args:
            agent_id: Unique agent identifier
            capabilities: Agent capabilities
            cluster_id: Optional specific cluster assignment
        
        Returns:
            Assigned cluster ID
        """
        async with self._lock:
            if cluster_id is None:
                # Assign to least loaded cluster
                cluster_sizes = {
                    cid: (await coord.get_stats())["registered_agents"]
                    for cid, coord in self._clusters.items()
                }
                cluster_id = min(cluster_sizes.items(), key=lambda x: x[1])[0]
            
            self._agent_to_cluster[agent_id] = cluster_id
            await self._clusters[cluster_id].register_agent(agent_id, capabilities)
            return cluster_id
    
    async def distribute(
        self,
        tasks: List[Task],
    ) -> None:
        """Distribute tasks across clusters.
        
        Args:
            tasks: List of tasks to distribute
        """
        # Round-robin distribution by default
        for i, task in enumerate(tasks):
            cluster_id = i % self.num_clusters
            await self._clusters[cluster_id].submit_task(task)
    
    async def assign_best(
        self,
        agent_id: str,
    ) -> Optional[Task]:
        """Assign best task to agent from its cluster.
        
        Args:
            agent_id: ID of the requesting agent
        
        Returns:
            Task if available, None otherwise
        """
        cluster_id = self._agent_to_cluster.get(agent_id)
        if cluster_id is None:
            return None
        
        return await self._clusters[cluster_id].assign_best(agent_id)
    
    async def complete_task(
        self,
        task_id: str,
        agent_id: str,
        success: bool = True,
    ) -> None:
        """Mark a task as completed.
        
        Args:
            task_id: ID of the completed task
            agent_id: ID of the agent that completed it
            success: Whether task completed successfully
        """
        cluster_id = self._agent_to_cluster.get(agent_id)
        if cluster_id is not None:
            await self._clusters[cluster_id].complete_task(task_id, success)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get hierarchical coordinator statistics.
        
        Returns:
            Statistics for all clusters
        """
        cluster_stats = {}
        for cid, coordinator in self._clusters.items():
            cluster_stats[f"cluster_{cid}"] = await coordinator.get_stats()
        
        return {
            "num_clusters": self.num_clusters,
            "clusters": cluster_stats,
        }


class IndependentAgents:
    """Independent agents with shared task pool.
    
    Agents autonomously select and claim tasks from a shared pool,
    minimizing coordination overhead.
    """
    
    def __init__(self) -> None:
        """Initialize independent agents coordinator."""
        self._task_pool: List[Task] = []
        self._claimed_tasks: Dict[str, str] = {}  # task_id -> agent_id
        self._lock = asyncio.Lock()
    
    async def submit_task(self, task: Task) -> None:
        """Add a task to the shared pool.
        
        Args:
            task: Task to add to the pool
        """
        async with self._lock:
            self._task_pool.append(task)
            # Sort by priority
            self._task_pool.sort(key=lambda t: t.priority, reverse=True)
    
    async def assign_best(
        self,
        agent_id: str,
        capabilities: Dict[str, Any],
    ) -> Optional[Task]:
        """Agent claims best matching task from pool.
        
        Args:
            agent_id: ID of the requesting agent
            capabilities: Agent's capabilities
        
        Returns:
            Task if available and agent is capable, None otherwise
        """
        async with self._lock:
            for i, task in enumerate(self._task_pool):
                # Check if agent can handle this task
                capable = all(
                    key in capabilities and (
                        not isinstance(val, (int, float)) or capabilities[key] >= val
                    )
                    for key, val in task.requirements.items()
                )
                
                if capable:
                    claimed_task = self._task_pool.pop(i)
                    claimed_task.status = TaskStatus.ASSIGNED
                    claimed_task.assigned_to = agent_id
                    self._claimed_tasks[claimed_task.task_id] = agent_id
                    return claimed_task
            
            return None
    
    async def complete_task(
        self,
        task_id: str,
        success: bool = True,
    ) -> None:
        """Mark a task as completed.
        
        Args:
            task_id: ID of the completed task
            success: Whether task completed successfully
        """
        async with self._lock:
            self._claimed_tasks.pop(task_id, None)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get independent agents statistics.
        
        Returns:
            Pool and claim statistics
        """
        async with self._lock:
            return {
                "pool_size": len(self._task_pool),
                "claimed_tasks": len(self._claimed_tasks),
            }
