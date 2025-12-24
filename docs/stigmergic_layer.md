# Stigmergic Coordination Layer

## Overview

The stigmergic coordination layer enables indirect coordination between agents through environmental traces, inspired by ant pheromone trails and swarm intelligence.

## Core Concepts

### Stigmergy
Stigmergy is a mechanism of indirect coordination where agents modify their environment, and these modifications influence the behavior of other agents. In Q-BIT, agents deposit and sense traces to coordinate without direct communication.

### Traces
A trace is a piece of information deposited in the environment:
- **Type**: Category of trace (task completion, path, resource claim, etc.)
- **Position**: Grid location (x, y)
- **Intensity**: Strength (0.0 to 1.0)
- **Metadata**: Additional context
- **Depositor**: Agent that created the trace

### Decay
Traces naturally decay over time, allowing old information to fade and preventing unbounded memory growth.

## API Reference

### StigmergicEnvironment

The main interface for stigmergic coordination.

#### Initialization

```python
from python.qbit.stigmergy import StigmergicEnvironment

# In-memory backend (default)
env = StigmergicEnvironment(
    grid_size=1000,           # 1000x1000 grid
    decay_rate=0.01,          # 1% decay per second
    density_threshold=0.5,    # Density threshold for clustering
    backend="memory",         # Use in-memory sparse storage
    enable_background_decay=True,  # Auto-decay in background
)

await env.initialize()
```

#### Core Operations

**Deposit Trace**
```python
from python.qbit.stigmergy import TraceType

await env.deposit_trace(
    trace_type=TraceType.TASK_COMPLETE,
    position=(100, 200),
    intensity=0.8,
    metadata={"task_id": "task_123"},
    depositor_id="agent_1",
)
```

**Sense Traces**
```python
# Sense all traces within radius 5
traces = await env.sense_traces(
    position=(100, 200),
    radius=5,
)

# Sense specific trace type
path_traces = await env.sense_traces(
    position=(100, 200),
    radius=10,
    trace_type=TraceType.AGENT_PATH,
)
```

**Apply Decay**
```python
# Manual decay (if not using background decay)
await env.decay()
```

**Get Density**
```python
density = await env.get_density(
    position=(150, 150),
    radius=10,
)
# Returns: density value (0.0 to 1.0+)
```

**Clear Traces**
```python
# Clear specific position
await env.clear(position=(100, 200))

# Clear all traces
await env.clear()
```

### TraceType Enum

Built-in trace types:
- `TASK_COMPLETE`: Task completion marker
- `RESOURCE_CLAIM`: Resource reservation
- `AGENT_PATH`: Agent movement trail
- `COLLABORATION_REQUEST`: Request for collaboration
- `PERFORMANCE_METRIC`: Performance indicator
- `CUSTOM`: Custom application-specific trace

### Trace Dataclass

```python
from python.qbit.stigmergy import Trace

trace = Trace(
    trace_type=TraceType.AGENT_PATH,
    position=(x, y),
    intensity=0.9,
    metadata={"speed": 1.5},
    depositor_id="agent_1",
)
```

## Backends

### In-Memory Backend (Default)

**Characteristics:**
- Fast, low latency
- Sparse dictionary storage (scales to large grids)
- Single-node only
- No persistence

**Use cases:**
- Development and testing
- Single-node deployments
- CI/CD pipelines

**Configuration:**
```python
env = StigmergicEnvironment(backend="memory")
```

### Redis Backend (Optional)

**Characteristics:**
- Distributed, multi-node coordination
- Persistent (configurable)
- Higher latency than in-memory
- Requires Redis server

**Use cases:**
- Multi-node agent swarms
- Persistent coordination state
- Production deployments

**Configuration:**
```python
import os

os.environ["REDIS_URL"] = "redis://localhost:6379"

env = StigmergicEnvironment(
    backend="redis",
    redis_url="redis://localhost:6379",  # Optional, uses env var if not set
)
```

**Enabling Redis:**

1. Install Redis dependency:
```bash
pip install redis
```

2. Set environment variable:
```bash
export REDIS_URL=redis://localhost:6379
# OR for production with auth:
export REDIS_URL=redis://:password@host:6379
```

3. Create environment with Redis backend:
```python
env = StigmergicEnvironment(backend="redis")
```

**Error Handling:**
- If Redis is not installed: `ImportError` with installation instructions
- If `REDIS_URL` not set: `ValueError` with guidance

## Scaling Guidance

### Single Node
- Use in-memory backend
- Grid size up to 10,000 x 10,000
- Supports 1000+ agents easily

### Multi-Node
- Use Redis backend
- Share `REDIS_URL` across nodes
- Grid size limited by Redis memory
- Supports 10,000+ agents

### Performance Tips

1. **Grid Size**: Choose smallest grid that fits your space
   - Smaller grid = less memory, faster operations
   - Rule of thumb: 10x the agent movement range

2. **Decay Rate**: Balance freshness vs. computation
   - Higher rate = fresher data, more CPU for decay
   - Lower rate = longer memory, less CPU
   - Typical: 0.01 (1% per second) to 0.1 (10% per second)

3. **Sensing Radius**: Keep small for efficiency
   - Radius 1-5: Very fast
   - Radius 10-20: Moderate
   - Radius >50: Slower, consider caching

4. **Background Decay**: Use for real-time systems
   - Enable for production with continuous operation
   - Disable for testing or batch processing

## Integration Examples

### Basic Agent Coordination

```python
from python.qbit.stigmergy import StigmergicEnvironment, TraceType

# Initialize environment
env = StigmergicEnvironment(grid_size=500)
await env.initialize()

# Agent deposits path
async def agent_step(agent_id, position):
    # Deposit trail
    await env.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=position,
        intensity=0.7,
        depositor_id=agent_id,
    )
    
    # Check density (avoid crowded areas)
    density = await env.get_density(position, radius=5)
    if density > 0.5:
        # Move away from crowd
        return move_away()
    
    # Follow trails
    traces = await env.sense_traces(position, radius=3)
    if traces:
        return move_toward_strongest_trace(traces)
    
    return explore_randomly()
```

### Task Coordination

```python
# Agent marks task completion
await env.deposit_trace(
    trace_type=TraceType.TASK_COMPLETE,
    position=task_position,
    intensity=1.0,
    metadata={"task_id": task.task_id, "result": "success"},
    depositor_id=agent_id,
)

# Other agents discover completed work
completed = await env.sense_traces(
    position=search_area,
    radius=10,
    trace_type=TraceType.TASK_COMPLETE,
)
```

## Best Practices

1. **Use sparse grids**: Don't allocate full 2D array, use sparse storage
2. **Set appropriate decay**: Match decay rate to your time scale
3. **Limit sensing radius**: Smaller radius = faster queries
4. **Use trace types**: Filter by type for efficient sensing
5. **Background decay**: Enable in production for automatic cleanup
6. **Monitor density**: Use `get_density()` to detect hotspots

## Troubleshooting

### High memory usage
- Reduce grid_size
- Increase decay_rate
- Clear old traces periodically

### Slow sensing
- Reduce sensing radius
- Use trace type filtering
- Consider Redis backend with indexing

### Traces not decaying
- Verify `enable_background_decay=True`
- Or call `env.decay()` manually
- Check decay_rate is > 0

### Redis connection errors
- Verify Redis server is running
- Check `REDIS_URL` is correct
- Ensure network connectivity

## References

- [Topology Refactor](topology_refactor.md)
- [Integration Guide](integration.md)
- API documentation in source code
