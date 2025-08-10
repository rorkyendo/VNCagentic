from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .session import Session


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageType(str, Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    THINKING = "thinking"


class Message(Base):
    """Message model for chat history"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    
    # Message details
    role = Column(String(20), nullable=False)
    message_type = Column(String(20), default=MessageType.TEXT.value)
    content = Column(Text, nullable=True)
    raw_content = Column(JSON, nullable=True)  # Store original API format
    
    # Tool information (if applicable)
    tool_name = Column(String(50), nullable=True)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    tool_use_id = Column(String(50), nullable=True)
    
    # Message metadata
    message_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', type='{self.message_type}', session_id='{self.session_id}')>"
