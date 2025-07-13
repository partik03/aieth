"""
Main FastAPI application for Crypto-UPI Backend
"""

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.services.db import db_service
from src.services.mock_db import mock_db_service
from src.api import aadhaar, upi, salary, auth, escrow, dashboard, test_api, chat, investment_strategy, wallet
from src.services.twitter_service import twitter_service
from src.services.mock_blockchain_listener import mock_blockchain_listener as blockchain_listener


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
        try:
            # Try to connect to real MongoDB first
            await db_service.connect()
            print("✅ Using Real MongoDB Database")
            
            # Initialize collections if they don't exist
            await _initialize_collections()
            
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("🔄 Falling back to Mock Database")
            await mock_db_service.connect()
            # Replace the global db_service with mock_db_service
            import src.services.db
            src.services.db.db_service = mock_db_service
        
        twitter_service.start_scheduler()
        
        # Start blockchain listener in background
        asyncio.create_task(blockchain_listener.start_listening())
    
    async def _initialize_collections():
        """Initialize database collections with indexes"""
        try:
            # Create indexes for better performance
            db = db_service.get_database()
            
            # Users collection
            await db.users.create_index("aadhaar_number", unique=True)
            await db.users.create_index("created_at")
            
            # Investment strategies collection
            await db.investment_strategies.create_index("user_id")
            await db.investment_strategies.create_index("is_active")
            await db.investment_strategies.create_index("created_at")
            
            # Investment invoices collection
            await db.investment_invoices.create_index("user_id")
            await db.investment_invoices.create_index("status")
            await db.investment_invoices.create_index("created_at")
            
            # Wallets collection
            await db.wallets.create_index("user_id", unique=True)
            await db.wallets.create_index("wallet_address")
            
            # UPI payments collection
            await db.upi_payments.create_index("user_id")
            await db.upi_payments.create_index("txn_ref", unique=True)
            await db.upi_payments.create_index("status")
            
            # Salary records collection
            await db.salary_records.create_index("user_id")
            await db.salary_records.create_index("created_at")
            
            # Portfolio performance collection
            await db.portfolio_performance.create_index("user_id")
            await db.portfolio_performance.create_index("execution_date")
            
            # User investment stats collection
            await db.user_investment_stats.create_index("user_id", unique=True)
            
            print("✅ Database collections initialized with indexes")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize collections: {e}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Disconnect from database and stop services on shutdown"""
        try:
            await db_service.disconnect()
        except:
            pass
        
        try:
            await mock_db_service.disconnect()
        except:
            pass
        
        twitter_service.stop_scheduler()
        blockchain_listener.stop_listening()
    
    # Include API routers
    app.include_router(auth.router, prefix="/api", tags=["Authentication"])
    app.include_router(aadhaar.router, prefix="/api/aadhaar", tags=["Aadhaar Verification & Registration"])
    app.include_router(upi.router, prefix="/api/upi", tags=["UPI Payments"])
    app.include_router(salary.router, prefix="/api", tags=["Salary & Investment"])
    app.include_router(escrow.router, prefix="/api", tags=["Escrow Deposits"])
    app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
    app.include_router(chat.router, prefix="/api", tags=["AI Chatbot"])
    app.include_router(investment_strategy.router, prefix="/api", tags=["Investment Strategies"])
    app.include_router(wallet.router, prefix="/api", tags=["Wallet & Portfolio"])
    app.include_router(test_api.router, prefix="/api", tags=["Testing"])
    
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