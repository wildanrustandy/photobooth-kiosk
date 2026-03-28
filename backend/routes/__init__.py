from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.payment import router as payment_router
from routes.websocket import router as websocket_router

__all__ = ["auth_router", "admin_router", "payment_router", "websocket_router"]
