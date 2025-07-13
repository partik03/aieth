"""
Investment strategy API routes for AI-driven automated investments
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

from src.models.investment_strategy import (
    StrategyCreateRequest,
    StrategyResponse,
    InvoiceResponse,
    InvestmentStrategy,
    InvestmentInvoice
)
from src.services.investment_strategy_service import investment_strategy_service
from src.api.dependencies import get_current_user
from src.models.user import User

router = APIRouter(prefix="/investment-strategy", tags=["Investment Strategies"])


@router.post("/create", response_model=StrategyResponse)
async def create_investment_strategy(
    strategy_data: StrategyCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new AI-driven investment strategy
    
    - **name**: Strategy name
    - **description**: Strategy description
    - **strategy_type**: Type of strategy (dollar_cost_averaging, lump_sum, etc.)
    - **trigger_type**: What triggers the investment (salary_received, market_dip, etc.)
    - **amount**: Investment amount in INR
    - **percentage**: Percentage of salary (optional)
    - **crypto_tokens**: List of crypto tokens to invest in
    - **allocation**: Token allocation percentages (must sum to 100%)
    - **risk_level**: Risk level (low, medium, high)
    - **max_investment**: Maximum investment amount
    - **min_investment**: Minimum investment amount
    """
    try:
        strategy = await investment_strategy_service.create_strategy(current_user.id, strategy_data)
        
        return StrategyResponse(
            success=True,
            strategy=strategy,
            message="Investment strategy created successfully. Please approve it to activate."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Failed to create strategy: {str(e)}",
                "error_code": "STRATEGY_CREATION_ERROR"
            }
        )


@router.get("/strategies", response_model=Dict[str, Any])
async def get_user_strategies(current_user: User = Depends(get_current_user)):
    """
    Get all investment strategies for the current user
    """
    try:
        strategies = await investment_strategy_service.get_user_strategies(current_user.id)
        
        return {
            "success": True,
            "strategies": [strategy.dict() for strategy in strategies],
            "count": len(strategies),
            "active_count": len([s for s in strategies if s.is_active and s.is_approved])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get strategies: {str(e)}",
                "error_code": "STRATEGY_FETCH_ERROR"
            }
        )


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific investment strategy by ID
    """
    try:
        strategy = await investment_strategy_service.get_strategy(strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail="Strategy not found"
            )
        
        # Ensure user can only access their own strategies
        if strategy.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only access own strategies"
            )
        
        return StrategyResponse(
            success=True,
            strategy=strategy,
            message="Strategy retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get strategy: {str(e)}",
                "error_code": "STRATEGY_FETCH_ERROR"
            }
        )


@router.post("/strategies/{strategy_id}/approve", response_model=StrategyResponse)
async def approve_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Approve an investment strategy for execution
    """
    try:
        strategy = await investment_strategy_service.get_strategy(strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail="Strategy not found"
            )
        
        if strategy.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only approve own strategies"
            )
        
        success = await investment_strategy_service.approve_strategy(strategy_id)
        
        if success:
            # Get updated strategy
            updated_strategy = await investment_strategy_service.get_strategy(strategy_id)
            
            return StrategyResponse(
                success=True,
                strategy=updated_strategy,
                message="Strategy approved successfully. AI will now monitor for triggers."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to approve strategy"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to approve strategy: {str(e)}",
                "error_code": "STRATEGY_APPROVAL_ERROR"
            }
        )


@router.post("/strategies/{strategy_id}/deactivate", response_model=StrategyResponse)
async def deactivate_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate an investment strategy
    """
    try:
        strategy = await investment_strategy_service.get_strategy(strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail="Strategy not found"
            )
        
        if strategy.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only deactivate own strategies"
            )
        
        success = await investment_strategy_service.update_strategy(strategy_id, {"is_active": False})
        
        if success:
            updated_strategy = await investment_strategy_service.get_strategy(strategy_id)
            
            return StrategyResponse(
                success=True,
                strategy=updated_strategy,
                message="Strategy deactivated successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to deactivate strategy"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to deactivate strategy: {str(e)}",
                "error_code": "STRATEGY_DEACTIVATION_ERROR"
            }
        )


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an investment strategy
    """
    try:
        strategy = await investment_strategy_service.get_strategy(strategy_id)
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail="Strategy not found"
            )
        
        if strategy.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only delete own strategies"
            )
        
        success = await investment_strategy_service.delete_strategy(strategy_id)
        
        if success:
            return {
                "success": True,
                "message": "Strategy deleted successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete strategy"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to delete strategy: {str(e)}",
                "error_code": "STRATEGY_DELETION_ERROR"
            }
        )


@router.post("/check-triggers")
async def check_investment_triggers(current_user: User = Depends(get_current_user)):
    """
    Check for investment strategies that should be triggered
    This endpoint can be called by the AI chatbot or automated systems
    """
    try:
        triggered_strategies = await investment_strategy_service.check_triggers(current_user.id)
        
        if not triggered_strategies:
            return {
                "success": True,
                "message": "No strategies triggered at this time",
                "triggered_strategies": [],
                "count": 0
            }
        
        # Generate invoices for triggered strategies
        invoices = []
        for strategy in triggered_strategies:
            reason = f"Strategy '{strategy.name}' triggered by {strategy.trigger_type}"
            invoice = await investment_strategy_service.generate_investment_invoice(strategy, reason)
            invoices.append(invoice)
        
        return {
            "success": True,
            "message": f"Found {len(triggered_strategies)} triggered strategies",
            "triggered_strategies": [strategy.dict() for strategy in triggered_strategies],
            "invoices": [invoice.dict() for invoice in invoices],
            "count": len(triggered_strategies)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to check triggers: {str(e)}",
                "error_code": "TRIGGER_CHECK_ERROR"
            }
        )


@router.get("/invoices", response_model=Dict[str, Any])
async def get_investment_invoices(current_user: User = Depends(get_current_user)):
    """
    Get all investment invoices for the current user
    """
    try:
        invoices = await investment_strategy_service.get_user_invoices(current_user.id)
        
        return {
            "success": True,
            "invoices": [invoice.dict() for invoice in invoices],
            "count": len(invoices),
            "pending_count": len([i for i in invoices if i.status == "pending"]),
            "paid_count": len([i for i in invoices if i.status == "paid"]),
            "executed_count": len([i for i in invoices if i.status == "executed"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get invoices: {str(e)}",
                "error_code": "INVOICE_FETCH_ERROR"
            }
        )


@router.post("/invoices/{invoice_id}/execute")
async def execute_investment(
    invoice_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Execute an investment after payment is confirmed
    This endpoint is typically called by the UPI callback system
    """
    try:
        # Get invoice to verify ownership
        invoices = await investment_strategy_service.get_user_invoices(current_user.id)
        invoice = next((i for i in invoices if i.id == invoice_id), None)
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail="Invoice not found"
            )
        
        if invoice.status != "paid":
            raise HTTPException(
                status_code=400,
                detail="Invoice must be paid before execution"
            )
        
        success = await investment_strategy_service.execute_investment(invoice_id)
        
        if success:
            return {
                "success": True,
                "message": "Investment executed successfully"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to execute investment"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to execute investment: {str(e)}",
                "error_code": "INVESTMENT_EXECUTION_ERROR"
            }
        ) 