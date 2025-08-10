from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging

from app.models.message import Message
from app.schemas.message import MessageCreate, MessageResponse

logger = logging.getLogger(__name__)


class MessageService:
    """Service for managing chat messages"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """Create a new message"""
        message = Message(
            session_id=message_data.session_id,
            role=message_data.role.value,
            message_type=message_data.message_type.value,
            content=message_data.content,
            message_metadata=message_data.metadata  # Note: model field is message_metadata
        )
        
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        return self._message_to_response(message)
    
    async def get_message(self, message_id: int) -> Optional[MessageResponse]:
        """Get message by ID"""
        stmt = select(Message).where(Message.id == message_id)
        result = await self.db.execute(stmt)
        message = result.scalar_one_or_none()
        
        if message:
            return self._message_to_response(message)
        return None
    
    async def list_messages(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageResponse]:
        """List messages for a session"""
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        return [self._message_to_response(message) for message in messages]
    
    def _message_to_response(self, message: Message) -> MessageResponse:
        """Convert message model to response format"""
        return MessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            message_type=message.message_type,
            content=message.content,
            tool_name=message.tool_name,
            tool_input=message.tool_input,
            tool_output=message.tool_output,
            tool_use_id=message.tool_use_id,
            raw_content=message.raw_content,
            metadata=message.message_metadata,  # Note: model field is message_metadata
            created_at=message.created_at
        )
