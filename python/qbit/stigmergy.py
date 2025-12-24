"""
Stigmergic coordination layer for Q-BIT agents.

This module provides an asynchronous stigmergic environment where agents
can deposit and sense traces for indirect coordination. Supports both
in-memory (sparse dict) and optional Redis backends.
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TraceType(Enum):
    """Types of traces that can be deposited in the stigmergic environment."""
    
    TASK_COMPLETE = "task_complete"
    RESOURCE_CLAIM = "resource_claim"
    AGENT_PATH = "agent_path"
    COLLABORATION_REQUEST = "collaboration_request"
    PERFORMANCE_METRIC = "performance_metric"
    CUSTOM = "custom"


@dataclass
class Trace:
    """A trace deposited in the stigmergic environment.
    
    Attributes:
        trace_type: Type of the trace
        position: Grid position (x, y) where trace is deposited
        intensity: Strength/intensity of the trace (0.0 to 1.0)
        metadata: Additional data associated with the trace
        timestamp: When the trace was created
        depositor_id: ID of the agent that deposited the trace
    """
    
    trace_type: TraceType
    position: Tuple[int, int]
    intensity: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    depositor_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate trace intensity."""
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(f"Trace intensity must be between 0.0 and 1.0, got {self.intensity}")


class StigmergicEnvironment:
    """Asynchronous stigmergic environment for agent coordination.
    
    This environment allows agents to deposit and sense traces for indirect
    coordination. Uses sparse storage by default for scalability, with optional
    Redis backend for distributed deployments.
    
    Args:
        grid_size: Size of the environment grid (grid_size x grid_size)
        decay_rate: Rate at which traces decay per second (0.0 to 1.0)
        density_threshold: Threshold for considering an area "dense" with traces
        backend: Storage backend ("memory" or "redis")
        redis_url: Redis connection URL (required if backend="redis")
        enable_background_decay: Whether to run automatic decay in background
    """
    
    def __init__(
        self,
        grid_size: int = 1000,
        decay_rate: float = 0.01,
        density_threshold: float = 0.5,
        backend: str = "memory",
        redis_url: Optional[str] = None,
        enable_background_decay: bool = False,
    ) -> None:
        """Initialize the stigmergic environment."""
        self.grid_size = grid_size
        self.decay_rate = decay_rate
        self.density_threshold = density_threshold
        self.backend = backend
        self.enable_background_decay = enable_background_decay
        
        # Sparse storage: Dict[(x, y), List[Trace]]
        self._traces: Dict[Tuple[int, int], List[Trace]] = {}
        self._redis_client: Optional[Any] = None
        self._decay_task: Optional[asyncio.Task[None]] = None
        self._lock = asyncio.Lock()
        
        # Initialize backend
        if backend == "redis":
            if not REDIS_AVAILABLE:
                raise ImportError(
                    "Redis backend requires 'redis' package. "
                    "Install it with: pip install redis"
                )
            
            redis_url = redis_url or os.getenv("REDIS_URL")
            if not redis_url:
                raise ValueError(
                    "Redis backend requires REDIS_URL environment variable or redis_url parameter"
                )
            
            # Note: Actual connection happens in async context
            self._redis_url = redis_url
        elif backend != "memory":
            raise ValueError(f"Unknown backend: {backend}. Use 'memory' or 'redis'")
    
    async def __aenter__(self) -> "StigmergicEnvironment":
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self) -> None:
        """Initialize the environment and connect to backend if needed."""
        if self.backend == "redis" and self._redis_client is None:
            self._redis_client = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        
        if self.enable_background_decay:
            self._decay_task = asyncio.create_task(self._background_decay_loop())
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._decay_task:
            self._decay_task.cancel()
            try:
                await self._decay_task
            except asyncio.CancelledError:
                pass
        
        if self._redis_client:
            await self._redis_client.close()
    
    async def deposit_trace(
        self,
        trace_type: TraceType,
        position: Tuple[int, int],
        intensity: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        depositor_id: Optional[str] = None,
    ) -> None:
        """Deposit a trace at the specified position.
        
        Args:
            trace_type: Type of trace to deposit
            position: Grid position (x, y)
            intensity: Trace intensity (0.0 to 1.0)
            metadata: Additional metadata
            depositor_id: ID of the depositing agent
        """
        x, y = position
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            raise ValueError(
                f"Position {position} out of bounds for grid size {self.grid_size}"
            )
        
        trace = Trace(
            trace_type=trace_type,
            position=position,
            intensity=intensity,
            metadata=metadata or {},
            depositor_id=depositor_id,
        )
        
        async with self._lock:
            if self.backend == "memory":
                if position not in self._traces:
                    self._traces[position] = []
                self._traces[position].append(trace)
            elif self.backend == "redis":
                # Store in Redis with key pattern: traces:{x}:{y}
                import json
                key = f"traces:{x}:{y}"
                trace_data = {
                    "trace_type": trace.trace_type.value,
                    "intensity": trace.intensity,
                    "metadata": trace.metadata,
                    "timestamp": trace.timestamp.isoformat(),
                    "depositor_id": trace.depositor_id,
                }
                await self._redis_client.lpush(key, json.dumps(trace_data))
    
    async def sense_traces(
        self,
        position: Tuple[int, int],
        radius: int = 1,
        trace_type: Optional[TraceType] = None,
    ) -> List[Trace]:
        """Sense traces within a radius of the specified position.
        
        Args:
            position: Center position to sense from
            radius: Sensing radius in grid cells
            trace_type: Optional filter by trace type
        
        Returns:
            List of traces within the sensing radius
        """
        x, y = position
        traces: List[Trace] = []
        
        async with self._lock:
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    px, py = x + dx, y + dy
                    if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                        pos = (px, py)
                        
                        if self.backend == "memory":
                            if pos in self._traces:
                                cell_traces = self._traces[pos]
                                if trace_type:
                                    cell_traces = [
                                        t for t in cell_traces if t.trace_type == trace_type
                                    ]
                                traces.extend(cell_traces)
                        elif self.backend == "redis":
                            # Retrieve from Redis
                            import json
                            key = f"traces:{px}:{py}"
                            raw_traces = await self._redis_client.lrange(key, 0, -1)
                            for raw in raw_traces:
                                data = json.loads(raw)
                                trace = Trace(
                                    trace_type=TraceType(data["trace_type"]),
                                    position=pos,
                                    intensity=data["intensity"],
                                    metadata=data["metadata"],
                                    timestamp=datetime.fromisoformat(data["timestamp"]),
                                    depositor_id=data.get("depositor_id"),
                                )
                                if trace_type is None or trace.trace_type == trace_type:
                                    traces.append(trace)
        
        return traces
    
    async def decay(self) -> None:
        """Apply decay to all traces in the environment."""
        async with self._lock:
            if self.backend == "memory":
                positions_to_remove = []
                for pos, traces in self._traces.items():
                    remaining_traces = []
                    for trace in traces:
                        trace.intensity *= (1.0 - self.decay_rate)
                        if trace.intensity > 0.01:  # Keep traces with intensity > 1%
                            remaining_traces.append(trace)
                    
                    if remaining_traces:
                        self._traces[pos] = remaining_traces
                    else:
                        positions_to_remove.append(pos)
                
                for pos in positions_to_remove:
                    del self._traces[pos]
            
            elif self.backend == "redis":
                # For Redis, we'd implement decay using Lua script or batch operations
                # Simplified implementation for now
                import json
                cursor = "0"
                while cursor != 0:
                    cursor, keys = await self._redis_client.scan(
                        cursor=cursor, match="traces:*", count=100
                    )
                    for key in keys:
                        raw_traces = await self._redis_client.lrange(key, 0, -1)
                        await self._redis_client.delete(key)
                        
                        for raw in raw_traces:
                            data = json.loads(raw)
                            data["intensity"] *= (1.0 - self.decay_rate)
                            if data["intensity"] > 0.01:
                                await self._redis_client.lpush(key, json.dumps(data))
    
    async def get_density(
        self,
        position: Tuple[int, int],
        radius: int = 5,
    ) -> float:
        """Calculate trace density in an area.
        
        Args:
            position: Center position
            radius: Radius to measure density
        
        Returns:
            Density value (0.0 to 1.0+)
        """
        traces = await self.sense_traces(position, radius)
        if not traces:
            return 0.0
        
        # Calculate density as sum of intensities normalized by area
        total_intensity = sum(t.intensity for t in traces)
        area = (2 * radius + 1) ** 2
        return total_intensity / area
    
    async def clear(self, position: Optional[Tuple[int, int]] = None) -> None:
        """Clear traces from the environment.
        
        Args:
            position: If specified, clear only this position. Otherwise, clear all.
        """
        async with self._lock:
            if self.backend == "memory":
                if position is not None:
                    self._traces.pop(position, None)
                else:
                    self._traces.clear()
            elif self.backend == "redis":
                if position is not None:
                    x, y = position
                    await self._redis_client.delete(f"traces:{x}:{y}")
                else:
                    # Clear all traces
                    cursor = "0"
                    while cursor != 0:
                        cursor, keys = await self._redis_client.scan(
                            cursor=cursor, match="traces:*", count=1000
                        )
                        if keys:
                            await self._redis_client.delete(*keys)
    
    async def _background_decay_loop(self) -> None:
        """Background task for automatic trace decay."""
        while True:
            await asyncio.sleep(1.0)  # Decay every second
            try:
                await self.decay()
            except Exception as e:
                # Log error but continue
                print(f"Error during background decay: {e}")
