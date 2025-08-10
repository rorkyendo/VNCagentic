from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from typing import TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class SessionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ERROR = "error"


class Session(Base):
    """Session model for computer use agent sessions"""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    status = Column(String(20), default=SessionStatus.ACTIVE.value)
    
    # Agent configuration
    model = Column(String(50), nullable=False)
    api_provider = Column(String(20), default="anthropic")
    system_prompt = Column(Text, nullable=True)
    max_tokens = Column(Integer, default=4096)
    
    # VNC connection details
    vnc_display = Column(String(10), nullable=True)
    vnc_port = Column(Integer, nullable=True)
    vnc_password = Column(String(50), nullable=True)
    
    # Session metadata
    session_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session(id='{self.id}', status='{self.status}', user_id={self.user_id})>"
