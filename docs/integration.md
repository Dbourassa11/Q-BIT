# Integration Guide

## Overview

This guide provides step-by-step instructions for integrating the Hybrid Topology Router and Stigmergic Coordination Layer into your existing Q-BIT deployment.

## Prerequisites

- Python 3.10 or higher
- Existing Q-BIT installation
- (Optional) Redis server for multi-node deployments

## Installation

### Basic Installation

```bash
# Install core dependencies
pip install -r requirements.txt
```

### Optional Redis Backend

```bash
# Install Redis support
pip install redis

# Or install with extras
pip install -e ".[redis]"
```

## Quick Start

### 1. Basic Integration

```python
from python.qbit.topology import TopologyRouter, Config
from python.qbit.coordinators import Task
from python.qbit.stigmergy import StigmergicEnvironment

# Initialize components
config = Config()
router = TopologyRouter(config=config)
environment = StigmergicEnvironment(grid_size=1000)
await environment.initialize()

# Create tasks
tasks = [
    Task(task_id=f"task_{i}", task_type="compute", priority=i)
    for i in range(100)
]

# Route to appropriate coordinator
coordinator_type = router.route(tasks)
coordinator = router.get_coordinator(coordinator_type)

# Submit tasks to coordinator
for task in tasks:
    if coordinator_type == "centralized":
        await coordinator.submit_task(task)
    elif coordinator_type == "hierarchical":
        await coordinator.distribute([task])
    else:  # independent
        await coordinator.submit_task(task)
```

### 2. Agent Registration

```python
# Register agents with coordinator
async def register_agent(coordinator, coordinator_type, agent_id, capabilities):
    if coordinator_type in ["centralized", "hierarchical"]:
        await coordinator.register_agent(agent_id, capabilities)
```

### 3. Task Assignment

```python
# Agent requests task
async def get_next_task(coordinator, coordinator_type, agent_id, capabilities):
    if coordinator_type == "centralized":
        return await coordinator.assign_best(agent_id)
    elif coordinator_type == "hierarchical":
        return await coordinator.assign_best(agent_id)
    else:  # independent
        return await coordinator.assign_best(agent_id, capabilities)
```

## Integration with Existing Scheduler

### Step 1: Identify Integration Point

Locate your existing task dispatch/scheduling code. Common patterns:

```python
# Before: Direct dispatch
async def dispatch_task(task, agent):
    agent.execute(task)

# After: Route through topology router
async def dispatch_task(task, agent):
    # Batch tasks for routing
    tasks = get_pending_tasks()
    coordinator_type = router.route(tasks)
    coordinator = router.get_coordinator(coordinator_type)
    
    # Submit to coordinator
    await coordinator.submit_task(task)
```

### Step 2: Modify Agent Loop

Update agent execution loop to pull from coordinator:

```python
# Before: Direct task queue
async def agent_loop(agent):
    while True:
        task = task_queue.get()
        await execute_task(task)

# After: Pull from coordinator
async def agent_loop(agent):
    # Register with coordinator
    await coordinator.register_agent(agent.id, agent.capabilities)
    
    while True:
        # Request task assignment
        task = await coordinator.assign_best(agent.id)
        if task:
            await execute_task(task)
            await coordinator.complete_task(task.task_id, success=True)
        else:
            await asyncio.sleep(0.1)  # Back off if no tasks
```

### Step 3: Add Stigmergic Coordination

Enhance agent behavior with environmental awareness:

```python
async def agent_loop_with_stigmergy(agent, environment):
    await coordinator.register_agent(agent.id, agent.capabilities)
    
    while True:
        # Deposit trail
        await environment.deposit_trace(
            trace_type=TraceType.AGENT_PATH,
            position=agent.position,
            intensity=0.7,
            depositor_id=agent.id,
        )
        
        # Sense environment
        traces = await environment.sense_traces(
            position=agent.position,
            radius=5,
        )
        
        # Adjust behavior based on density
        density = await environment.get_density(agent.position, radius=10)
        if density > 0.8:
            # High density, explore elsewhere
            agent.position = explore_new_area()
        
        # Get task
        task = await coordinator.assign_best(agent.id)
        if task:
            result = await execute_task(task)
            
            # Mark completion in environment
            await environment.deposit_trace(
                trace_type=TraceType.TASK_COMPLETE,
                position=agent.position,
                intensity=1.0,
                metadata={"task_id": task.task_id},
                depositor_id=agent.id,
            )
            
            await coordinator.complete_task(task.task_id, success=result.success)
```

## Single StigmergicEnvironment Pattern

### Create Singleton Instance

```python
# In your application initialization
from python.qbit.stigmergy import StigmergicEnvironment

# Global environment instance
_global_environment = None

async def get_environment():
    global _global_environment
    if _global_environment is None:
        _global_environment = StigmergicEnvironment(
            grid_size=1000,
            decay_rate=0.01,
            enable_background_decay=True,
        )
        await _global_environment.initialize()
    return _global_environment

# In agent code
environment = await get_environment()
```

### Dependency Injection Pattern

```python
class AgentManager:
    def __init__(self, environment: StigmergicEnvironment):
        self.environment = environment
        self.agents = []
    
    async def spawn_agent(self, agent_id, capabilities):
        agent = Agent(
            agent_id=agent_id,
            capabilities=capabilities,
            environment=self.environment,  # Inject shared environment
        )
        self.agents.append(agent)
        return agent

# Initialize once
environment = StigmergicEnvironment(grid_size=1000)
await environment.initialize()

# Inject into manager
manager = AgentManager(environment=environment)
```

