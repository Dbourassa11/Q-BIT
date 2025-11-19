"""
Core Framework Module

Provides the foundational components for the Q-BIT agent system including
agent lifecycle management, state management, and communication infrastructure.
"""

from .agent import BaseAgent, AgentStatus, AgentCapability
from .lifecycle import AgentLifecycle, LifecycleEvent
from .state import StateManager, StateType
from .communication import CommunicationHub, Message, MessageType

__all__ = [
    "BaseAgent",
    "AgentStatus", 
    "AgentCapability",
    "AgentLifecycle",
    "LifecycleEvent",
    "StateManager",
    "StateType",
    "CommunicationHub",
    "Message",
    "MessageType",
]
