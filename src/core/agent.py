"""
Base Agent Framework

Provides the foundational agent class and interfaces for all Q-BIT agents.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class AgentStatus(str, Enum):
    """Agent lifecycle status enumeration."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    TERMINATED = "terminated"


class AgentCapability(str, Enum):
    """Agent capability enumeration."""
    CODE_ANALYSIS = "code_analysis"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DEBUGGING = "debugging"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    OPTIMIZATION = "optimization"
    SECURITY_ANALYSIS = "security_analysis"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    LEARNING = "learning"


class AgentMetrics(BaseModel):
    """Agent performance and health metrics."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    uptime: float = 0.0
    last_activity: Optional[datetime] = None


class AgentConfig(BaseModel):
    """Agent configuration model."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    capabilities: Set[AgentCapability] = Field(default_factory=set)
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 3
    log_level: str = "INFO"
    custom_config: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """Task model for agent execution."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    priority: int = 5  # 1-10, 10 being highest
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    requester_id: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Task execution result model."""
    task_id: str
    agent_id: str
    status: str  # "success", "failure", "partial"
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base agent class providing core functionality for all Q-BIT agents.
    
    This class defines the fundamental interface and behavior that all agents
    must implement, including lifecycle management, task execution, and
    communication capabilities.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the base agent with configuration."""
        self.config = config
        self.agent_id = config.agent_id
        self.name = config.name
        self.status = AgentStatus.INITIALIZING
        self.capabilities = config.capabilities
        self.metrics = AgentMetrics()
        self.active_tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.shutdown_event = asyncio.Event()
        self.logger = structlog.get_logger(__name__).bind(
            agent_id=self.agent_id,
            agent_name=self.name
        )
        
        # Internal state
        self._start_time = datetime.utcnow()
        self._task_semaphore = asyncio.Semaphore(config.max_concurrent_tasks)
        self._health_check_interval = 30  # seconds
        
    async def initialize(self) -> None:
        """Initialize the agent and prepare for operation."""
        try:
            self.logger.info("Initializing agent")
            await self._setup()
            self.status = AgentStatus.IDLE
            self.logger.info("Agent initialized successfully")
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error("Agent initialization failed", error=str(e))
            raise
    
    async def start(self) -> None:
        """Start the agent's main execution loop."""
        if self.status != AgentStatus.IDLE:
            raise RuntimeError(f"Cannot start agent in status: {self.status}")
        
        self.logger.info("Starting agent")
        self.status = AgentStatus.ACTIVE
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._task_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error("Agent execution error", error=str(e))
            self.status = AgentStatus.ERROR
            raise
    
    async def stop(self) -> None:
        """Stop the agent gracefully."""
        self.logger.info("Stopping agent")
        self.status = AgentStatus.SHUTTING_DOWN
        self.shutdown_event.set()
        
        # Wait for active tasks to complete
        while self.active_tasks:
            await asyncio.sleep(0.1)
        
        await self._cleanup()
        self.status = AgentStatus.TERMINATED
        self.logger.info("Agent stopped")
    
    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution."""
        if self.status not in [AgentStatus.IDLE, AgentStatus.ACTIVE]:
            raise RuntimeError(f"Cannot accept tasks in status: {self.status}")
        
        self.logger.info("Task submitted", task_id=task.task_id, task_type=task.type)
        await self.task_queue.put(task)
        return task.task_id
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "metrics": self.metrics.model_dump(),
            "uptime": (datetime.utcnow() - self._start_time).total_seconds(),
        }
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
    
    async def _task_processor(self) -> None:
        """Main task processing loop."""
        while not self.shutdown_event.is_set():
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Process task with concurrency control
                async with self._task_semaphore:
                    await self._execute_task(task)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error("Task processor error", error=str(e))
    
    async def _execute_task(self, task: Task) -> None:
        """Execute a single task."""
        start_time = datetime.utcnow()
        self.active_tasks[task.task_id] = task
        
        try:
            self.logger.info("Executing task", task_id=task.task_id)
            self.status = AgentStatus.BUSY
            
            # Execute the task
            result = await self.execute_task(task)
            
            # Create success result
            task_result = TaskResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                status="success",
                result=result,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            self.metrics.tasks_completed += 1
            self.logger.info("Task completed successfully", task_id=task.task_id)
            
        except Exception as e:
            # Create failure result
            task_result = TaskResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                status="failure",
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
            
            self.metrics.tasks_failed += 1
            self.logger.error("Task failed", task_id=task.task_id, error=str(e))
            
        finally:
            # Cleanup
            self.active_tasks.pop(task.task_id, None)
            self.status = AgentStatus.ACTIVE if not self.active_tasks else AgentStatus.BUSY
            self.metrics.last_activity = datetime.utcnow()
            
            # Update average response time
            total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
            if total_tasks > 0:
                self.metrics.average_response_time = (
                    (self.metrics.average_response_time * (total_tasks - 1) + 
                     task_result.execution_time) / total_tasks
                )
    
    async def _health_monitor(self) -> None:
        """Monitor agent health and perform maintenance."""
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self._health_check_interval)
            except Exception as e:
                self.logger.error("Health monitor error", error=str(e))
    
    async def _metrics_collector(self) -> None:
        """Collect and update agent metrics."""
        while not self.shutdown_event.is_set():
            try:
                await self._update_metrics()
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                self.logger.error("Metrics collector error", error=str(e))
    
    async def _perform_health_check(self) -> None:
        """Perform health check operations."""
        # Update uptime
        self.metrics.uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        # Check for stuck tasks
        current_time = datetime.utcnow()
        for task_id, task in list(self.active_tasks.items()):
            if task.deadline and current_time > task.deadline:
                self.logger.warning("Task deadline exceeded", task_id=task_id)
                # Could implement task cancellation here
    
    async def _update_metrics(self) -> None:
        """Update performance metrics."""
        # This would typically collect system metrics
        # For now, we'll just update basic counters
        pass
    
    @abstractmethod
    async def _setup(self) -> None:
        """Agent-specific setup logic."""
        pass
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Agent-specific cleanup logic."""
        pass
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Any:
        """Execute a specific task. Must be implemented by subclasses."""
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name}, status={self.status})>"
