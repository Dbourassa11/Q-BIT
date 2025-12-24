"""
Simulated worker pool and stress harness for CI-friendly benchmarks.

Provides deterministic, fast simulation of large agent populations
without requiring network services.
"""

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from python.qbit.coordinators import Task, TaskStatus
from python.qbit.stigmergy import StigmergicEnvironment, TraceType


@dataclass
class SimulatedAgent:
    """A simulated agent for stress testing.
    
    Attributes:
        agent_id: Unique identifier
        position: Current position in environment
        capabilities: Agent capabilities
        tasks_completed: Number of completed tasks
        tasks_failed: Number of failed tasks
    """
    
    agent_id: str
    position: tuple[int, int] = (0, 0)
    capabilities: Dict[str, Any] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    
    def __post_init__(self) -> None:
        """Initialize capabilities if not provided."""
        if self.capabilities is None:
            self.capabilities = {
                "compute": random.uniform(0.5, 1.0),
                "memory": random.uniform(0.5, 1.0),
            }


class SimulatedWorkerPool:
    """Simulated worker pool for stress testing.
    
    Simulates a pool of agents performing tasks without actual computation,
    allowing fast, deterministic benchmarks.
    
    Args:
        num_agents: Number of agents to simulate
        grid_size: Size of the environment grid
        enable_stigmergy: Whether to use stigmergic coordination
        seed: Random seed for deterministic behavior
    """
    
    def __init__(
        self,
        num_agents: int = 100,
        grid_size: int = 100,
        enable_stigmergy: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        """Initialize the simulated worker pool."""
        self.num_agents = num_agents
        self.grid_size = grid_size
        self.enable_stigmergy = enable_stigmergy
        
        if seed is not None:
            random.seed(seed)
        
        # Create simulated agents
        self.agents = [
            SimulatedAgent(
                agent_id=f"agent_{i}",
                position=(
                    random.randint(0, grid_size - 1),
                    random.randint(0, grid_size - 1),
                ),
            )
            for i in range(num_agents)
        ]
        
        # Stigmergic environment (optional)
        self.environment: Optional[StigmergicEnvironment] = None
        if enable_stigmergy:
            self.environment = StigmergicEnvironment(
                grid_size=grid_size,
                decay_rate=0.01,
                enable_background_decay=False,
            )
        
        # Task pool
        self.task_pool: List[Task] = []
        self.completed_tasks: List[Task] = []
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize the worker pool."""
        if self.environment:
            await self.environment.initialize()
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.environment:
            await self.environment.cleanup()
    
    async def generate_tasks(
        self,
        num_tasks: int,
        task_types: Optional[List[str]] = None,
    ) -> None:
        """Generate simulated tasks.
        
        Args:
            num_tasks: Number of tasks to generate
            task_types: Optional list of task types to use
        """
        if task_types is None:
            task_types = ["compute", "memory", "io", "network"]
        
        async with self._lock:
            for i in range(num_tasks):
                task = Task(
                    task_id=f"task_{len(self.task_pool) + i}",
                    task_type=random.choice(task_types),
                    priority=random.randint(0, 10),
                    requirements={
                        "compute": random.uniform(0.3, 0.8),
                        "memory": random.uniform(0.3, 0.8),
                    },
                )
                self.task_pool.append(task)
    
    async def simulate_agent_step(
        self,
        agent: SimulatedAgent,
        max_move_distance: int = 5,
    ) -> None:
        """Simulate one step of agent behavior.
        
        Args:
            agent: Agent to simulate
            max_move_distance: Maximum distance agent can move
        """
        # Move agent randomly
        dx = random.randint(-max_move_distance, max_move_distance)
        dy = random.randint(-max_move_distance, max_move_distance)
        new_x = max(0, min(self.grid_size - 1, agent.position[0] + dx))
        new_y = max(0, min(self.grid_size - 1, agent.position[1] + dy))
        agent.position = (new_x, new_y)
        
        # Deposit trace if using stigmergy
        if self.environment:
            await self.environment.deposit_trace(
                trace_type=TraceType.AGENT_PATH,
                position=agent.position,
                intensity=0.5,
                depositor_id=agent.agent_id,
            )
            
            # Sense nearby traces
            traces = await self.environment.sense_traces(
                position=agent.position,
                radius=3,
            )
            
            # Adjust behavior based on trace density
            if len(traces) > 5:
                # High density, move away
                agent.position = (
                    max(0, min(self.grid_size - 1, agent.position[0] + random.randint(-10, 10))),
                    max(0, min(self.grid_size - 1, agent.position[1] + random.randint(-10, 10))),
                )
        
        # Try to claim a task
        async with self._lock:
            if self.task_pool:
                # Find a task the agent can handle
                for i, task in enumerate(self.task_pool):
                    can_handle = all(
                        agent.capabilities.get(req, 0) >= val
                        for req, val in task.requirements.items()
                    )
                    
                    if can_handle:
                        # Claim task
                        claimed_task = self.task_pool.pop(i)
                        claimed_task.status = TaskStatus.IN_PROGRESS
                        claimed_task.assigned_to = agent.agent_id
                        
                        # Simulate task execution (deterministic)
                        success = random.random() > 0.05  # 95% success rate
                        
                        if success:
                            claimed_task.status = TaskStatus.COMPLETED
                            claimed_task.completed_at = datetime.utcnow()
                            agent.tasks_completed += 1
                        else:
                            claimed_task.status = TaskStatus.FAILED
                            agent.tasks_failed += 1
                        
                        self.completed_tasks.append(claimed_task)
                        
                        # Deposit completion trace
                        if self.environment:
                            await self.environment.deposit_trace(
                                trace_type=TraceType.TASK_COMPLETE,
                                position=agent.position,
                                intensity=0.8,
                                depositor_id=agent.agent_id,
                                metadata={"task_id": claimed_task.task_id},
                            )
                        
                        break
    
    async def run_simulation(
        self,
        num_steps: int = 10,
        parallel: bool = True,
    ) -> Dict[str, Any]:
        """Run the simulation for a number of steps.
        
        Args:
            num_steps: Number of simulation steps
            parallel: Whether to run agents in parallel
        
        Returns:
            Simulation statistics
        """
        start_time = datetime.utcnow()
        
        for step in range(num_steps):
            if parallel:
                # Run all agents in parallel
                await asyncio.gather(
                    *[self.simulate_agent_step(agent) for agent in self.agents]
                )
            else:
                # Run agents sequentially
                for agent in self.agents:
                    await self.simulate_agent_step(agent)
            
            # Apply decay if using stigmergy
            if self.environment:
                await self.environment.decay()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Gather statistics
        total_completed = sum(agent.tasks_completed for agent in self.agents)
        total_failed = sum(agent.tasks_failed for agent in self.agents)
        
        return {
            "num_agents": self.num_agents,
            "num_steps": num_steps,
            "duration_seconds": duration,
            "tasks_completed": total_completed,
            "tasks_failed": total_failed,
            "tasks_remaining": len(self.task_pool),
            "throughput_tasks_per_second": total_completed / duration if duration > 0 else 0,
            "success_rate": total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0,
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get current simulation statistics.
        
        Returns:
            Current statistics
        """
        async with self._lock:
            return {
                "num_agents": self.num_agents,
                "tasks_in_pool": len(self.task_pool),
                "tasks_completed": len(self.completed_tasks),
                "agent_stats": [
                    {
                        "agent_id": agent.agent_id,
                        "position": agent.position,
                        "tasks_completed": agent.tasks_completed,
                        "tasks_failed": agent.tasks_failed,
                    }
                    for agent in self.agents
                ],
            }
