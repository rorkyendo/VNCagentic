from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class WebSocketMessageType(str, Enum):
    # Client to Server
    PING = "ping"
    USER_MESSAGE = "user_message"
    TOOL_RESPONSE = "tool_response"
    
    # Server to Client
    PONG = "pong"
    AGENT_MESSAGE = "agent_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    SESSION_UPDATE = "session_update"
    ERROR = "error"
    STATUS = "status"


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    content: Optional[Union[str, Dict[str, Any]]] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentStatusUpdate(BaseModel):
    status: str
    current_action: Optional[str] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None


class ToolCallMessage(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]
    tool_use_id: str


class ToolResultMessage(BaseModel):
    tool_use_id: str
    result: Dict[str, Any]
    error: Optional[str] = None
