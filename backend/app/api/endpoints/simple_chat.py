"""
AI Generative Chat API - Pure AI untuk computer control
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from app.core.database import get_db_session
from app.services.session_service import SessionService
from app.services.message_service import MessageService
from app.schemas.session import SessionCreate
from app.schemas.message import MessageCreate
from app.agent.ai_generative_agent import AIGenerativeAgent

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    response: str
    success: bool
    actions_taken: list = []
    error: Optional[str] = None

# Global agent storage (simple in-memory for now)
active_agents: Dict[str, AIGenerativeAgent] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Simple chat endpoint using POST method"""
    try:
        session_service = SessionService(db)
        message_service = MessageService(db)
        
        # Get or create session
        if request.session_id:
            session = await session_service.get_session(request.session_id)
            if not session:
                session_data = SessionCreate(title="Simple Chat Session")
                session = await session_service.create_session(session_data)
        else:
            session_data = SessionCreate(title="Simple Chat Session")
            session = await session_service.create_session(session_data)
        
        session_id = session.id
        
        # Get or create agent for session
        if session_id not in active_agents:
            agent = AIGenerativeAgent(session_id)
            active_agents[session_id] = agent
        else:
            agent = active_agents[session_id]
        
        # Save user message
        user_message_data = MessageCreate(
            session_id=session_id,
            role="user",
            content=request.message
        )
        await message_service.create_message(user_message_data)
        
        logger.info(f"Processing message: {request.message} for session {session_id}")
        
        # Process message through agent
        result = await agent.process_message(request.message)
        
        # Save agent response
        agent_message_data = MessageCreate(
            session_id=session_id,
            role="assistant",
            content=result["response"]
        )
        await message_service.create_message(agent_message_data)
        
        return ChatResponse(
            session_id=session_id,
            message=request.message,
            response=result["response"],
            success=result["success"],
            actions_taken=result.get("actions_taken", []),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get chat history for a session"""
    try:
        message_service = MessageService(db)
        messages = await message_service.list_messages(session_id=session_id)
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))
