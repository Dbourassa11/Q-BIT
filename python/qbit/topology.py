"""
Topology router with parallelism analysis and coordinator selection.

Routes tasks to appropriate coordinators based on workload characteristics
and parallelism analysis.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

from python.qbit.coordinators import (
    CentralizedCoordinator,
    HierarchicalClusters,
    IndependentAgents,
    Task,
)
from python.qbit.telemetry import record_metric


@dataclass
class Config:
    """Configuration for topology routing.
    
    Attributes:
        centralized_threshold: Max tasks for centralized coordinator
        hierarchical_threshold: Max tasks for hierarchical clusters
        parallelism_threshold: Parallelism score threshold for coordinator selection
        num_clusters: Number of clusters for hierarchical mode
        enable_ml_policy: Whether to use ML-based routing policy
    """
    
    centralized_threshold: int = 100
    hierarchical_threshold: int = 1000
    parallelism_threshold: float = 0.7
    num_clusters: int = 4
    enable_ml_policy: bool = False


class MLPolicy(Protocol):
    """Protocol for pluggable ML-based routing policies."""
    
    def predict_coordinator(
        self,
        features: Dict[str, Any],
    ) -> str:
        """Predict best coordinator type for given features.
        
        Args:
            features: Extracted features from analyze_parallelism
        
        Returns:
            Coordinator type: "centralized", "hierarchical", or "independent"
        """
        ...


class TopologyRouter:
    """Routes tasks to coordinators based on workload analysis.
    
    Analyzes task parallelism and workload characteristics to select
    the optimal coordination strategy.
    
    Args:
        config: Router configuration
        ml_policy: Optional ML-based routing policy
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        ml_policy: Optional[MLPolicy] = None,
    ) -> None:
        """Initialize the topology router."""
        self.config = config or Config()
        self.ml_policy = ml_policy
        
        # Initialize coordinators
        self.centralized = CentralizedCoordinator()
        self.hierarchical = HierarchicalClusters(num_clusters=self.config.num_clusters)
        self.independent = IndependentAgents()
        
        # Track parallel scores for auto-tuning
        self._parallel_scores: List[float] = []
    
    def analyze_parallelism(
        self,
        tasks: List[Task],
    ) -> Dict[str, Any]:
        """Analyze parallelism potential of a task batch.
        
        Extracts features to determine the best coordination strategy:
        - Task count and distribution
        - Dependency analysis
        - Resource contention
        - Priority distribution
        
        Args:
            tasks: List of tasks to analyze
        
        Returns:
            Feature dictionary with parallelism metrics
        """
        if not tasks:
            return {
                "task_count": 0,
                "parallel_score": 0.0,
                "avg_priority": 0.0,
                "unique_types": 0,
                "resource_diversity": 0.0,
            }
        
        # Basic metrics
        task_count = len(tasks)
        avg_priority = sum(t.priority for t in tasks) / task_count
        unique_types = len(set(t.task_type for t in tasks))
        
        # Resource diversity: how diverse are the resource requirements?
        all_requirements = set()
        for task in tasks:
            all_requirements.update(task.requirements.keys())
        
        resource_diversity = len(all_requirements) / max(task_count, 1)
        
        # Parallelism score: combination of factors
        # Higher score = more parallelizable
        type_diversity_score = min(unique_types / max(task_count * 0.5, 1), 1.0)
        resource_score = min(resource_diversity, 1.0)
        
        # Tasks with low priority variance are more parallelizable
        priority_variance = (
            sum((t.priority - avg_priority) ** 2 for t in tasks) / task_count
        ) ** 0.5
        priority_score = 1.0 / (1.0 + priority_variance / 10.0)
        
        # Combined parallel score (weighted average)
        parallel_score = (
            0.4 * type_diversity_score +
            0.3 * resource_score +
            0.3 * priority_score
        )
        
        features = {
            "task_count": task_count,
            "parallel_score": parallel_score,
            "avg_priority": avg_priority,
            "unique_types": unique_types,
            "resource_diversity": resource_diversity,
            "priority_variance": priority_variance,
        }
        
        # Record for auto-tuning
        self._parallel_scores.append(parallel_score)
        record_metric("topology.parallel_score", parallel_score)
        
        return features
    
    def route(
        self,
        tasks: List[Task],
    ) -> str:
        """Route tasks to appropriate coordinator.
        
        Args:
            tasks: Tasks to route
        
        Returns:
            Coordinator type: "centralized", "hierarchical", or "independent"
        """
        features = self.analyze_parallelism(tasks)
        
        # Use ML policy if enabled and available
        if self.config.enable_ml_policy and self.ml_policy is not None:
            coordinator_type = self.ml_policy.predict_coordinator(features)
            record_metric("topology.route", 1.0, {"coordinator": coordinator_type, "source": "ml"})
            return coordinator_type
        
        # Heuristic-based routing
        task_count = features["task_count"]
        parallel_score = features["parallel_score"]
        
        # Decision logic based on thresholds
        if task_count <= self.config.centralized_threshold:
            coordinator_type = "centralized"
        elif task_count <= self.config.hierarchical_threshold:
            # Choose between hierarchical and independent based on parallelism
            if parallel_score >= self.config.parallelism_threshold:
                coordinator_type = "independent"
            else:
                coordinator_type = "hierarchical"
        else:
            # For very large workloads, prefer independent agents
            coordinator_type = "independent"
        
        record_metric("topology.route", 1.0, {"coordinator": coordinator_type, "source": "heuristic"})
        return coordinator_type
    
    def get_coordinator(
        self,
        coordinator_type: str,
    ) -> Any:
        """Get coordinator instance by type.
        
        Args:
            coordinator_type: Type of coordinator
        
        Returns:
            Coordinator instance
        
        Raises:
            ValueError: If coordinator type is unknown
        """
        if coordinator_type == "centralized":
            return self.centralized
        elif coordinator_type == "hierarchical":
            return self.hierarchical
        elif coordinator_type == "independent":
            return self.independent
        else:
            raise ValueError(f"Unknown coordinator type: {coordinator_type}")
    
    def get_auto_tuning_stats(self) -> Dict[str, Any]:
        """Get statistics for auto-tuning.
        
        Returns:
            Statistics about parallel scores and routing decisions
        """
        if not self._parallel_scores:
            return {
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
            }
        
        return {
            "count": len(self._parallel_scores),
            "mean": sum(self._parallel_scores) / len(self._parallel_scores),
            "min": min(self._parallel_scores),
            "max": max(self._parallel_scores),
            "histogram": self._compute_histogram(self._parallel_scores),
        }
    
    def _compute_histogram(
        self,
        scores: List[float],
        bins: int = 10,
    ) -> Dict[str, int]:
        """Compute histogram of parallel scores.
        
        Args:
            scores: List of scores
            bins: Number of histogram bins
        
        Returns:
            Histogram as dict of bin_label -> count
        """
        histogram: Dict[str, int] = {}
        bin_width = 1.0 / bins
        
        for score in scores:
            bin_idx = min(int(score / bin_width), bins - 1)
            bin_label = f"{bin_idx * bin_width:.2f}-{(bin_idx + 1) * bin_width:.2f}"
            histogram[bin_label] = histogram.get(bin_label, 0) + 1
        
        return histogram