## Multi-Node Deployments with Redis

### Setup Redis Backend

```bash
# Start Redis server
docker run -d -p 6379:6379 redis:latest

# Or use managed Redis service
# export REDIS_URL=redis://user:password@your-redis-host:6379
```

### Environment Configuration

```python
import os

# Set Redis URL (can be in .env file)
os.environ["REDIS_URL"] = "redis://localhost:6379"

# Create environment with Redis backend
environment = StigmergicEnvironment(
    grid_size=1000,
    backend="redis",
    enable_background_decay=True,
)
await environment.initialize()
```

### Multi-Node Agent Deployment

```python
# On Node 1
async def run_node_1():
    env = StigmergicEnvironment(backend="redis")
    await env.initialize()
    
    # Spawn agents 0-99
    agents = [Agent(i, environment=env) for i in range(100)]
    await asyncio.gather(*[agent.run() for agent in agents])

# On Node 2
async def run_node_2():
    # Same Redis URL, shared environment
    env = StigmergicEnvironment(backend="redis")
    await env.initialize()
    
    # Spawn agents 100-199
    agents = [Agent(i, environment=env) for i in range(100, 200)]
    await asyncio.gather(*[agent.run() for agent in agents])
```

## Configuration Best Practices

### Development
```python
config = Config(
    centralized_threshold=50,
    hierarchical_threshold=200,
    parallelism_threshold=0.6,
    enable_ml_policy=False,
)

environment = StigmergicEnvironment(
    grid_size=500,
    backend="memory",
    enable_background_decay=False,  # Manual control for testing
)
```

### Production
```python
config = Config(
    centralized_threshold=100,
    hierarchical_threshold=1000,
    parallelism_threshold=0.7,
    num_clusters=8,  # Scale with agent count
    enable_ml_policy=False,  # Enable after training
)

environment = StigmergicEnvironment(
    grid_size=2000,
    backend="redis",
    redis_url=os.getenv("REDIS_URL"),
    decay_rate=0.01,
    enable_background_decay=True,
)
```

## Environment Variables

```bash
# Redis backend
export REDIS_URL=redis://localhost:6379
export QBIT_ENABLE_REDIS=true

# Logging
export QBIT_LOG_LEVEL=INFO

# Topology routing
export QBIT_CENTRALIZED_THRESHOLD=100
export QBIT_HIERARCHICAL_THRESHOLD=1000
export QBIT_PARALLELISM_THRESHOLD=0.7
```

## Monitoring and Observability

### Enable Telemetry

```python
from python.qbit.telemetry import setup_logging, record_metric

# Setup logging
setup_logging(level="INFO")

# Record custom metrics
record_metric("agent.tasks_completed", 1.0, labels={"agent_id": "agent_1"})
```

### Monitor Routing Decisions

```python
# Check auto-tuning stats
stats = router.get_auto_tuning_stats()
logger.info(f"Parallel score stats: {stats}")

# Monitor coordinator stats
centralized_stats = await router.centralized.get_stats()
hierarchical_stats = await router.hierarchical.get_stats()
independent_stats = await router.independent.get_stats()
```

## Testing Integration

```python
# In your test suite
import pytest
from python.qbit.topology import TopologyRouter
from python.qbit.stigmergy import StigmergicEnvironment

@pytest.mark.asyncio
async def test_integration():
    # Setup
    router = TopologyRouter()
    env = StigmergicEnvironment(grid_size=100)
    await env.initialize()
    
    # Create test tasks
    tasks = [Task(task_id=f"task_{i}", task_type="test") for i in range(10)]
    
    # Route and execute
    coordinator_type = router.route(tasks)
    coordinator = router.get_coordinator(coordinator_type)
    
    for task in tasks:
        await coordinator.submit_task(task)
    
    # Cleanup
    await env.cleanup()
```

## Migration Checklist

- [ ] Install dependencies
- [ ] Initialize TopologyRouter with appropriate config
- [ ] Create StigmergicEnvironment (singleton pattern)
- [ ] Update task dispatch to route through coordinator
- [ ] Modify agent loop to pull from coordinator
- [ ] Add stigmergic coordination to agent behavior
- [ ] Configure environment variables
- [ ] Enable telemetry and monitoring
- [ ] Test with simulated workload
- [ ] Deploy to staging
- [ ] Monitor and tune thresholds
- [ ] Deploy to production

## Troubleshooting

### Import Errors
```python
# Ensure python/qbit is in PYTHONPATH
import sys
sys.path.insert(0, '/path/to/Q-BIT')
```

### Redis Connection Issues
```bash
# Test Redis connectivity
redis-cli ping
# Should return: PONG
```

### Performance Issues
- Check coordinator stats for bottlenecks
- Review auto-tuning stats for routing patterns
- Monitor trace density in environment
- Consider increasing num_clusters

## Next Steps

1. Read [Topology Refactor](topology_refactor.md) for tuning guidance
2. Review [Stigmergic Layer](stigmergic_layer.md) for API details
3. Run tests: `pytest tests/`
4. Run simulator: See harness/simulator.py examples

## Support

For issues and questions:
- GitHub Issues: https://github.com/Dbourassa11/Q-BIT/issues
- Documentation: See docs/ directory
- Code examples: See tests/ directory
