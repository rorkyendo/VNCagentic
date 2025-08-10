import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from datetime import datetime
import uuid

from app.core.config import settings
from app.core.redis import get_redis
from app.schemas.websocket import WebSocketMessage, WebSocketMessageType, AgentStatusUpdate
from app.agent.ai_generative_agent import AIGenerativeAgent

logger = logging.getLogger(__name__)


class AgentService:
    """Service for managing computer use agents and their sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, AIGenerativeAgent] = {}
        self.session_websockets: Dict[str, List[WebSocket]] = {}
    
    async def initialize_session(self, session_id: str) -> bool:
        """Initialize a new computer use agent for the session"""
        try:
            # Determine API configuration based on provider
            api_config = self._get_api_config()
            
            # Create agent instance
            agent = AIGenerativeAgent(
                session_id=session_id,
                model=settings.ANTHROPIC_MODEL,
                api_provider=settings.API_PROVIDER,
                api_key=settings.ANTHROPIC_API_KEY,
                on_output=self._on_agent_output,
                on_tool_call=self._on_tool_call,
                on_tool_result=self._on_tool_result,
                on_status_update=self._on_status_update,
                api_base_url=api_config.get('base_url')
            )
            
            # Initialize agent
            await agent.initialize()
            
            # Store in active sessions
            self.active_sessions[session_id] = agent
            
            # Initialize websocket list for this session
            self.session_websockets[session_id] = []
            
            logger.info(f"Agent initialized for session {session_id} with {settings.API_PROVIDER} provider")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent for session {session_id}: {e}")
            return False
    
    def _get_api_config(self) -> Dict[str, str]:
        """Get API configuration based on provider"""
        if settings.API_PROVIDER == "comet":
            return {
                'base_url': settings.COMET_API_BASE_URL,
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {}'
            }
        elif settings.API_PROVIDER == "anthropic":
            return {
                'base_url': settings.ANTHROPIC_API_URL,
                'auth_header': 'x-api-key',
                'auth_format': '{}'
            }
        else:
            return {
                'base_url': settings.ANTHROPIC_API_URL,
                'auth_header': 'x-api-key', 
                'auth_format': '{}'
            }
    
    async def cleanup_session(self, session_id: str):
        """Clean up resources for a session"""
        try:
            # Stop agent if active
            if session_id in self.active_sessions:
                agent = self.active_sessions[session_id]
                await agent.cleanup()
                del self.active_sessions[session_id]
            
            # Close all websockets for this session
            if session_id in self.session_websockets:
                websockets = self.session_websockets[session_id].copy()
                for ws in websockets:
                    try:
                        await ws.close()
                    except:
                        pass
                del self.session_websockets[session_id]
            
            logger.info(f"Session {session_id} cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
    
    async def process_user_message(self, session_id: str, message: str):
        """Process a user message through the agent"""
        try:
            logger.info(f"Processing user message for session {session_id}: {message[:100]}...")
            
            if session_id not in self.active_sessions:
                logger.warning(f"No active agent for session {session_id}, initializing...")
                success = await self.initialize_session(session_id)
                if not success:
                    raise ValueError(f"Failed to initialize agent for session {session_id}")
            
            agent = self.active_sessions[session_id]
            logger.info(f"Sending message to agent for session {session_id}")
            
            # Send message to agent
            await agent.process_message(message)
            logger.info(f"Message processed by agent for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}")
            await self._broadcast_to_session(session_id, WebSocketMessage(
                type=WebSocketMessageType.ERROR,
                content={"error": str(e)},
                session_id=session_id
            ))
    
    async def register_websocket(self, session_id: str, websocket: WebSocket):
        """Register a websocket for session updates"""
        if session_id not in self.session_websockets:
            self.session_websockets[session_id] = []
        
        self.session_websockets[session_id].append(websocket)
        logger.info(f"WebSocket registered for session {session_id}")
    
    async def unregister_websocket(self, session_id: str, websocket: WebSocket):
        """Unregister a websocket"""
        if session_id in self.session_websockets:
            try:
                self.session_websockets[session_id].remove(websocket)
                logger.info(f"WebSocket unregistered for session {session_id}")
            except ValueError:
                pass
    
    async def _broadcast_to_session(self, session_id: str, message: WebSocketMessage):
        """Broadcast a message to all websockets for a session"""
        if session_id not in self.session_websockets:
            return
        
        websockets = self.session_websockets[session_id].copy()
        message_json = message.model_dump_json()
        
        for websocket in websockets:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send message to websocket: {e}")
                # Remove failed websocket
                try:
                    self.session_websockets[session_id].remove(websocket)
                except ValueError:
                    pass
    
    async def _save_agent_response_to_db(self, session_id: str, response_text: str):
        """Save agent response to database"""
        try:
            from app.core.database import get_db_session
            from app.services.message_service import MessageService
            from app.schemas.message import MessageCreate
            
            # Get database session
            async for db in get_db_session():
                message_service = MessageService(db)
                
                # Create agent message
                agent_message = MessageCreate(
                    content=response_text,
                    role="assistant",
                    message_type="agent_response",
                    metadata={"generated_by": "mock_agent"},
                    session_id=session_id
                )
                
                # Save to database
                await message_service.create_message(agent_message)
                logger.info(f"Agent response saved to database for session {session_id}")
                break
                
        except Exception as e:
            logger.error(f"Error saving agent response to database: {e}")

    # Agent callback methods
    async def _on_agent_output(self, session_id: str, content: Any):
        """Handle agent output"""
        message = WebSocketMessage(
            type=WebSocketMessageType.AGENT_MESSAGE,
            content=content,
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_session(session_id, message)
    
    async def _on_tool_call(self, session_id: str, tool_name: str, tool_input: Dict[str, Any], tool_use_id: str):
        """Handle tool call from agent"""
        message = WebSocketMessage(
            type=WebSocketMessageType.TOOL_CALL,
            content={
                "tool_name": tool_name,
                "tool_input": tool_input,
                "tool_use_id": tool_use_id
            },
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_session(session_id, message)
    
    async def _on_tool_result(self, session_id: str, tool_use_id: str, result: Any, error: Optional[str] = None):
        """Handle tool result"""
        message = WebSocketMessage(
            type=WebSocketMessageType.TOOL_RESULT,
            content={
                "tool_use_id": tool_use_id,
                "result": result,
                "error": error
            },
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_session(session_id, message)
    
    async def _on_status_update(self, session_id: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Handle status updates from agent"""
        message = WebSocketMessage(
            type=WebSocketMessageType.STATUS,
            content={
                "status": status,
                "details": details or {}
            },
            session_id=session_id,
            timestamp=datetime.utcnow()
        )
        await self._broadcast_to_session(session_id, message)
