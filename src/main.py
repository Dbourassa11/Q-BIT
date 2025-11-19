"""
Q-BIT Main Entry Point

Main application entry point for the Q-BIT omni agent and swarm intelligence system.
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import structlog
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.core.agent import AgentConfig, AgentCapability
from src.swarm.coordinator import SwarmCoordinator, SwarmStrategy
from src.agents.code_reviewer import CodeReviewerAgent
from src.agents.debugger import DebuggerAgent
from src.agents.architect import ArchitectAgent
from src.agents.tester import TesterAgent
from src.agents.documenter import DocumenterAgent

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
console = Console()

app = typer.Typer(
    name="qbit",
    help="Q-BIT: Advanced Omni Agent & Swarm Intelligence Hub",
    rich_markup_mode="rich"
)


class QBitSystem:
    """Main Q-BIT system orchestrator."""
    
    def __init__(self):
        """Initialize the Q-BIT system."""
        self.coordinator: Optional[SwarmCoordinator] = None
        self.agents = []
        self.running = False
        self.shutdown_event = asyncio.Event()
        
    async def initialize(self, strategy: SwarmStrategy = SwarmStrategy.ADAPTIVE) -> None:
        """Initialize the Q-BIT system."""
        console.print(Panel.fit(
            Text("🚀 Q-BIT: Advanced Omni Agent & Swarm Intelligence Hub", style="bold blue"),
            border_style="blue"
        ))
        
        logger.info("Initializing Q-BIT system")
        
        # Initialize swarm coordinator
        self.coordinator = SwarmCoordinator(strategy=strategy)
        
        # Create and register specialized agents
        await self._create_agents()
        
        logger.info("Q-BIT system initialized successfully")
        console.print("✅ System initialized successfully", style="green")
    
    async def _create_agents(self) -> None:
        """Create and register specialized agents."""
        console.print("🤖 Creating specialized agents...", style="yellow")
        
        # Code Reviewer Agent
        reviewer_config = AgentConfig(
            name="CodeReviewer",
            description="Advanced code review and quality analysis agent",
            capabilities={
                AgentCapability.CODE_REVIEW,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.QUALITY
            },
            max_concurrent_tasks=3
        )
        reviewer_agent = CodeReviewerAgent(reviewer_config)
        await reviewer_agent.initialize()
        await self.coordinator.register_agent(reviewer_agent)
        self.agents.append(reviewer_agent)
        console.print("  ✓ Code Reviewer Agent created", style="green")
        
        # Debugger Agent
        debugger_config = AgentConfig(
            name="Debugger",
            description="Intelligent debugging and error analysis agent",
            capabilities={
                AgentCapability.DEBUGGING,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.TESTING
            },
            max_concurrent_tasks=2
        )
        debugger_agent = DebuggerAgent(debugger_config)
        await debugger_agent.initialize()
        await self.coordinator.register_agent(debugger_agent)
        self.agents.append(debugger_agent)
        console.print("  ✓ Debugger Agent created", style="green")
        
        # Architect Agent
        architect_config = AgentConfig(
            name="Architect",
            description="System architecture and design agent",
            capabilities={
                AgentCapability.ARCHITECTURE,
                AgentCapability.CODE_GENERATION,
                AgentCapability.OPTIMIZATION
            },
            max_concurrent_tasks=2
        )
        architect_agent = ArchitectAgent(architect_config)
        await architect_agent.initialize()
        await self.coordinator.register_agent(architect_agent)
        self.agents.append(architect_agent)
        console.print("  ✓ Architect Agent created", style="green")
        
        # Tester Agent
        tester_config = AgentConfig(
            name="Tester",
            description="Automated testing and quality assurance agent",
            capabilities={
                AgentCapability.TESTING,
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_ANALYSIS
            },
            max_concurrent_tasks=3
        )
        tester_agent = TesterAgent(tester_config)
        await tester_agent.initialize()
        await self.coordinator.register_agent(tester_agent)
        self.agents.append(tester_agent)
        console.print("  ✓ Tester Agent created", style="green")
        
        # Documenter Agent
        documenter_config = AgentConfig(
            name="Documenter",
            description="Documentation generation and maintenance agent",
            capabilities={
                AgentCapability.DOCUMENTATION,
                AgentCapability.CODE_ANALYSIS
            },
            max_concurrent_tasks=2
        )
        documenter_agent = DocumenterAgent(documenter_config)
        await documenter_agent.initialize()
        await self.coordinator.register_agent(documenter_agent)
        self.agents.append(documenter_agent)
        console.print("  ✓ Documenter Agent created", style="green")
        
        console.print(f"🎉 Created {len(self.agents)} specialized agents", style="bold green")
    
    async def start(self) -> None:
        """Start the Q-BIT system."""
        if self.running:
            return
        
        console.print("🚀 Starting Q-BIT system...", style="yellow")
        self.running = True
        
        # Start all agents
        agent_tasks = []
        for agent in self.agents:
            task = asyncio.create_task(agent.start())
            agent_tasks.append(task)
        
        # Start coordinator
        coordinator_task = asyncio.create_task(self.coordinator.start())
        
        # Start system monitor
        monitor_task = asyncio.create_task(self._system_monitor())
        
        console.print("✅ Q-BIT system started successfully", style="bold green")
        console.print("🔍 System monitoring active", style="blue")
        
        # Wait for shutdown signal
        try:
            await asyncio.gather(
                coordinator_task,
                monitor_task,
                *agent_tasks
            )
        except KeyboardInterrupt:
            console.print("\n🛑 Shutdown signal received", style="yellow")
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the Q-BIT system gracefully."""
        if not self.running:
            return
        
        console.print("🛑 Stopping Q-BIT system...", style="yellow")
        self.running = False
        self.shutdown_event.set()
        
        # Stop coordinator
        if self.coordinator:
            await self.coordinator.stop()
        
        # Stop all agents
        for agent in self.agents:
            await agent.stop()
        
        console.print("✅ Q-BIT system stopped gracefully", style="green")
    
    async def _system_monitor(self) -> None:
        """Monitor system health and performance."""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Get system status
                if self.coordinator:
                    status = await self.coordinator.get_swarm_status()
                    
                    # Log system metrics
                    logger.info(
                        "System status",
                        total_agents=status["total_agents"],
                        active_tasks=status["active_tasks"],
                        queue_size=status["queue_size"]
                    )
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error("System monitor error", error=str(e))
                await asyncio.sleep(10)
    
    async def get_status(self) -> dict:
        """Get comprehensive system status."""
        if not self.coordinator:
            return {"status": "not_initialized"}
        
        return await self.coordinator.get_swarm_status()


