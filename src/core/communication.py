"""
Communication Hub

Provides inter-agent communication infrastructure for the Q-BIT system.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from pydantic import BaseModel, Field
import structlog
import uuid

logger = structlog.get_logger(__name__)


class MessageType(str, Enum):
    """Types of messages that can be sent between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    QUERY = "query"
    UPDATE = "update"
    ERROR = "error"


class MessagePriority(int, Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


class Message(BaseModel):
    """Represents a message between agents."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    sender_id: str
    receiver_id: Optional[str] = None  # None for broadcast
    subject: str
    content: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False


class MessageHandler:
    """Handles message processing for an entity."""
    
    def __init__(self, entity_id: str):
        """Initialize message handler."""
        self.entity_id = entity_id
        self.handlers: Dict[MessageType, List[Callable]] = {}
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.logger = structlog.get_logger(__name__).bind(entity_id=entity_id)
    
    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a handler for a specific message type."""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
        self.logger.info("Handler registered", message_type=message_type.value)
    
    async def handle_message(self, message: Message) -> None:
        """Handle an incoming message."""
        handlers = self.handlers.get(message.message_type, [])
        
        if not handlers:
            self.logger.warning(
                "No handlers for message type",
                message_type=message.message_type.value,
                message_id=message.message_id
            )
            return
        
        # Execute all handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                self.logger.error(
                    "Handler execution failed",
                    message_id=message.message_id,
                    error=str(e)
                )


class CommunicationHub:
    """
    Central communication hub for inter-agent messaging.
    
    Provides reliable message delivery, routing, and broadcasting
    capabilities for all agents in the Q-BIT system.
    """
    
    def __init__(self):
        """Initialize the communication hub."""
        self.handlers: Dict[str, MessageHandler] = {}
        self.message_history: List[Message] = []
        self.pending_responses: Dict[str, asyncio.Future] = {}
        
        self.logger = structlog.get_logger(__name__)
        
        # Configuration
        self.max_history_size = 10000
        self.message_timeout = 300  # 5 minutes
        
        # Stats
        self.stats = {
            "total_messages": 0,
            "broadcasts": 0,
            "failed_deliveries": 0,
            "pending_responses": 0
        }
    
    def register_entity(self, entity_id: str) -> MessageHandler:
        """Register an entity to receive messages."""
        if entity_id in self.handlers:
            return self.handlers[entity_id]
        
        handler = MessageHandler(entity_id)
        self.handlers[entity_id] = handler
        
        self.logger.info("Entity registered", entity_id=entity_id)
        return handler
    
    def unregister_entity(self, entity_id: str) -> None:
        """Unregister an entity from receiving messages."""
        if entity_id in self.handlers:
            del self.handlers[entity_id]
            self.logger.info("Entity unregistered", entity_id=entity_id)
    
    async def send_message(self, message: Message) -> Optional[str]:
        """
        Send a message to a recipient or broadcast to all.
        
        Returns the message ID.
        """
        self.message_history.append(message)
        self.stats["total_messages"] += 1
        
        # Trim history if needed
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
        
        self.logger.info(
            "Message sent",
            message_id=message.message_id,
            message_type=message.message_type.value,
            sender=message.sender_id,
            receiver=message.receiver_id or "broadcast"
        )
        
        # Handle broadcast
        if message.receiver_id is None:
            self.stats["broadcasts"] += 1
            await self._broadcast_message(message)
        else:
            await self._deliver_message(message)
        
        # Setup response waiting if needed
        if message.requires_response:
            future = asyncio.Future()
            self.pending_responses[message.message_id] = future
            self.stats["pending_responses"] += 1
        
        return message.message_id
    
    async def _deliver_message(self, message: Message) -> None:
        """Deliver a message to a specific recipient."""
        if message.receiver_id not in self.handlers:
            self.logger.warning(
                "Recipient not found",
                message_id=message.message_id,
                receiver_id=message.receiver_id
            )
            self.stats["failed_deliveries"] += 1
            return
        
        handler = self.handlers[message.receiver_id]
        await handler.handle_message(message)
    
    async def _broadcast_message(self, message: Message) -> None:
        """Broadcast a message to all registered entities."""
        delivery_tasks = []
        
        for entity_id, handler in self.handlers.items():
            # Don't send to self
            if entity_id == message.sender_id:
                continue
            
            # Create a copy for each recipient
            message_copy = message.model_copy()
            message_copy.receiver_id = entity_id
            
            task = asyncio.create_task(handler.handle_message(message_copy))
            delivery_tasks.append(task)
        
        # Wait for all deliveries
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)
    
    async def send_request(
        self,
        sender_id: str,
        receiver_id: str,
        subject: str,
        content: Any,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Send a request and wait for a response.
        
        Returns the response content or raises TimeoutError.
        """
        message = Message(
            message_type=MessageType.REQUEST,
            sender_id=sender_id,
            receiver_id=receiver_id,
            subject=subject,
            content=content,
            requires_response=True
        )
        
        message_id = await self.send_message(message)
        
        # Wait for response
        future = self.pending_responses.get(message_id)
        if not future:
            raise RuntimeError("Response future not created")
        
        try:
            response = await asyncio.wait_for(
                future,
                timeout=timeout or self.message_timeout
            )
            return response
        except asyncio.TimeoutError:
            self.pending_responses.pop(message_id, None)
            self.stats["pending_responses"] -= 1
            raise
    
    async def send_response(
        self,
        sender_id: str,
        original_message_id: str,
        content: Any
    ) -> None:
        """Send a response to a previous request."""
        # Find the original message
        original_message = None
        for msg in reversed(self.message_history):
            if msg.message_id == original_message_id:
                original_message = msg
                break
        
        if not original_message:
            self.logger.warning(
                "Original message not found for response",
                message_id=original_message_id
            )
            return
        
        # Create response message
        response = Message(
            message_type=MessageType.RESPONSE,
            sender_id=sender_id,
            receiver_id=original_message.sender_id,
            subject=f"Re: {original_message.subject}",
            content=content,
            reply_to=original_message_id
        )
        
        await self.send_message(response)
        
        # Complete the pending future
        if original_message_id in self.pending_responses:
            future = self.pending_responses.pop(original_message_id)
            if not future.done():
                future.set_result(content)
            self.stats["pending_responses"] -= 1
    
    async def broadcast(
        self,
        sender_id: str,
        subject: str,
        content: Any,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """Broadcast a message to all registered entities."""
        message = Message(
            message_type=MessageType.BROADCAST,
            priority=priority,
            sender_id=sender_id,
            receiver_id=None,
            subject=subject,
            content=content
        )
        
        return await self.send_message(message)
    
    def get_message_history(
        self,
        entity_id: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message history with optional filtering."""
        filtered = self.message_history
        
        if entity_id:
            filtered = [
                m for m in filtered
                if m.sender_id == entity_id or m.receiver_id == entity_id
            ]
        
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]
        
        return filtered[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get communication hub statistics."""
        return {
            **self.stats,
            "registered_entities": len(self.handlers),
            "history_size": len(self.message_history)
        }
