"""
Tests for async stigmergic coordination layer.
"""

import pytest
import pytest_asyncio

from python.qbit.stigmergy import (
    StigmergicEnvironment,
    Trace,
    TraceType,
)


@pytest_asyncio.fixture
async def environment():
    """Create a test stigmergic environment."""
    env = StigmergicEnvironment(
        grid_size=100,
        decay_rate=0.1,
        enable_background_decay=False,
    )
    await env.initialize()
    yield env
    await env.cleanup()


@pytest.mark.asyncio
async def test_deposit_trace(environment):
    """Test depositing a trace."""
    await environment.deposit_trace(
        trace_type=TraceType.TASK_COMPLETE,
        position=(10, 20),
        intensity=0.8,
        depositor_id="agent_1",
    )
    
    traces = await environment.sense_traces(position=(10, 20), radius=0)
    assert len(traces) == 1
    assert traces[0].trace_type == TraceType.TASK_COMPLETE
    assert traces[0].position == (10, 20)
    assert traces[0].intensity == 0.8
    assert traces[0].depositor_id == "agent_1"


@pytest.mark.asyncio
async def test_sense_traces_with_radius(environment):
    """Test sensing traces within a radius."""
    # Deposit traces at different positions
    await environment.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=(50, 50),
        intensity=1.0,
    )
    await environment.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=(51, 50),
        intensity=0.9,
    )
    await environment.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=(50, 51),
        intensity=0.8,
    )
    
    # Sense from center
    traces = await environment.sense_traces(position=(50, 50), radius=1)
    assert len(traces) == 3
    
    # Sense with radius 0
    traces = await environment.sense_traces(position=(50, 50), radius=0)
    assert len(traces) == 1


@pytest.mark.asyncio
async def test_trace_decay(environment):
    """Test trace decay."""
    await environment.deposit_trace(
        trace_type=TraceType.TASK_COMPLETE,
        position=(30, 30),
        intensity=1.0,
    )
    
    # Check initial intensity
    traces = await environment.sense_traces(position=(30, 30), radius=0)
    assert len(traces) == 1
    assert traces[0].intensity == 1.0
    
    # Apply decay
    await environment.decay()
    
    # Check decayed intensity
    traces = await environment.sense_traces(position=(30, 30), radius=0)
    assert len(traces) == 1
    # With decay_rate=0.1, intensity should be 0.9
    assert traces[0].intensity == pytest.approx(0.9, rel=0.01)


@pytest.mark.asyncio
async def test_trace_removal_after_decay(environment):
    """Test that very weak traces are removed."""
    await environment.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=(40, 40),
        intensity=0.015,  # Very weak trace
    )
    
    # Apply decay multiple times
    for _ in range(5):  # More iterations to ensure removal
        await environment.decay()
    
    # Trace should be removed (intensity < 0.01)
    traces = await environment.sense_traces(position=(40, 40), radius=0)
    assert len(traces) == 0


@pytest.mark.asyncio
async def test_get_density(environment):
    """Test density calculation."""
    # Deposit multiple traces in an area
    for i in range(5):
        for j in range(5):
            await environment.deposit_trace(
                trace_type=TraceType.AGENT_PATH,
                position=(60 + i, 60 + j),
                intensity=0.5,
            )
    
    # Check density at center
    density = await environment.get_density(position=(62, 62), radius=2)
    assert density > 0.0


@pytest.mark.asyncio
async def test_clear_position(environment):
    """Test clearing traces at a specific position."""
    await environment.deposit_trace(
        trace_type=TraceType.TASK_COMPLETE,
        position=(70, 70),
        intensity=1.0,
    )
    
    # Verify trace exists
    traces = await environment.sense_traces(position=(70, 70), radius=0)
    assert len(traces) == 1
    
    # Clear position
    await environment.clear(position=(70, 70))
    
    # Verify trace is gone
    traces = await environment.sense_traces(position=(70, 70), radius=0)
    assert len(traces) == 0


@pytest.mark.asyncio
async def test_clear_all(environment):
    """Test clearing all traces."""
    # Deposit traces at multiple positions
    for i in range(10):
        await environment.deposit_trace(
            trace_type=TraceType.AGENT_PATH,
            position=(i * 10, i * 10),
            intensity=1.0,
        )
    
    # Clear all
    await environment.clear()
    
    # Verify all traces are gone
    for i in range(10):
        traces = await environment.sense_traces(position=(i * 10, i * 10), radius=0)
        assert len(traces) == 0


@pytest.mark.asyncio
async def test_trace_type_filtering(environment):
    """Test filtering traces by type."""
    # Deposit different types of traces at same position
    await environment.deposit_trace(
        trace_type=TraceType.TASK_COMPLETE,
        position=(80, 80),
        intensity=1.0,
    )
    await environment.deposit_trace(
        trace_type=TraceType.AGENT_PATH,
        position=(80, 80),
        intensity=0.9,
    )
    
    # Sense all traces
    all_traces = await environment.sense_traces(position=(80, 80), radius=0)
    assert len(all_traces) == 2
    
    # Sense only TASK_COMPLETE traces
    task_traces = await environment.sense_traces(
        position=(80, 80),
        radius=0,
        trace_type=TraceType.TASK_COMPLETE,
    )
    assert len(task_traces) == 1
    assert task_traces[0].trace_type == TraceType.TASK_COMPLETE


@pytest.mark.asyncio
async def test_trace_validation():
    """Test trace intensity validation."""
    with pytest.raises(ValueError):
        Trace(
            trace_type=TraceType.AGENT_PATH,
            position=(0, 0),
            intensity=1.5,  # Invalid: > 1.0
        )
    
    with pytest.raises(ValueError):
        Trace(
            trace_type=TraceType.AGENT_PATH,
            position=(0, 0),
            intensity=-0.1,  # Invalid: < 0.0
        )


@pytest.mark.asyncio
async def test_position_bounds(environment):
    """Test that depositing outside bounds raises error."""
    with pytest.raises(ValueError):
        await environment.deposit_trace(
            trace_type=TraceType.AGENT_PATH,
            position=(200, 200),  # Outside grid_size=100
            intensity=1.0,
        )
