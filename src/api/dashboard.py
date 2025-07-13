"""
Dashboard API routes for user summary and analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from src.services.dashboard_service import dashboard_service
from src.api.dependencies import get_current_user
from src.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_user)):
    """
    Get complete dashboard summary for authenticated user
    
    Returns:
    - Wallet balances (crypto + INR)
    - Last salary investment strategy
    - Recent transactions
    - Escrow activity
    - Investment performance
    """
    try:
        summary = await dashboard_service.get_dashboard_summary(current_user.id)
        
        return {
            "success": True,
            "data": summary,
            "message": "Dashboard summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.get("/balances")
async def get_wallet_balances(current_user: User = Depends(get_current_user)):
    """
    Get user's wallet balances (crypto + INR)
    """
    try:
        balances = await dashboard_service.get_wallet_balances(current_user.id)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "balances": balances,
                "total_crypto_value": sum(balances.values()) - balances.get("INR", 0)
            },
            "message": "Wallet balances retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get wallet balances: {str(e)}"
        )


@router.get("/transactions")
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=50, description="Number of transactions to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent transactions for the user
    
    - **limit**: Number of transactions to return (1-50)
    """
    try:
        transactions = await dashboard_service.get_recent_transactions(current_user.id, limit)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "transactions": transactions,
                "count": len(transactions)
            },
            "message": "Recent transactions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recent transactions: {str(e)}"
        )


@router.get("/investments")
async def get_investment_summary(current_user: User = Depends(get_current_user)):
    """
    Get investment summary and latest strategy
    """
    try:
        last_investment = await dashboard_service.get_last_salary_investment(current_user.id)
        performance = await dashboard_service.get_investment_performance(current_user.id)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "last_investment": last_investment,
                "performance": performance
            },
            "message": "Investment summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get investment summary: {str(e)}"
        )


@router.get("/escrow")
async def get_escrow_summary(current_user: User = Depends(get_current_user)):
    """
    Get escrow activity summary
    """
    try:
        escrow_activity = await dashboard_service.get_escrow_activity(current_user.id)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "escrow_activity": escrow_activity,
                "net_escrow": escrow_activity["deposited"] - escrow_activity["purchased"]
            },
            "message": "Escrow summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get escrow summary: {str(e)}"
        )


@router.get("/analytics")
async def get_analytics_summary(current_user: User = Depends(get_current_user)):
    """
    Get analytics summary with key metrics
    """
    try:
        # Get all data for analytics
        balances = await dashboard_service.get_wallet_balances(current_user.id)
        escrow_activity = await dashboard_service.get_escrow_activity(current_user.id)
        performance = await dashboard_service.get_investment_performance(current_user.id)
        
        # Calculate key metrics
        total_crypto_value = sum(balances.values()) - balances.get("INR", 0)
        total_fiat = balances.get("INR", 0)
        escrow_net = escrow_activity["deposited"] - escrow_activity["purchased"]
        
        analytics = {
            "user_id": current_user.id,
            "total_portfolio_value": total_crypto_value + total_fiat,
            "crypto_allocation": total_crypto_value / (total_crypto_value + total_fiat) * 100 if (total_crypto_value + total_fiat) > 0 else 0,
            "fiat_allocation": total_fiat / (total_crypto_value + total_fiat) * 100 if (total_crypto_value + total_fiat) > 0 else 0,
            "escrow_utilization": escrow_activity["deposited"] / (total_crypto_value + total_fiat) * 100 if (total_crypto_value + total_fiat) > 0 else 0,
            "investment_frequency": performance["strategies_count"],
            "risk_profile": performance["avg_risk_level"],
            "active_tokens": len([k for k, v in balances.items() if k != "INR" and v > 0])
        }
        
        return {
            "success": True,
            "data": analytics,
            "message": "Analytics summary retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics summary: {str(e)}"
        ) 