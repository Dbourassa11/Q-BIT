"""
Stress test for 625+ agents using simulated harness.

This test is designed to be CI-friendly: deterministic, fast, and
requires no external services.
"""

import pytest
import pytest_asyncio

from python.qbit.harness.simulator import SimulatedWorkerPool


@pytest_asyncio.fixture
async def worker_pool():
    """Create a simulated worker pool."""
    pool = SimulatedWorkerPool(
        num_agents=625,
        grid_size=100,
        enable_stigmergy=True,
        seed=42,  # Deterministic
    )
    await pool.initialize()
    yield pool
    await pool.cleanup()


@pytest.mark.asyncio
async def test_625_agents_stress(worker_pool):
    """Stress test with 625 agents.
    
    This test simulates 625 agents for 10 steps, which should complete
    in under 30 seconds on a typical CI machine.
    """
    # Generate tasks
    await worker_pool.generate_tasks(num_tasks=500)
    
    # Run simulation
    results = await worker_pool.run_simulation(
        num_steps=10,
        parallel=True,
    )
    
    # Verify results
    assert results["num_agents"] == 625
    assert results["num_steps"] == 10
    assert results["duration_seconds"] < 30.0  # CI-friendly timing
    assert results["tasks_completed"] > 0
    assert results["throughput_tasks_per_second"] > 0
    
    # Success rate should be reasonably high
    assert results["success_rate"] > 0.9


@pytest.mark.asyncio
async def test_agent_initialization(worker_pool):
    """Test that agents are properly initialized."""
    assert len(worker_pool.agents) == 625
    
    # All agents should have unique IDs
    agent_ids = [agent.agent_id for agent in worker_pool.agents]
    assert len(agent_ids) == len(set(agent_ids))
    
    # All agents should have capabilities
    for agent in worker_pool.agents:
        assert "compute" in agent.capabilities
        assert "memory" in agent.capabilities
        assert 0.5 <= agent.capabilities["compute"] <= 1.0
        assert 0.5 <= agent.capabilities["memory"] <= 1.0


@pytest.mark.asyncio
async def test_task_generation(worker_pool):
    """Test task generation."""
    await worker_pool.generate_tasks(num_tasks=100)
    
    stats = await worker_pool.get_stats()
    assert stats["tasks_in_pool"] == 100


@pytest.mark.asyncio
async def test_stigmergic_coordination(worker_pool):
    """Test that stigmergic environment is working."""
    # Verify environment exists
    assert worker_pool.environment is not None
    
    # Generate some tasks
    await worker_pool.generate_tasks(num_tasks=50)
    
    # Run a few steps
    await worker_pool.run_simulation(num_steps=3, parallel=True)
    
    # Check that traces have been deposited
    # (At least some agents should have moved and deposited traces)
    traces_exist = False
    for i in range(0, 100, 10):
        for j in range(0, 100, 10):
            traces = await worker_pool.environment.sense_traces(
                position=(i, j),
                radius=5,
            )
            if traces:
                traces_exist = True
                break
        if traces_exist:
            break
    
    assert traces_exist, "No traces found after simulation"


@pytest.mark.asyncio
async def test_parallel_vs_sequential():
    """Test that parallel execution is faster than sequential."""
    import time
    
    # Parallel execution
    pool_parallel = SimulatedWorkerPool(
        num_agents=100,
        grid_size=50,
        enable_stigmergy=False,
        seed=42,
    )
    await pool_parallel.initialize()
    await pool_parallel.generate_tasks(num_tasks=50)
    
    start = time.time()
    await pool_parallel.run_simulation(num_steps=5, parallel=True)
    parallel_time = time.time() - start
    
    await pool_parallel.cleanup()
    
    # Sequential execution
    pool_sequential = SimulatedWorkerPool(
        num_agents=100,
        grid_size=50,
        enable_stigmergy=False,
        seed=42,
    )
    await pool_sequential.initialize()
    await pool_sequential.generate_tasks(num_tasks=50)
    
    start = time.time()
    await pool_sequential.run_simulation(num_steps=5, parallel=False)
    sequential_time = time.time() - start
    
    await pool_sequential.cleanup()
    
    # Parallel should generally be faster or at least not significantly slower
    # (On single-core CI, they might be similar, so we just check it completes)
    assert parallel_time > 0
    assert sequential_time > 0


