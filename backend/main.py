from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, dispose_db
from routes import auth_router, admin_router, payment_router, websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")

    # Initialize database tables in development mode
    if settings.environment == "development":
        print("Creating database tables...")
        await init_db()
        print("Database tables created")

    yield

    # Shutdown
    print("Shutting down...")
    await dispose_db()
    print("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Photobooth Kiosk API with multi-booth support",
    version=settings.app_version,
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(payment_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
