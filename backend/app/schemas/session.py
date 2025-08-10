from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ERROR = "error"


class SessionBase(BaseModel):
    title: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"
    api_provider: str = "anthropic"
    system_prompt: Optional[str] = None
    max_tokens: int = 4096


class SessionCreate(SessionBase):
    user_id: int = Field(default=1, description="User ID (simplified for demo)")


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[SessionStatus] = None
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None


class VNCDetails(BaseModel):
    display: Optional[str] = None
    port: Optional[int] = None
    password: Optional[str] = None
    web_url: Optional[str] = None


class SessionResponse(SessionBase):
    id: str
    user_id: int
    status: SessionStatus
    vnc_details: Optional[VNCDetails] = None
    session_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SessionList(BaseModel):
    sessions: List[SessionResponse]
    total: int
