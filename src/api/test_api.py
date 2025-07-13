"""
Test API routes for end-to-end flow testing
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import asyncio
import json
from datetime import datetime

from src.api.dependencies import get_current_user
from src.models.user import User

router = APIRouter(prefix="/test", tags=["Testing"])


@router.get("/full-flow")
async def run_full_flow_test(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Run the complete end-to-end flow test
    
    This endpoint simulates the full crypto deposit to UPI purchase flow:
    1. Create test users (depositor and buyer)
    2. Simulate crypto deposit
    3. Simulate blockchain confirmation
    4. Buyer purchases via UPI
    5. Simulate UPI payment success
    6. Verify crypto release
    7. Get dashboard summaries
    8. Get notifications
    
    Returns comprehensive test results
    """
    try:
        # Import and run the full flow test
        from scripts.test_full_flow import run_full_flow_test
        
        # Run the test
        result = await run_full_flow_test()
        
        return {
            "success": True,
            "message": "Full flow test completed",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for testing
    
    Returns basic system health information
    """
    try:
        from src.services.db import db_service
        from src.services.mock_blockchain_listener import mock_blockchain_listener
        
        # Check database connection
        db_status = "connected" if db_service.database is not None else "disconnected"
        
        # Check blockchain listener
        listener_status = "active" if mock_blockchain_listener.is_listening else "inactive"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "blockchain_listener": listener_status,
                "api": "running"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/reset-test-data")
async def reset_test_data(current_user: User = Depends(get_current_user)):
    """
    Reset test data for clean testing
    
    Clears test users, escrow deposits, and other test data
    """
    try:
        from src.services.db import db_service
        
        # Clear test data collections
        collections_to_clear = [
            "users",
            "escrow_deposits", 
            "upi_payments",
            "wallets",
            "salaries",
            "investment_strategies"
        ]
        
        cleared_count = {}
        
        for collection in collections_to_clear:
            # Clear documents with test emails
            result = await db_service.delete_documents(
                collection,
                {
                    "$or": [
                        {"email": {"$regex": ".*@test\\.com"}},
                        {"email": {"$regex": ".*@example\\.com"}},
                        {"user_id": {"$regex": "test.*"}}
                    ]
                }
            )
            cleared_count[collection] = result
        
        return {
            "success": True,
            "message": "Test data reset completed",
            "cleared_count": cleared_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reset failed: {str(e)}"
        )


@router.get("/system-status")
async def get_system_status():
    """
    Get comprehensive system status for testing
    
    Returns status of all major system components
    """
    try:
        from src.services.db import db_service
        from src.services.mock_blockchain_listener import mock_blockchain_listener
        from src.services.twitter_service import twitter_service
        
        # Check database
        db_connected = db_service.database is not None
        
        # Check blockchain listener
        listener_active = mock_blockchain_listener.is_listening
        
        # Check Twitter service
        twitter_active = twitter_service.scheduler.running if hasattr(twitter_service, 'scheduler') else False
        
        # Get collection counts
        collections = ["users", "escrow_deposits", "upi_payments", "wallets", "salaries", "investment_strategies"]
        collection_counts = {}
        
        for collection in collections:
            try:
                count = await db_service.get_collection(collection).count_documents({})
                collection_counts[collection] = count
            except:
                collection_counts[collection] = 0
        
        return {
            "system_status": "operational" if all([db_connected, listener_active]) else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": {
                    "status": "connected" if db_connected else "disconnected",
                    "collections": collection_counts
                },
                "blockchain_listener": {
                    "status": "active" if listener_active else "inactive",
                    "escrow_wallet": mock_blockchain_listener.escrow_wallet
                },
                "twitter_service": {
                    "status": "active" if twitter_active else "inactive"
                },
                "api": {
                    "status": "running",
                    "version": "1.0.0"
                }
            }
        }
        
    except Exception as e:
        return {
            "system_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 