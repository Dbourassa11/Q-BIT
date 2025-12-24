"""
Q-BIT Hybrid Topology and Stigmergic Coordination Layer.

This package provides:
- Stigmergic environment for agent coordination
- Multiple coordinator types (Centralized, Hierarchical, Independent)
- Topology routing with parallelism analysis
- Model routing with cost/capability based selection
- Transactional safety with pluggable backends
- Telemetry and monitoring
"""

from typing import List

__version__ = "0.1.0"

# Import key classes for easy access
from python.qbit.stigmergy import (
    StigmergicEnvironment,
    Trace,
    TraceType,
)
from python.qbit.coordinators import (
    CentralizedCoordinator,
    HierarchicalClusters,
    IndependentAgents,
    Task,
)
from python.qbit.topology import (
    TopologyRouter,
    Config,
)
from python.qbit.model_router import (
    ModelRouter,
    ModelSpec,
)
from python.qbit.transaction import (
    TransactionalSafety,
)
from python.qbit.telemetry import (
    setup_logging,
    record_metric,
)

__all__: List[str] = [
    # Stigmergy
    "StigmergicEnvironment",
    "Trace",
    "TraceType",
    # Coordinators
    "CentralizedCoordinator",
    "HierarchicalClusters",
    "IndependentAgents",
    "Task",
    # Topology
    "TopologyRouter",
    "Config",
    # Model Router
    "ModelRouter",
    "ModelSpec",
    # Transaction
    "TransactionalSafety",
    # Telemetry
    "setup_logging",
    "record_metric",
]
