"""
Swarm Coordinator

Advanced swarm intelligence coordination system for managing multiple AI agents
working collaboratively on complex programming tasks.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field
import structlog

from src.core.agent import BaseAgent, Task, TaskResult, AgentCapability, AgentStatus

logger = structlog.get_logger(__name__)


class SwarmStrategy(str, Enum):
    """Swarm coordination strategies."""
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    DEMOCRATIC = "democratic"
    EXPERT_BASED = "expert_based"
    ADAPTIVE = "adaptive"


class TaskComplexity(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


class SwarmTask(BaseModel):
    """Extended task model for swarm coordination."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: Optional[str] = None
    type: str
    complexity: TaskComplexity = TaskComplexity.MODERATE
    required_capabilities: Set[AgentCapability] = Field(default_factory=set)
    priority: int = 5
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # seconds
    dependencies: List[str] = Field(default_factory=list)
    subtasks: List[str] = Field(default_factory=list)
    collaboration_required: bool = False
    min_agents: int = 1
    max_agents: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentAssignment(BaseModel):
    """Agent assignment for a task."""
    agent_id: str
    task_id: str
    role: str  # "primary", "secondary", "reviewer", "coordinator"
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = 0.0
    estimated_completion: Optional[datetime] = None


class SwarmDecision(BaseModel):
    """Collective decision made by the swarm."""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    decision_type: str  # "assignment", "approach", "quality", "completion"
    options: List[Dict[str, Any]] = Field(default_factory=list)
    votes: Dict[str, Any] = Field(default_factory=dict)  # agent_id -> vote
    consensus_reached: bool = False
    final_decision: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SwarmCoordinator:
    """
    Advanced swarm intelligence coordinator for managing multiple AI agents.
    
    Implements sophisticated algorithms for task distribution, agent coordination,
    consensus building, and collective decision making.
    """
    
    def __init__(self, strategy: SwarmStrategy = SwarmStrategy.ADAPTIVE):
        """Initialize the swarm coordinator."""
        self.coordinator_id = str(uuid.uuid4())
        self.strategy = strategy
        self.agents: Dict[str, BaseAgent] = {}
        self.active_tasks: Dict[str, SwarmTask] = {}
        self.task_assignments: Dict[str, List[AgentAssignment]] = {}
        self.pending_decisions: Dict[str, SwarmDecision] = {}
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.coordination_lock = asyncio.Lock()
        
        self.logger = structlog.get_logger(__name__).bind(
            coordinator_id=self.coordinator_id
        )
        
        # Configuration
        self.max_task_retries = 3
        self.consensus_threshold = 0.7
        self.task_timeout = 3600  # 1 hour default
        self.health_check_interval = 30
        
        # Metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0.0,
            "agent_utilization": 0.0,
            "consensus_success_rate": 0.0,
        }
        
        # Internal state
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    async def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the swarm."""
        async with self.coordination_lock:
            self.agents[agent.agent_id] = agent
            self.logger.info(
                "Agent registered",
                agent_id=agent.agent_id,
                agent_name=agent.name,
                capabilities=[cap.value for cap in agent.capabilities]
            )
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the swarm."""
        async with self.coordination_lock:
            if agent_id in self.agents:
                agent = self.agents.pop(agent_id)
                self.logger.info("Agent unregistered", agent_id=agent_id)
                
                # Reassign tasks if necessary
                await self._handle_agent_removal(agent_id)
    
    async def submit_task(self, task: SwarmTask) -> str:
        """Submit a task to the swarm for execution."""
        self.logger.info(
            "Task submitted to swarm",
            task_id=task.task_id,
            task_type=task.type,
            complexity=task.complexity.value,
            required_capabilities=[cap.value for cap in task.required_capabilities]
        )
        
        # Analyze task and determine execution strategy
        await self._analyze_task(task)
        
        # Add to active tasks
        self.active_tasks[task.task_id] = task
        
        # Queue for assignment
        priority = -task.priority  # Negative for max-heap behavior
        await self.task_queue.put((priority, task.created_at, task))
        
        return task.task_id
    
    async def start(self) -> None:
        """Start the swarm coordinator."""
        if self._running:
            return
        
        self.logger.info("Starting swarm coordinator")
        self._running = True
        
        # Start coordination tasks
        tasks = [
            asyncio.create_task(self._task_coordinator()),
            asyncio.create_task(self._decision_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error("Swarm coordinator error", error=str(e))
            raise
    
    async def stop(self) -> None:
        """Stop the swarm coordinator."""
        self.logger.info("Stopping swarm coordinator")
        self._running = False
        self._shutdown_event.set()
        
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(0.1)
    
    async def get_swarm_status(self) -> Dict[str, Any]:
        """Get comprehensive swarm status."""
        agent_statuses = {}
        for agent_id, agent in self.agents.items():
            agent_statuses[agent_id] = await agent.get_status()
        
        return {
            "coordinator_id": self.coordinator_id,
            "strategy": self.strategy.value,
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "pending_decisions": len(self.pending_decisions),
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics,
            "agents": agent_statuses,
        }
    
    async def _task_coordinator(self) -> None:
        """Main task coordination loop."""
        while self._running and not self._shutdown_event.is_set():
            try:
                # Get next task from queue
                try:
                    priority, created_at, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Coordinate task execution
                await self._coordinate_task(task)
                
            except Exception as e:
                self.logger.error("Task coordination error", error=str(e))
    
    async def _coordinate_task(self, task: SwarmTask) -> None:
        """Coordinate the execution of a single task."""
        self.logger.info("Coordinating task", task_id=task.task_id)
        
        try:
            # Find suitable agents
            suitable_agents = await self._find_suitable_agents(task)
            
            if not suitable_agents:
                self.logger.warning("No suitable agents found", task_id=task.task_id)
                await self._handle_task_failure(task, "No suitable agents")
                return
            
            # Determine assignment strategy
            assignments = await self._determine_assignments(task, suitable_agents)
            
            if not assignments:
                self.logger.warning("Could not create assignments", task_id=task.task_id)
                await self._handle_task_failure(task, "Assignment failed")
                return
            
            # Execute assignments
            self.task_assignments[task.task_id] = assignments
            await self._execute_assignments(task, assignments)
            
        except Exception as e:
            self.logger.error("Task coordination failed", task_id=task.task_id, error=str(e))
            await self._handle_task_failure(task, str(e))
    
    async def _find_suitable_agents(self, task: SwarmTask) -> List[BaseAgent]:
        """Find agents suitable for executing a task."""
        suitable_agents = []
        
        for agent in self.agents.values():
            # Check agent status
            if agent.status not in [AgentStatus.IDLE, AgentStatus.ACTIVE]:
                continue
            
            # Check capabilities
            if task.required_capabilities:
                if not task.required_capabilities.issubset(agent.capabilities):
                    continue
            
            # Check availability
            agent_status = await agent.get_status()
            if agent_status["active_tasks"] >= agent.config.max_concurrent_tasks:
                continue
            
            suitable_agents.append(agent)
        
        # Sort by suitability score
        suitable_agents.sort(key=lambda a: self._calculate_suitability_score(a, task), reverse=True)
        
        return suitable_agents
    
    def _calculate_suitability_score(self, agent: BaseAgent, task: SwarmTask) -> float:
        """Calculate how suitable an agent is for a task."""
        score = 0.0
        
        # Capability match score
        if task.required_capabilities:
            matching_caps = task.required_capabilities.intersection(agent.capabilities)
            score += len(matching_caps) / len(task.required_capabilities) * 50
        
        # Performance score
        if agent.metrics.tasks_completed > 0:
            success_rate = agent.metrics.tasks_completed / (
                agent.metrics.tasks_completed + agent.metrics.tasks_failed
            )
            score += success_rate * 30
        
        # Availability score
        current_load = len(agent.active_tasks) / agent.config.max_concurrent_tasks
        score += (1 - current_load) * 20
        
        return score
    
    async def _determine_assignments(
        self, 
        task: SwarmTask, 
        suitable_agents: List[BaseAgent]
    ) -> List[AgentAssignment]:
        """Determine how to assign agents to a task."""
        assignments = []
        
        if task.collaboration_required:
            # Multi-agent collaboration
            num_agents = min(len(suitable_agents), task.max_agents)
            num_agents = max(num_agents, task.min_agents)
            
            for i, agent in enumerate(suitable_agents[:num_agents]):
                role = "primary" if i == 0 else "secondary"
                assignment = AgentAssignment(
                    agent_id=agent.agent_id,
                    task_id=task.task_id,
                    role=role,
                    confidence_score=self._calculate_suitability_score(agent, task)
                )
                assignments.append(assignment)
        else:
            # Single agent assignment
            if suitable_agents:
                best_agent = suitable_agents[0]
                assignment = AgentAssignment(
                    agent_id=best_agent.agent_id,
                    task_id=task.task_id,
                    role="primary",
                    confidence_score=self._calculate_suitability_score(best_agent, task)
                )
                assignments.append(assignment)
        
        return assignments
    
    async def _execute_assignments(
        self, 
        task: SwarmTask, 
        assignments: List[AgentAssignment]
    ) -> None:
        """Execute task assignments."""
        execution_tasks = []
        
        for assignment in assignments:
            agent = self.agents[assignment.agent_id]
            
            # Create agent-specific task
            agent_task = Task(
                task_id=f"{task.task_id}_{assignment.agent_id}",
                type=task.type,
                priority=task.priority,
                payload={
                    **task.payload,
                    "swarm_task_id": task.task_id,
                    "role": assignment.role,
                    "collaboration_required": task.collaboration_required,
                }
            )
            
            # Submit to agent
            execution_task = asyncio.create_task(
                self._execute_agent_task(agent, agent_task, assignment)
            )
            execution_tasks.append(execution_task)
        
        # Wait for completion
        try:
            results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            await self._process_task_results(task, assignments, results)
        except Exception as e:
            self.logger.error("Task execution failed", task_id=task.task_id, error=str(e))
            await self._handle_task_failure(task, str(e))
    
    async def _execute_agent_task(
        self, 
        agent: BaseAgent, 
        task: Task, 
        assignment: AgentAssignment
    ) -> TaskResult:
        """Execute a task on a specific agent."""
        try:
            await agent.submit_task(task)
            # In a real implementation, we'd wait for the result
            # For now, we'll simulate a successful result
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                status="success",
                result={"message": "Task completed successfully"},
                execution_time=10.0
            )
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                status="failure",
                error=str(e),
                execution_time=0.0
            )
    
    async def _process_task_results(
        self, 
        task: SwarmTask, 
        assignments: List[AgentAssignment], 
        results: List[Union[TaskResult, Exception]]
    ) -> None:
        """Process the results of task execution."""
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append(result)
            elif isinstance(result, TaskResult) and result.status == "success":
                successful_results.append(result)
            else:
                failed_results.append(result)
        
        if successful_results:
            self.logger.info(
                "Task completed successfully",
                task_id=task.task_id,
                successful_agents=len(successful_results),
                failed_agents=len(failed_results)
            )
            
            # If collaboration was required, we might need consensus
            if task.collaboration_required and len(successful_results) > 1:
                await self._build_consensus(task, successful_results)
            
            await self._handle_task_success(task, successful_results)
        else:
            self.logger.error("All agents failed to complete task", task_id=task.task_id)
            await self._handle_task_failure(task, "All agents failed")
    
    async def _build_consensus(self, task: SwarmTask, results: List[TaskResult]) -> None:
        """Build consensus among multiple agent results."""
        decision = SwarmDecision(
            task_id=task.task_id,
            decision_type="completion",
            options=[{"result": result.result, "agent_id": result.agent_id} for result in results]
        )
        
        # Simple consensus: choose the result with highest confidence
        # In a real implementation, this would be more sophisticated
        best_result = max(results, key=lambda r: r.execution_time)  # Placeholder logic
        decision.final_decision = {"result": best_result.result}
        decision.consensus_reached = True
        decision.confidence = 0.8  # Placeholder
        
        self.pending_decisions[decision.decision_id] = decision
    
    async def _handle_task_success(self, task: SwarmTask, results: List[TaskResult]) -> None:
        """Handle successful task completion."""
        self.active_tasks.pop(task.task_id, None)
        self.task_assignments.pop(task.task_id, None)
        self.metrics["tasks_completed"] += 1
        
        self.logger.info("Task completed successfully", task_id=task.task_id)
    
    async def _handle_task_failure(self, task: SwarmTask, error: str) -> None:
        """Handle task failure."""
        self.active_tasks.pop(task.task_id, None)
        self.task_assignments.pop(task.task_id, None)
        self.metrics["tasks_failed"] += 1
        
        self.logger.error("Task failed", task_id=task.task_id, error=error)
    
    async def _analyze_task(self, task: SwarmTask) -> None:
        """Analyze a task to determine optimal execution strategy."""
        # Determine complexity based on requirements
        if len(task.required_capabilities) > 3:
            task.complexity = TaskComplexity.COMPLEX
        elif len(task.required_capabilities) > 1:
            task.complexity = TaskComplexity.MODERATE
        else:
            task.complexity = TaskComplexity.SIMPLE
        
        # Determine if collaboration is beneficial
        if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            task.collaboration_required = True
            task.max_agents = min(3, len(self.agents))
    
    async def _handle_agent_removal(self, agent_id: str) -> None:
        """Handle the removal of an agent from the swarm."""
        # Find tasks assigned to this agent
        affected_tasks = []
        for task_id, assignments in self.task_assignments.items():
            for assignment in assignments:
                if assignment.agent_id == agent_id:
                    affected_tasks.append(task_id)
                    break
        
        # Reassign affected tasks
        for task_id in affected_tasks:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                self.logger.info("Reassigning task due to agent removal", task_id=task_id)
                await self.task_queue.put((-task.priority, task.created_at, task))
    
    async def _decision_processor(self) -> None:
        """Process pending swarm decisions."""
        while self._running and not self._shutdown_event.is_set():
            try:
                # Process pending decisions
                for decision_id, decision in list(self.pending_decisions.items()):
                    if decision.consensus_reached:
                        self.logger.info("Decision finalized", decision_id=decision_id)
                        self.pending_decisions.pop(decision_id)
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error("Decision processor error", error=str(e))
    
    async def _health_monitor(self) -> None:
        """Monitor swarm health."""
        while self._running and not self._shutdown_event.is_set():
            try:
                # Check agent health
                unhealthy_agents = []
                for agent_id, agent in self.agents.items():
                    if agent.status == AgentStatus.ERROR:
                        unhealthy_agents.append(agent_id)
                
                if unhealthy_agents:
                    self.logger.warning("Unhealthy agents detected", agents=unhealthy_agents)
                
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error("Health monitor error", error=str(e))
    
    async def _metrics_collector(self) -> None:
        """Collect swarm metrics."""
        while self._running and not self._shutdown_event.is_set():
            try:
                # Calculate agent utilization
                if self.agents:
                    total_capacity = sum(agent.config.max_concurrent_tasks for agent in self.agents.values())
                    total_active = sum(len(agent.active_tasks) for agent in self.agents.values())
                    self.metrics["agent_utilization"] = total_active / total_capacity if total_capacity > 0 else 0.0
                
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                self.logger.error("Metrics collector error", error=str(e))
