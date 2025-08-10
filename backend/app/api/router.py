from fastapi import APIRouter
from app.api.endpoints import health, simple_chat, executor, sessions, messages

api_router = APIRouter()

# Include essential endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(simple_chat.router, prefix="/simple", tags=["simple-chat"])
api_router.include_router(executor.router, prefix="/vnc", tags=["vnc-exec"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(messages.router, prefix="/sessions", tags=["messages"])
