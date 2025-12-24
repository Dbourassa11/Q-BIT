"""
Telemetry and observability for Q-BIT.

Provides structured logging and Prometheus-compatible metrics
without requiring external services.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from prometheus_client import Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# Global metrics registry (using dict if prometheus not available)
_metrics_registry: Dict[str, Any] = {}
_agent_trajectories: List[Dict[str, Any]] = []


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
) -> None:
    """Set up structured logging for Q-BIT.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Optional custom format string
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def record_metric(
    name: str,
    value: float,
    labels: Optional[Dict[str, str]] = None,
    metric_type: str = "gauge",
) -> None:
    """Record a metric value.
    
    Args:
        name: Metric name (e.g., "topology.parallel_score")
        value: Metric value
        labels: Optional metric labels
        metric_type: Type of metric ("counter", "gauge", "histogram")
    """
    labels = labels or {}
    
    if PROMETHEUS_AVAILABLE:
        # Use Prometheus metrics if available
        metric_key = (name, metric_type)
        
        if metric_key not in _metrics_registry:
            # Create metric if it doesn't exist
            if metric_type == "counter":
                metric = Counter(
                    name.replace(".", "_"),
                    f"Q-BIT metric: {name}",
                    list(labels.keys()) if labels else [],
                )
            elif metric_type == "histogram":
                metric = Histogram(
                    name.replace(".", "_"),
                    f"Q-BIT metric: {name}",
                    list(labels.keys()) if labels else [],
                )
            else:  # gauge
                metric = Gauge(
                    name.replace(".", "_"),
                    f"Q-BIT metric: {name}",
                    list(labels.keys()) if labels else [],
                )
            
            _metrics_registry[metric_key] = metric
        
        metric = _metrics_registry[metric_key]
        
        # Record value
        if labels:
            if metric_type == "counter":
                metric.labels(**labels).inc(value)
            elif metric_type == "histogram":
                metric.labels(**labels).observe(value)
            else:  # gauge
                metric.labels(**labels).set(value)
        else:
            if metric_type == "counter":
                metric.inc(value)
            elif metric_type == "histogram":
                metric.observe(value)
            else:  # gauge
                metric.set(value)
    else:
        # Fallback to simple dict storage
        if name not in _metrics_registry:
            _metrics_registry[name] = []
        
        _metrics_registry[name].append({
            "value": value,
            "labels": labels,
            "timestamp": datetime.utcnow().isoformat(),
        })


def record_agent_trajectory(
    agent_id: str,
    position: Tuple[int, int],
    action: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Record an agent's trajectory point.
    
    Args:
        agent_id: Unique agent identifier
        position: Agent position (x, y)
        action: Action taken at this position
        metadata: Additional trajectory metadata
    """
    trajectory_point = {
        "agent_id": agent_id,
        "position": position,
        "action": action,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    _agent_trajectories.append(trajectory_point)
    
    # Limit trajectory history to prevent unbounded growth
    max_trajectory_points = 10000
    if len(_agent_trajectories) > max_trajectory_points:
        _agent_trajectories.pop(0)


def get_agent_trajectory(
    agent_id: str,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Get trajectory history for an agent.
    
    Args:
        agent_id: Agent identifier
        limit: Optional limit on number of points to return
    
    Returns:
        List of trajectory points
    """
    trajectory = [
        point for point in _agent_trajectories
        if point["agent_id"] == agent_id
    ]
    
    if limit:
        trajectory = trajectory[-limit:]
    
    return trajectory


def get_all_metrics() -> Dict[str, Any]:
    """Get all recorded metrics.
    
    Returns:
        Dictionary of all metrics
    """
    if PROMETHEUS_AVAILABLE:
        # For Prometheus, return registry info
        return {
            "prometheus_enabled": True,
            "metrics_count": len(_metrics_registry),
            "metric_names": [
                name for name, _ in _metrics_registry.keys()
            ],
        }
    else:
        # Return raw metric data
        return {
            "prometheus_enabled": False,
            "metrics": dict(_metrics_registry),
        }


def clear_metrics() -> None:
    """Clear all metrics (useful for testing)."""
    global _metrics_registry, _agent_trajectories
    _metrics_registry.clear()
    _agent_trajectories.clear()


def get_metrics_summary() -> Dict[str, Any]:
    """Get summary statistics of recorded metrics.
    
    Returns:
        Summary statistics
    """
    if PROMETHEUS_AVAILABLE:
        return {
            "prometheus_enabled": True,
            "total_metrics": len(_metrics_registry),
        }
    else:
        summary = {
            "prometheus_enabled": False,
            "total_metrics": len(_metrics_registry),
            "metrics": {},
        }
        
        for name, values in _metrics_registry.items():
            if isinstance(values, list) and values:
                numeric_values = [v["value"] for v in values if isinstance(v.get("value"), (int, float))]
                if numeric_values:
                    summary["metrics"][name] = {
                        "count": len(numeric_values),
                        "mean": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                    }
        
        return summary