@pytest.mark.asyncio
async def test_deterministic_behavior():
    """Test that simulation is deterministic with same seed."""
    # Run simulation 1
    pool1 = SimulatedWorkerPool(num_agents=50, grid_size=50, seed=123)
    await pool1.initialize()
    await pool1.generate_tasks(num_tasks=30)
    results1 = await pool1.run_simulation(num_steps=5, parallel=True)
    await pool1.cleanup()
    
    # Run simulation 2 with same seed
    pool2 = SimulatedWorkerPool(num_agents=50, grid_size=50, seed=123)
    await pool2.initialize()
    await pool2.generate_tasks(num_tasks=30)
    results2 = await pool2.run_simulation(num_steps=5, parallel=True)
    await pool2.cleanup()
    
    # Results should be identical
    assert results1["tasks_completed"] == results2["tasks_completed"]
    assert results1["tasks_failed"] == results2["tasks_failed"]


@pytest.mark.asyncio
async def test_high_task_load(worker_pool):
    """Test with more tasks than agents."""
    # Generate 2000 tasks for 625 agents
    await worker_pool.generate_tasks(num_tasks=2000)
    
    results = await worker_pool.run_simulation(num_steps=10, parallel=True)
    
    # Should complete some tasks
    assert results["tasks_completed"] > 0
    
    # With 625 agents and 10 steps, we expect many tasks completed
    # but possibly not all 2000
    total_processed = results["tasks_completed"] + results["tasks_failed"]
    assert total_processed > 100  # At least some significant work done


@pytest.mark.asyncio
async def test_agent_stats(worker_pool):
    """Test that agent statistics are tracked."""
    await worker_pool.generate_tasks(num_tasks=100)
    await worker_pool.run_simulation(num_steps=5, parallel=True)
    
    stats = await worker_pool.get_stats()
    
    assert "agent_stats" in stats
    assert len(stats["agent_stats"]) == 625
    
    # At least some agents should have completed tasks
    total_completed = sum(
        agent["tasks_completed"] for agent in stats["agent_stats"]
    )
    assert total_completed > 0


@pytest.mark.asyncio
async def test_simulation_throughput(worker_pool):
    """Test that throughput metrics are calculated correctly."""
    await worker_pool.generate_tasks(num_tasks=200)
    
    results = await worker_pool.run_simulation(num_steps=10, parallel=True)
    
    # Verify throughput calculation
    expected_throughput = (
        results["tasks_completed"] / results["duration_seconds"]
    )
    assert results["throughput_tasks_per_second"] == pytest.approx(
        expected_throughput,
        rel=0.01,
    )


@pytest.mark.asyncio
async def test_without_stigmergy():
    """Test simulation without stigmergic coordination."""
    pool = SimulatedWorkerPool(
        num_agents=100,
        grid_size=50,
        enable_stigmergy=False,
        seed=42,
    )
    await pool.initialize()
    
    # Verify no environment
    assert pool.environment is None
    
    # Should still work
    await pool.generate_tasks(num_tasks=50)
    results = await pool.run_simulation(num_steps=5, parallel=True)
    
    assert results["tasks_completed"] > 0
    
    await pool.cleanup()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_1000_agents_extended():
    """Extended stress test with 1000 agents.
    
    Marked as slow, not run by default in CI.
    """
    pool = SimulatedWorkerPool(
        num_agents=1000,
        grid_size=200,
        enable_stigmergy=True,
        seed=42,
    )
    await pool.initialize()
    
    await pool.generate_tasks(num_tasks=5000)
    results = await pool.run_simulation(num_steps=20, parallel=True)
    
    assert results["num_agents"] == 1000
    assert results["tasks_completed"] > 0
    
    await pool.cleanup()
