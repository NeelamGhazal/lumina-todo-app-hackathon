"""API routers."""

from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.notifications import router as notifications_router
from app.routers.tasks import router as tasks_router

__all__ = ["auth_router", "chat_router", "notifications_router", "tasks_router"]
