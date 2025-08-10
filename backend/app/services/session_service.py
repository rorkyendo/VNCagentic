from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.session import Session, SessionStatus
from app.models.user import User
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse, VNCDetails
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing agent sessions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(self, session_data: SessionCreate) -> SessionResponse:
        """Create a new session"""
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Assign VNC display and port (simplified logic)
        vnc_display = settings.VNC_DISPLAY
        vnc_port = 5900  # Default VNC port
        
        # Create session model
        session = Session(
            id=session_id,
            user_id=session_data.user_id,
            title=session_data.title or f"Session {session_id[:8]}",
            model=session_data.model,
            api_provider=session_data.api_provider,
            system_prompt=session_data.system_prompt,
            max_tokens=session_data.max_tokens,
            vnc_display=vnc_display,
            vnc_port=vnc_port,
            vnc_password=settings.VNC_PASSWORD,
            status=SessionStatus.ACTIVE.value
        )
        
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        # Convert to response format
        return await self._session_to_response(session)
    
    async def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Get session by ID"""
        stmt = select(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            return await self._session_to_response(session)
        return None
    
    async def list_sessions(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[SessionStatus] = None
    ) -> List[SessionResponse]:
        """List sessions with optional filtering"""
        stmt = select(Session)
        
        if status:
            stmt = stmt.where(Session.status == status.value)
        
        stmt = stmt.offset(skip).limit(limit).order_by(Session.created_at.desc())
        
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()
        
        return [await self._session_to_response(session) for session in sessions]
    
    async def update_session(
        self, 
        session_id: str, 
        session_data: SessionUpdate
    ) -> Optional[SessionResponse]:
        """Update session"""
        # Get existing session
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Build update dict
        update_data = {}
        if session_data.title is not None:
            update_data[Session.title] = session_data.title
        if session_data.status is not None:
            update_data[Session.status] = session_data.status.value
        if session_data.system_prompt is not None:
            update_data[Session.system_prompt] = session_data.system_prompt
        if session_data.max_tokens is not None:
            update_data[Session.max_tokens] = session_data.max_tokens
        
        update_data[Session.updated_at] = datetime.utcnow()
        
        # Execute update
        stmt = update(Session).where(Session.id == session_id).values(**update_data)
        await self.db.execute(stmt)
        await self.db.commit()
        
        # Return updated session
        return await self.get_session(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session and all associated messages"""
        try:
            # First delete all messages for this session
            from app.models.message import Message
            messages_stmt = delete(Message).where(Message.session_id == session_id)
            messages_result = await self.db.execute(messages_stmt)
            
            # Then delete the session
            session_stmt = delete(Session).where(Session.id == session_id)
            session_result = await self.db.execute(session_stmt)
            
            await self.db.commit()
            
            print(f"Deleted {messages_result.rowcount} messages and {session_result.rowcount} session for session_id: {session_id}")
            return session_result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            print(f"Error deleting session {session_id}: {e}")
            raise
    
    async def update_last_activity(self, session_id: str):
        """Update session last activity timestamp"""
        stmt = update(Session).where(Session.id == session_id).values(
            last_activity=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def _session_to_response(self, session: Session) -> SessionResponse:
        """Convert session model to response format"""
        vnc_details = None
        if session.vnc_port and session.vnc_display:
            vnc_details = VNCDetails(
                display=session.vnc_display,
                port=session.vnc_port,
                password=session.vnc_password,
                web_url=f"http://localhost:6080/vnc.html?host=localhost&port={session.vnc_port}"
            )
        
        return SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            model=session.model,
            api_provider=session.api_provider,
            system_prompt=session.system_prompt,
            max_tokens=session.max_tokens,
            status=SessionStatus(session.status),
            vnc_details=vnc_details,
            metadata=session.metadata,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_activity=session.last_activity
        )
