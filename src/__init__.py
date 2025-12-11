"""
Q-BIT: Advanced Omni Agent & Swarm Intelligence Hub

The most advanced autonomous AI programming and coding creation system.
"""

__version__ = "0.1.0"
__author__ = "Q-BIT Team"
__email__ = "team@q-bit.ai"
__description__ = "Advanced Omni Agent & Swarm Intelligence Hub for Autonomous Programming"

from src.core.agent import BaseAgent
from src.core.lifecycle import AgentLifecycle
from src.core.state import StateManager
from src.core.communication import CommunicationHub
from src.swarm.coordinator import SwarmCoordinator
from src.programming.code_generator import CodeGenerator

# Optional imports with heavy dependencies
try:
    from src.programming.code_analyzer import CodeAnalyzer
    _has_code_analyzer = True
except ImportError:
    CodeAnalyzer = None
    _has_code_analyzer = False

__all__ = [
    "BaseAgent",
    "AgentLifecycle", 
    "StateManager",
    "CommunicationHub",
    "SwarmCoordinator",
    "CodeGenerator",
]

if _has_code_analyzer:
    __all__.append("CodeAnalyzer")
