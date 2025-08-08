from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db_session
from app.services.message_service import MessageService
from app.schemas.message import MessageCreate, MessageResponse, MessageList

router = APIRouter()


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Send a message to an agent session"""
    try:
        message_service = MessageService(db)
        
        # Ensure session_id matches
        message_data.session_id = session_id
        
        # Create and store message
        message = await message_service.create_message(message_data)
        
        # TODO: Trigger agent processing
        # agent_service = AgentService()
        # await agent_service.process_user_message(session_id, message_data.content)
        
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages", response_model=MessageList)
async def get_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """Get messages for a session"""
    try:
        message_service = MessageService(db)
        messages = await message_service.list_messages(
            session_id=session_id,
            skip=skip,
            limit=limit
        )
        return MessageList(
            messages=messages,
            total=len(messages),
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    session_id: str,
    message_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific message"""
    try:
        message_service = MessageService(db)
        message = await message_service.get_message(message_id)
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if message.session_id != session_id:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
