from fastapi import APIRouter
from app.api.endpoints import sessions, messages, vnc, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(vnc.router, prefix="/vnc", tags=["vnc"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
