from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import json
import logging

from app.core.database import get_db_session
from app.services.session_service import SessionService
from app.services.agent_service import AgentService
from app.schemas.session import (
    SessionCreate, SessionResponse, SessionUpdate, SessionList,
    SessionStatus
)
from app.schemas.websocket import WebSocketMessage, WebSocketMessageType

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new agent session"""
    try:
        session_service = SessionService(db)
        session = await session_service.create_session(session_data)
        
        # Initialize agent for this session
        agent_service = AgentService()
        await agent_service.initialize_session(session.id)
        
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=SessionList)
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[SessionStatus] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List all sessions with optional filtering"""
    try:
        session_service = SessionService(db)
        sessions = await session_service.list_sessions(
            skip=skip, 
            limit=limit, 
            status=status
        )
        return SessionList(sessions=sessions, total=len(sessions))
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get session details"""
    try:
        session_service = SessionService(db)
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update session details"""
    try:
        session_service = SessionService(db)
        session = await session_service.update_session(session_id, session_data)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a session"""
    try:
        session_service = SessionService(db)
        success = await session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Clean up agent resources
        agent_service = AgentService()
        await agent_service.cleanup_session(session_id)
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/{session_id}/stream")
async def session_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time session updates"""
    await websocket.accept()
    
    try:
        # Verify session exists
        async with get_db_session() as db:
            session_service = SessionService(db)
            session = await session_service.get_session(session_id)
            if not session:
                await websocket.close(code=4004, reason="Session not found")
                return
        
        # Get agent service for this session
        agent_service = AgentService()
        
        # Register websocket for this session
        await agent_service.register_websocket(session_id, websocket)
        
        # Listen for messages from client
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "user_message":
                    # Handle user message through agent service
                    await agent_service.process_user_message(
                        session_id, 
                        message.get("content", "")
                    )
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket error for session {session_id}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except Exception as e:
        logger.error(f"WebSocket connection error for session {session_id}: {e}")
    finally:
        # Unregister websocket
        try:
            await agent_service.unregister_websocket(session_id, websocket)
        except:
            pass
