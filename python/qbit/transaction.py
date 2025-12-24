"""
Transactional safety for Q-BIT operations.

Provides begin/commit/rollback semantics with pluggable backends
for distributed consistency.
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class TransactionStatus(Enum):
    """Status of a transaction."""
    
    PENDING = "pending"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class TransactionLog:
    """Log entry for a transaction.
    
    Attributes:
        transaction_id: Unique transaction identifier
        actions: List of actions performed in this transaction
        status: Current transaction status
        created_at: Transaction creation time
        completed_at: Transaction completion time
        metadata: Additional transaction metadata
    """
    
    transaction_id: str
    actions: List[Dict[str, Any]] = field(default_factory=list)
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TransactionalSafety:
    """Provides transactional guarantees for agent operations.
    
    Supports begin/commit/rollback semantics with optional persistence
    to Redis for distributed consistency.
    
    Args:
        backend: Storage backend ("memory" or "redis")
        redis_url: Redis connection URL (required if backend="redis")
        enable_hooks: Whether to enable commit/rollback hooks
    """
    
    def __init__(
        self,
        backend: str = "memory",
        redis_url: Optional[str] = None,
        enable_hooks: bool = True,
    ) -> None:
        """Initialize transactional safety system."""
        self.backend = backend
        self.enable_hooks = enable_hooks
        
        # In-memory storage
        self._transactions: Dict[str, TransactionLog] = {}
        self._active_transaction: Optional[str] = None
        self._lock = asyncio.Lock()
        
        # Redis backend
        self._redis_client: Optional[Any] = None
        
        # Hooks for custom persistence
        self._commit_hooks: List[Callable[[TransactionLog], Any]] = []
        self._rollback_hooks: List[Callable[[TransactionLog], Any]] = []
        
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
            
            self._redis_url = redis_url
        elif backend != "memory":
            raise ValueError(f"Unknown backend: {backend}. Use 'memory' or 'redis'")
    
    async def __aenter__(self) -> "TransactionalSafety":
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    async def initialize(self) -> None:
        """Initialize the transactional system and connect to backend."""
        if self.backend == "redis" and self._redis_client is None:
            self._redis_client = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._redis_client:
            await self._redis_client.close()
    
    async def begin_action(
        self,
        transaction_id: str,
        action_type: str,
        action_data: Dict[str, Any],
    ) -> None:
        """Begin a new action within a transaction.
        
        Args:
            transaction_id: Unique transaction identifier
            action_type: Type of action being performed
            action_data: Data associated with the action
        """
        async with self._lock:
            # Create transaction if it doesn't exist
            if transaction_id not in self._transactions:
                self._transactions[transaction_id] = TransactionLog(
                    transaction_id=transaction_id,
                )
                self._active_transaction = transaction_id
            
            # Add action to transaction log
            transaction = self._transactions[transaction_id]
            transaction.actions.append({
                "action_type": action_type,
                "action_data": action_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            
            # Persist to Redis if using Redis backend
            if self.backend == "redis":
                await self._persist_transaction_redis(transaction)
    
    async def commit(
        self,
        transaction_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Commit a transaction.
        
        Args:
            transaction_id: ID of transaction to commit
            metadata: Optional metadata to attach to the commit
        
        Raises:
            ValueError: If transaction not found or already completed
        """
        async with self._lock:
            if transaction_id not in self._transactions:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            transaction = self._transactions[transaction_id]
            
            if transaction.status != TransactionStatus.PENDING:
                raise ValueError(
                    f"Transaction {transaction_id} already {transaction.status.value}"
                )
            
            # Update transaction status
            transaction.status = TransactionStatus.COMMITTED
            transaction.completed_at = datetime.now(timezone.utc)
            if metadata:
                transaction.metadata.update(metadata)
            
            # Persist to Redis if using Redis backend
            if self.backend == "redis":
                await self._persist_transaction_redis(transaction)
            
            # Execute commit hooks
            if self.enable_hooks:
                for hook in self._commit_hooks:
                    try:
                        result = hook(transaction)
                        # Handle async hooks
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        # Log but don't fail commit
                        print(f"Commit hook error: {e}")
            
            # Clear active transaction if this was it
            if self._active_transaction == transaction_id:
                self._active_transaction = None
    
    async def rollback(
        self,
        transaction_id: str,
        reason: Optional[str] = None,
    ) -> None:
        """Rollback a transaction.
        
        Args:
            transaction_id: ID of transaction to rollback
            reason: Optional reason for rollback
        
        Raises:
            ValueError: If transaction not found or already completed
        """
        async with self._lock:
            if transaction_id not in self._transactions:
                raise ValueError(f"Transaction not found: {transaction_id}")
            
            transaction = self._transactions[transaction_id]
            
            if transaction.status != TransactionStatus.PENDING:
                raise ValueError(
                    f"Transaction {transaction_id} already {transaction.status.value}"
                )
            
            # Update transaction status
            transaction.status = TransactionStatus.ROLLED_BACK
            transaction.completed_at = datetime.now(timezone.utc)
            if reason:
                transaction.metadata["rollback_reason"] = reason
            
            # Persist to Redis if using Redis backend
            if self.backend == "redis":
                await self._persist_transaction_redis(transaction)
            
            # Execute rollback hooks
            if self.enable_hooks:
                for hook in self._rollback_hooks:
                    try:
                        result = hook(transaction)
                        # Handle async hooks
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as e:
                        # Log but don't fail rollback
                        print(f"Rollback hook error: {e}")
            
            # Clear active transaction if this was it
            if self._active_transaction == transaction_id:
                self._active_transaction = None
    
    def register_commit_hook(
        self,
        hook: Callable[[TransactionLog], Any],
    ) -> None:
        """Register a hook to be called on commit.
        
        Args:
            hook: Function to call on commit (can be sync or async)
        """
        self._commit_hooks.append(hook)
    
    def register_rollback_hook(
        self,
        hook: Callable[[TransactionLog], Any],
    ) -> None:
        """Register a hook to be called on rollback.
        
        Args:
            hook: Function to call on rollback (can be sync or async)
        """
        self._rollback_hooks.append(hook)
    
    async def get_transaction(
        self,
        transaction_id: str,
    ) -> Optional[TransactionLog]:
        """Get transaction log by ID.
        
        Args:
            transaction_id: ID of the transaction
        
        Returns:
            TransactionLog if found, None otherwise
        """
        async with self._lock:
            return self._transactions.get(transaction_id)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get transaction statistics.
        
        Returns:
            Statistics about transactions
        """
        async with self._lock:
            status_counts = {
                TransactionStatus.PENDING: 0,
                TransactionStatus.COMMITTED: 0,
                TransactionStatus.ROLLED_BACK: 0,
                TransactionStatus.FAILED: 0,
            }
            
            for transaction in self._transactions.values():
                status_counts[transaction.status] += 1
            
            return {
                "total_transactions": len(self._transactions),
                "active_transaction": self._active_transaction,
                "status_counts": {
                    status.value: count
                    for status, count in status_counts.items()
                },
            }
    
    async def _persist_transaction_redis(
        self,
        transaction: TransactionLog,
    ) -> None:
        """Persist transaction to Redis.
        
        Args:
            transaction: Transaction to persist
        """
        import json
        
        key = f"transaction:{transaction.transaction_id}"
        data = {
            "transaction_id": transaction.transaction_id,
            "actions": transaction.actions,
            "status": transaction.status.value,
            "created_at": transaction.created_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "metadata": transaction.metadata,
        }
        
        await self._redis_client.set(key, json.dumps(data))
        
        # Set expiration for completed transactions (24 hours)
        if transaction.status in (TransactionStatus.COMMITTED, TransactionStatus.ROLLED_BACK):
            await self._redis_client.expire(key, 86400)
