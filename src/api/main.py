"""
Main FastAPI application for Crypto-UPI Backend
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from src.services.db import db_service
from src.api import aadhaar, upi, salary
from src.api.ws_chat import websocket_endpoint
from src.services.twitter_service import twitter_service


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="Crypto-UPI Backend",
        description="AI-powered crypto trading platform with UPI integration for India",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Enable CORS for all origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    @app.on_event("startup")
    async def startup_event():
        """Connect to MongoDB and start services on startup"""
        await db_service.connect()
        twitter_service.start_scheduler()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Disconnect from MongoDB and stop services on shutdown"""
        await db_service.disconnect()
        twitter_service.stop_scheduler()
    
    # Include API routers
    app.include_router(aadhaar.router, prefix="/api/aadhaar", tags=["Aadhaar Verification"])
    app.include_router(upi.router, prefix="/api/upi", tags=["UPI Payments"])
    app.include_router(salary.router, prefix="/api", tags=["Salary & Investment"])
    
    # WebSocket routes
    @app.websocket("/ws/chat/{user_id}")
    async def websocket_chat(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for AI wallet assistant chat"""
        await websocket_endpoint(websocket, user_id)
    
    @app.get("/ping")
    async def ping():
        """Health check endpoint"""
        return {"message": "pong"}
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Crypto-UPI Backend API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs"
        }
    
    return app


# Create the application instance
app = create_app() 