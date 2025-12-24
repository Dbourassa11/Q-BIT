"""
Model router for cost and capability-based model selection.

Routes requests to appropriate models based on capabilities,
cost constraints, and performance requirements.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ModelSpec:
    """Specification for a model in the router.
    
    Attributes:
        model_id: Unique identifier for the model
        capabilities: Model capabilities (e.g., {"reasoning": 0.9, "code_gen": 0.8})
        cost_per_token: Cost per token in credits/dollars
        max_tokens: Maximum token capacity
        latency_ms: Average response latency in milliseconds
        metadata: Additional model metadata
    """
    
    model_id: str
    capabilities: Dict[str, float]
    cost_per_token: float = 0.0
    max_tokens: int = 4096
    latency_ms: float = 100.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = {}
    
    def matches_requirements(
        self,
        requirements: Dict[str, float],
    ) -> bool:
        """Check if model capabilities meet requirements.
        
        Args:
            requirements: Required capabilities and minimum levels
        
        Returns:
            True if model meets all requirements
        """
        for capability, min_level in requirements.items():
            if capability not in self.capabilities:
                return False
            if self.capabilities[capability] < min_level:
                return False
        return True


class ModelRouter:
    """Routes requests to models based on cost and capabilities.
    
    Selects the most cost-effective model that meets the required
    capabilities and constraints.
    
    Args:
        models: List of available models
        default_model_id: Default model if no match found
    """
    
    def __init__(
        self,
        models: Optional[List[ModelSpec]] = None,
        default_model_id: Optional[str] = None,
    ) -> None:
        """Initialize the model router."""
        self.models: Dict[str, ModelSpec] = {}
        if models:
            for model in models:
                self.add_model(model)
        
        self.default_model_id = default_model_id
        self._routing_stats: Dict[str, int] = {}
    
    def add_model(self, model: ModelSpec) -> None:
        """Add a model to the router.
        
        Args:
            model: Model specification to add
        """
        self.models[model.model_id] = model
    
    def remove_model(self, model_id: str) -> None:
        """Remove a model from the router.
        
        Args:
            model_id: ID of model to remove
        """
        self.models.pop(model_id, None)
    
    def route(
        self,
        requirements: Dict[str, float],
        max_cost: Optional[float] = None,
        max_latency_ms: Optional[float] = None,
        prefer_cost: bool = True,
    ) -> Optional[str]:
        """Route a request to the best matching model.
        
        Args:
            requirements: Required capabilities
            max_cost: Maximum cost per token constraint
            max_latency_ms: Maximum latency constraint
            prefer_cost: If True, prefer lower cost; otherwise prefer higher capability
        
        Returns:
            Model ID of the selected model, or None if no match
        """
        # Filter models that meet requirements and constraints
        candidates = []
        
        for model in self.models.values():
            # Check capability requirements
            if not model.matches_requirements(requirements):
                continue
            
            # Check cost constraint
            if max_cost is not None and model.cost_per_token > max_cost:
                continue
            
            # Check latency constraint
            if max_latency_ms is not None and model.latency_ms > max_latency_ms:
                continue
            
            candidates.append(model)
        
        if not candidates:
            # Return default model if available
            if self.default_model_id and self.default_model_id in self.models:
                self._record_routing(self.default_model_id)
                return self.default_model_id
            return None
        
        # Select best candidate based on preference
        if prefer_cost:
            # Choose lowest cost model
            best_model = min(candidates, key=lambda m: m.cost_per_token)
        else:
            # Choose model with highest total capability score
            def capability_score(model: ModelSpec) -> float:
                return sum(
                    model.capabilities.get(cap, 0.0)
                    for cap in requirements.keys()
                )
            
            best_model = max(candidates, key=capability_score)
        
        self._record_routing(best_model.model_id)
        return best_model.model_id
    
    def get_model(self, model_id: str) -> Optional[ModelSpec]:
        """Get model specification by ID.
        
        Args:
            model_id: ID of the model
        
        Returns:
            ModelSpec if found, None otherwise
        """
        return self.models.get(model_id)
    
    def estimate_cost(
        self,
        model_id: str,
        num_tokens: int,
    ) -> float:
        """Estimate cost for a request.
        
        Args:
            model_id: ID of the model
            num_tokens: Number of tokens to process
        
        Returns:
            Estimated cost
        
        Raises:
            ValueError: If model not found
        """
        model = self.get_model(model_id)
        if model is None:
            raise ValueError(f"Model not found: {model_id}")
        
        return model.cost_per_token * num_tokens
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics.
        
        Returns:
            Statistics about model usage
        """
        return {
            "total_routes": sum(self._routing_stats.values()),
            "model_usage": dict(self._routing_stats),
            "available_models": len(self.models),
        }
    
    def _record_routing(self, model_id: str) -> None:
        """Record a routing decision for statistics.
        
        Args:
            model_id: ID of the routed model
        """
        self._routing_stats[model_id] = self._routing_stats.get(model_id, 0) + 1
