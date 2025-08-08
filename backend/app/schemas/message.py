from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


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


class MessageBase(BaseModel):
    content: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    role: MessageRole = MessageRole.USER
    session_id: str


class MessageResponse(MessageBase):
    id: int
    session_id: str
    role: MessageRole
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    tool_use_id: Optional[str] = None
    raw_content: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageList(BaseModel):
    messages: list[MessageResponse]
    total: int
    session_id: str
