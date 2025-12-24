"""
Tests for topology router with async coordinators.
"""

import pytest
import pytest_asyncio

from python.qbit.coordinators import Task
from python.qbit.topology import Config, TopologyRouter


@pytest.fixture
def router():
    """Create a test topology router."""
    config = Config(
        centralized_threshold=10,
        hierarchical_threshold=50,
        parallelism_threshold=0.6,
    )
    return TopologyRouter(config=config)


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    tasks = []
    for i in range(20):
        task = Task(
            task_id=f"task_{i}",
            task_type=f"type_{i % 3}",
            priority=i % 5,
            requirements={"compute": 0.5, "memory": 0.6},
        )
        tasks.append(task)
    return tasks


def test_analyze_parallelism_empty(router):
    """Test parallelism analysis with empty task list."""
    features = router.analyze_parallelism([])
    
    assert features["task_count"] == 0
    assert features["parallel_score"] == 0.0
    assert features["avg_priority"] == 0.0


def test_analyze_parallelism_features(router, sample_tasks):
    """Test that parallelism analysis extracts correct features."""
    features = router.analyze_parallelism(sample_tasks)
    
    assert features["task_count"] == 20
    assert "parallel_score" in features
    assert 0.0 <= features["parallel_score"] <= 1.0
    assert "avg_priority" in features
    assert "unique_types" in features
    assert features["unique_types"] == 3  # type_0, type_1, type_2
    assert "resource_diversity" in features


def test_route_centralized(router):
    """Test routing to centralized coordinator."""
    # Small batch should route to centralized
    tasks = [
        Task(task_id=f"task_{i}", task_type="test", priority=1)
        for i in range(5)
    ]
    
    coordinator_type = router.route(tasks)
    assert coordinator_type == "centralized"


def test_route_hierarchical(router):
    """Test routing to hierarchical coordinator."""
    # Medium batch with low parallelism should route to hierarchical
    tasks = [
        Task(task_id=f"task_{i}", task_type="test", priority=i * 10)
        for i in range(30)
    ]
    
    coordinator_type = router.route(tasks)
    # With high priority variance, parallel_score will be low
    assert coordinator_type in ["hierarchical", "centralized"]


def test_route_independent(router):
    """Test routing to independent coordinator."""
    # Large batch with high parallelism should route to independent
    tasks = [
        Task(
            task_id=f"task_{i}",
            task_type=f"type_{i}",  # High diversity
            priority=1,  # Low variance
            requirements={f"resource_{i}": 0.5},  # High resource diversity
        )
        for i in range(60)
    ]
    
    coordinator_type = router.route(tasks)
    assert coordinator_type == "independent"


def test_get_coordinator(router):
    """Test getting coordinator instances."""
    centralized = router.get_coordinator("centralized")
    assert centralized is not None
    
    hierarchical = router.get_coordinator("hierarchical")
    assert hierarchical is not None
    
    independent = router.get_coordinator("independent")
    assert independent is not None
    
    with pytest.raises(ValueError):
        router.get_coordinator("invalid")


@pytest.mark.asyncio
async def test_centralized_coordinator_flow(router):
    """Test full flow with centralized coordinator."""
    coordinator = router.get_coordinator("centralized")
    
    # Register an agent
    await coordinator.register_agent(
        agent_id="agent_1",
        capabilities={"compute": 0.8, "memory": 0.9},
    )
    
    # Submit a task
    task = Task(
        task_id="task_1",
        task_type="test",
        requirements={"compute": 0.5},
    )
    await coordinator.submit_task(task)
    
    # Assign task to agent
    assigned = await coordinator.assign_best("agent_1")
    assert assigned is not None
    assert assigned.task_id == "task_1"
    
    # Complete task
    await coordinator.complete_task("task_1", success=True)
    
    # Check stats
    stats = await coordinator.get_stats()
    assert stats["pending_tasks"] == 0
    assert stats["assigned_tasks"] == 0


@pytest.mark.asyncio
async def test_hierarchical_coordinator_flow(router):
    """Test full flow with hierarchical coordinator."""
    coordinator = router.get_coordinator("hierarchical")
    
    # Register agents
    for i in range(4):
        await coordinator.register_agent(
            agent_id=f"agent_{i}",
            capabilities={"compute": 0.8},
        )
    
    # Distribute tasks
    tasks = [
        Task(task_id=f"task_{i}", task_type="test", requirements={"compute": 0.5})
        for i in range(8)
    ]
    await coordinator.distribute(tasks)
    
    # Agents can get tasks
    assigned = await coordinator.assign_best("agent_0")
    assert assigned is not None
    
    # Complete task
    await coordinator.complete_task(assigned.task_id, "agent_0", success=True)
    
    # Check stats
    stats = await coordinator.get_stats()
    assert stats["num_clusters"] == 4


@pytest.mark.asyncio
async def test_independent_coordinator_flow(router):
    """Test full flow with independent coordinator."""
    coordinator = router.get_coordinator("independent")
    
    # Submit tasks
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            task_type="test",
            requirements={"compute": 0.5},
        )
        await coordinator.submit_task(task)
    
    # Agent claims task
    assigned = await coordinator.assign_best(
        agent_id="agent_1",
        capabilities={"compute": 0.8},
    )
    assert assigned is not None
    
    # Complete task
    await coordinator.complete_task(assigned.task_id, success=True)
    
    # Check stats
    stats = await coordinator.get_stats()
    assert stats["pool_size"] == 4  # 5 submitted, 1 claimed


def test_auto_tuning_stats(router, sample_tasks):
    """Test auto-tuning statistics collection."""
    # Analyze multiple batches
    for _ in range(3):
        router.analyze_parallelism(sample_tasks)
    
    stats = router.get_auto_tuning_stats()
    assert stats["count"] == 3
    assert "mean" in stats
    assert "min" in stats
    assert "max" in stats
    assert "histogram" in stats


def test_parallel_score_calculation(router):
    """Test parallel score is correctly calculated."""
    # High parallelism: diverse types, low priority variance
    high_parallel_tasks = [
        Task(
            task_id=f"task_{i}",
            task_type=f"type_{i}",
            priority=1,
            requirements={f"res_{i}": 0.5},
        )
        for i in range(10)
    ]
    
    features_high = router.analyze_parallelism(high_parallel_tasks)
    
    # Low parallelism: same type, high priority variance
    low_parallel_tasks = [
        Task(
            task_id=f"task_{i}",
            task_type="same_type",
            priority=i * 100,
            requirements={"same_res": 0.5},
        )
        for i in range(10)
    ]
    
    features_low = router.analyze_parallelism(low_parallel_tasks)
    
    # High parallelism should have higher score
    assert features_high["parallel_score"] > features_low["parallel_score"]


@pytest.mark.asyncio
async def test_task_priority_ordering(router):
    """Test that higher priority tasks are assigned first."""
    coordinator = router.get_coordinator("centralized")
    
    # Register agent
    await coordinator.register_agent(
        agent_id="agent_1",
        capabilities={"compute": 1.0},
    )
    
    # Submit tasks with different priorities
    await coordinator.submit_task(
        Task(task_id="low", task_type="test", priority=1, requirements={"compute": 0.5})
    )
    await coordinator.submit_task(
        Task(task_id="high", task_type="test", priority=10, requirements={"compute": 0.5})
    )
    await coordinator.submit_task(
        Task(task_id="medium", task_type="test", priority=5, requirements={"compute": 0.5})
    )
    
    # First assignment should be highest priority
    assigned = await coordinator.assign_best("agent_1")
    assert assigned.task_id == "high"
