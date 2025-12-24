# Hybrid Topology Refactor

## Overview

The Hybrid Topology Router provides intelligent task routing to different coordination strategies based on workload characteristics and parallelism analysis.

## Architecture

The system consists of three main coordinator types:

### 1. Centralized Coordinator
- **Best for**: Small to medium workloads (<100 tasks)
- **Characteristics**: Single point of coordination, global view
- **Advantages**: Simple, optimal for sequential dependencies
- **Trade-offs**: Single point of bottleneck for large workloads

### 2. Hierarchical Clusters
- **Best for**: Medium to large workloads (100-1000 tasks) with moderate parallelism
- **Characteristics**: Agents organized into clusters with local coordinators
- **Advantages**: Reduced coordination overhead, scalable
- **Trade-offs**: May not achieve perfect load balancing

### 3. Independent Agents
- **Best for**: Large workloads (>1000 tasks) with high parallelism
- **Characteristics**: Agents autonomously claim tasks from shared pool
- **Advantages**: Maximum scalability, minimal coordination overhead
- **Trade-offs**: No global optimization, potential contention

## Parallelism Analysis

The `TopologyRouter.analyze_parallelism()` method extracts features to determine routing:

### Features Extracted
- **Task Count**: Total number of tasks in batch
- **Parallel Score**: 0.0-1.0 metric indicating parallelizability
- **Type Diversity**: Number of unique task types
- **Resource Diversity**: Variety of required resources
- **Priority Variance**: Spread of task priorities

### Parallel Score Calculation
```
parallel_score = 0.4 * type_diversity_score +
                 0.3 * resource_score +
                 0.3 * priority_score
```

Higher scores indicate more parallelizable workloads.

## Configuration

Configure routing thresholds via the `Config` dataclass:

```python
from python.qbit.topology import Config, TopologyRouter

config = Config(
    centralized_threshold=100,      # Max tasks for centralized
    hierarchical_threshold=1000,    # Max tasks for hierarchical
    parallelism_threshold=0.7,      # Threshold for independent routing
    num_clusters=4,                 # Clusters for hierarchical mode
    enable_ml_policy=False,         # Use ML-based routing
)

router = TopologyRouter(config=config)
```

## Tuning Guidelines

### Centralized Threshold
- **Increase** if you have powerful coordination infrastructure
- **Decrease** if coordination becomes a bottleneck
- **Default**: 100 tasks

### Hierarchical Threshold
- **Increase** for larger deployments
- **Decrease** if hierarchical overhead is high
- **Default**: 1000 tasks

### Parallelism Threshold
- **Increase** (e.g., 0.8) to prefer hierarchical over independent
- **Decrease** (e.g., 0.6) to prefer independent coordination sooner
- **Default**: 0.7

### Number of Clusters
- **Increase** for larger agent populations
- **Decrease** if clusters are underutilized
- **Rule of thumb**: 1 cluster per 20-50 agents
- **Default**: 4 clusters

## Auto-Tuning

The router records parallel score histogram for future auto-tuning:

```python
stats = router.get_auto_tuning_stats()
# Returns: count, mean, min, max, histogram of scores
```

Use these statistics to:
1. Identify common workload patterns
2. Adjust thresholds based on actual distribution
3. Train ML models for routing decisions

## ML Policy Interface

You can plug in custom ML-based routing policies:

```python
class CustomMLPolicy:
    def predict_coordinator(self, features: Dict[str, Any]) -> str:
        # Your ML logic here
        # Return: "centralized", "hierarchical", or "independent"
        pass

config = Config(enable_ml_policy=True)
router = TopologyRouter(config=config, ml_policy=CustomMLPolicy())
```

## Integration Steps

See [integration.md](integration.md) for detailed integration instructions.

## Performance Considerations

### Memory Usage
- **Centralized**: O(T) where T = total tasks
- **Hierarchical**: O(T + C) where C = num_clusters
- **Independent**: O(T) with distributed storage

### Latency
- **Centralized**: ~1ms per task assignment
- **Hierarchical**: ~0.5ms per task assignment (amortized)
- **Independent**: ~0.1ms per task claim (highly parallel)

### Throughput
- **Centralized**: Up to 1000 tasks/sec
- **Hierarchical**: Up to 10,000 tasks/sec
- **Independent**: Up to 100,000 tasks/sec

## Monitoring

The router records metrics via telemetry:

- `topology.parallel_score`: Histogram of parallel scores
- `topology.route`: Routing decisions with labels

Use these for:
- Monitoring routing patterns
- Detecting workload shifts
- Performance analysis

## Best Practices

1. **Start with defaults** and tune based on observed performance
2. **Monitor parallel scores** to understand your workload
3. **Use hierarchical** for most production workloads
4. **Reserve independent** for truly massive parallel workloads
5. **Enable ML policy** only after collecting sufficient training data
6. **Test routing** with your actual workload before production

## Troubleshooting

### High coordination overhead
- Increase centralized_threshold
- Decrease num_clusters

### Poor load balancing
- Switch from independent to hierarchical
- Increase num_clusters

### Suboptimal routing
- Review auto-tuning stats
- Adjust parallelism_threshold
- Consider ML policy

## References

- [Stigmergic Coordination Layer](stigmergic_layer.md)
- [Integration Guide](integration.md)
- API documentation in source code docstrings