# Global system instance
qbit_system = QBitSystem()


@app.command()
def start(
    strategy: str = typer.Option(
        "adaptive",
        help="Swarm coordination strategy",
        case_sensitive=False
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file path"
    )
):
    """Start the Q-BIT system."""
    
    # Parse strategy
    try:
        swarm_strategy = SwarmStrategy(strategy.lower())
    except ValueError:
        console.print(f"❌ Invalid strategy: {strategy}", style="red")
        console.print(f"Available strategies: {', '.join([s.value for s in SwarmStrategy])}")
        raise typer.Exit(1)
    
    async def run_system():
        """Run the Q-BIT system."""
        try:
            # Setup signal handlers
            def signal_handler(signum, frame):
                console.print(f"\n🛑 Received signal {signum}", style="yellow")
                asyncio.create_task(qbit_system.stop())
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Initialize and start system
            await qbit_system.initialize(strategy=swarm_strategy)
            await qbit_system.start()
            
        except KeyboardInterrupt:
            console.print("\n🛑 Interrupted by user", style="yellow")
        except Exception as e:
            console.print(f"❌ System error: {e}", style="red")
            logger.error("System startup failed", error=str(e))
            raise typer.Exit(1)
        finally:
            await qbit_system.stop()
    
    # Run the system
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="blue")


@app.command()
def status():
    """Get system status."""
    async def get_status():
        status = await qbit_system.get_status()
        console.print_json(data=status)
    
    try:
        asyncio.run(get_status())
    except Exception as e:
        console.print(f"❌ Failed to get status: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from src import __version__, __description__
    
    console.print(Panel.fit(
        f"[bold blue]Q-BIT[/bold blue] v{__version__}\n{__description__}",
        border_style="blue"
    ))


if __name__ == "__main__":
    app()
