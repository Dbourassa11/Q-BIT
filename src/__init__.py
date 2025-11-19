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
from src.programming.code_analyzer import CodeAnalyzer
from src.programming.code_generator import CodeGenerator

__all__ = [
    "BaseAgent",
    "AgentLifecycle", 
    "StateManager",
    "CommunicationHub",
    "SwarmCoordinator",
    "CodeAnalyzer",
    "CodeGenerator",
]
