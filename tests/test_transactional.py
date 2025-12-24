"""
Tests for transactional safety system.
"""

import pytest
import pytest_asyncio

from python.qbit.transaction import (
    TransactionalSafety,
    TransactionStatus,
)


@pytest_asyncio.fixture
async def transaction_system():
    """Create a test transaction system."""
    ts = TransactionalSafety(backend="memory")
    await ts.initialize()
    yield ts
    await ts.cleanup()


@pytest.mark.asyncio
async def test_begin_action(transaction_system):
    """Test beginning an action in a transaction."""
    await transaction_system.begin_action(
        transaction_id="tx_1",
        action_type="create_agent",
        action_data={"agent_id": "agent_1", "capabilities": {"compute": 0.8}},
    )
    
    transaction = await transaction_system.get_transaction("tx_1")
    assert transaction is not None
    assert transaction.transaction_id == "tx_1"
    assert len(transaction.actions) == 1
    assert transaction.actions[0]["action_type"] == "create_agent"
    assert transaction.status == TransactionStatus.PENDING


@pytest.mark.asyncio
async def test_commit_transaction(transaction_system):
    """Test committing a transaction."""
    # Begin transaction
    await transaction_system.begin_action(
        transaction_id="tx_2",
        action_type="update_state",
        action_data={"key": "value"},
    )
    
    # Commit
    await transaction_system.commit(
        transaction_id="tx_2",
        metadata={"reason": "test"},
    )
    
    # Verify status
    transaction = await transaction_system.get_transaction("tx_2")
    assert transaction.status == TransactionStatus.COMMITTED
    assert transaction.completed_at is not None
    assert transaction.metadata["reason"] == "test"


@pytest.mark.asyncio
async def test_rollback_transaction(transaction_system):
    """Test rolling back a transaction."""
    # Begin transaction
    await transaction_system.begin_action(
        transaction_id="tx_3",
        action_type="delete_agent",
        action_data={"agent_id": "agent_1"},
    )
    
    # Rollback
    await transaction_system.rollback(
        transaction_id="tx_3",
        reason="test rollback",
    )
    
    # Verify status
    transaction = await transaction_system.get_transaction("tx_3")
    assert transaction.status == TransactionStatus.ROLLED_BACK
    assert transaction.completed_at is not None
    assert transaction.metadata["rollback_reason"] == "test rollback"


@pytest.mark.asyncio
async def test_multiple_actions_in_transaction(transaction_system):
    """Test multiple actions in a single transaction."""
    # Begin multiple actions
    await transaction_system.begin_action(
        transaction_id="tx_4",
        action_type="action_1",
        action_data={"data": 1},
    )
    await transaction_system.begin_action(
        transaction_id="tx_4",
        action_type="action_2",
        action_data={"data": 2},
    )
    await transaction_system.begin_action(
        transaction_id="tx_4",
        action_type="action_3",
        action_data={"data": 3},
    )
    
    # Verify all actions are recorded
    transaction = await transaction_system.get_transaction("tx_4")
    assert len(transaction.actions) == 3
    assert transaction.actions[0]["action_type"] == "action_1"
    assert transaction.actions[1]["action_type"] == "action_2"
    assert transaction.actions[2]["action_type"] == "action_3"


@pytest.mark.asyncio
async def test_commit_already_completed(transaction_system):
    """Test that committing an already completed transaction fails."""
    # Begin and commit
    await transaction_system.begin_action(
        transaction_id="tx_5",
        action_type="test",
        action_data={},
    )
    await transaction_system.commit("tx_5")
    
    # Try to commit again
    with pytest.raises(ValueError, match="already committed"):
        await transaction_system.commit("tx_5")


@pytest.mark.asyncio
async def test_rollback_already_completed(transaction_system):
    """Test that rolling back an already completed transaction fails."""
    # Begin and rollback
    await transaction_system.begin_action(
        transaction_id="tx_6",
        action_type="test",
        action_data={},
    )
    await transaction_system.rollback("tx_6")
    
    # Try to rollback again
    with pytest.raises(ValueError, match="already rolled_back"):
        await transaction_system.rollback("tx_6")


@pytest.mark.asyncio
async def test_commit_nonexistent_transaction(transaction_system):
    """Test committing a non-existent transaction."""
    with pytest.raises(ValueError, match="not found"):
        await transaction_system.commit("nonexistent")


@pytest.mark.asyncio
async def test_rollback_nonexistent_transaction(transaction_system):
    """Test rolling back a non-existent transaction."""
    with pytest.raises(ValueError, match="not found"):
        await transaction_system.rollback("nonexistent")


@pytest.mark.asyncio
async def test_commit_hooks(transaction_system):
    """Test commit hooks are called."""
    hook_called = []
    
    def commit_hook(transaction):
        hook_called.append(transaction.transaction_id)
    
    transaction_system.register_commit_hook(commit_hook)
    
    # Begin and commit
    await transaction_system.begin_action(
        transaction_id="tx_7",
        action_type="test",
        action_data={},
    )
    await transaction_system.commit("tx_7")
    
    # Verify hook was called
    assert "tx_7" in hook_called


@pytest.mark.asyncio
async def test_rollback_hooks(transaction_system):
    """Test rollback hooks are called."""
    hook_called = []
    
    def rollback_hook(transaction):
        hook_called.append(transaction.transaction_id)
    
    transaction_system.register_rollback_hook(rollback_hook)
    
    # Begin and rollback
    await transaction_system.begin_action(
        transaction_id="tx_8",
        action_type="test",
        action_data={},
    )
    await transaction_system.rollback("tx_8")
    
    # Verify hook was called
    assert "tx_8" in hook_called


@pytest.mark.asyncio
async def test_async_commit_hooks(transaction_system):
    """Test async commit hooks are awaited."""
    hook_called = []
    
    async def async_commit_hook(transaction):
        # Simulate async operation
        import asyncio
        await asyncio.sleep(0.01)
        hook_called.append(transaction.transaction_id)
    
    transaction_system.register_commit_hook(async_commit_hook)
    
    # Begin and commit
    await transaction_system.begin_action(
        transaction_id="tx_9",
        action_type="test",
        action_data={},
    )
    await transaction_system.commit("tx_9")
    
    # Verify hook was called
    assert "tx_9" in hook_called


@pytest.mark.asyncio
async def test_get_stats(transaction_system):
    """Test getting transaction statistics."""
    # Create some transactions
    await transaction_system.begin_action("tx_10", "test", {})
    await transaction_system.begin_action("tx_11", "test", {})
    await transaction_system.commit("tx_10")
    await transaction_system.begin_action("tx_12", "test", {})
    await transaction_system.rollback("tx_12")
    
    # Get stats
    stats = await transaction_system.get_stats()
    
    assert stats["total_transactions"] == 3
    assert stats["status_counts"]["committed"] == 1
    assert stats["status_counts"]["rolled_back"] == 1
    assert stats["status_counts"]["pending"] == 1


@pytest.mark.asyncio
async def test_transaction_metadata(transaction_system):
    """Test transaction metadata handling."""
    await transaction_system.begin_action(
        transaction_id="tx_13",
        action_type="test",
        action_data={"key": "value"},
    )
    
    # Add metadata on commit
    await transaction_system.commit(
        transaction_id="tx_13",
        metadata={"commit_reason": "test", "user": "test_user"},
    )
    
    transaction = await transaction_system.get_transaction("tx_13")
    assert transaction.metadata["commit_reason"] == "test"
    assert transaction.metadata["user"] == "test_user"
