"""
Wallet API routes for detailed investment and portfolio data
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.services.wallet_service import wallet_service
from src.services.investment_strategy_service import investment_strategy_service
from src.services.dashboard_service import dashboard_service
from src.api.dependencies import get_current_user
from src.models.user import User

router = APIRouter(prefix="/wallet", tags=["Wallet & Portfolio"])


@router.get("/portfolio")
async def get_portfolio_overview():
    """
    Get complete portfolio overview with all investments and holdings
    """
    try:
        current_user = {"id":"6872f4a6f0cdf587b2d8f06b"}
        # Get wallet balances
        balances = await dashboard_service.get_wallet_balances(current_user["id"])
        
        # Get investment strategies
        strategies = await investment_strategy_service.get_user_strategies(current_user["id"])
        
        # Get investment invoices
        invoices = await investment_strategy_service.get_user_invoices(current_user["id"])
        
        # Calculate portfolio metrics
        total_crypto_value = sum(balances.values()) - balances.get("INR", 0)
        total_fiat = balances.get("INR", 0)
        total_portfolio = total_crypto_value + total_fiat
        
        # Calculate investment metrics
        total_invested = sum(invoice.amount for invoice in invoices if invoice.status in ["paid", "executed"])
        pending_investments = sum(invoice.amount for invoice in invoices if invoice.status == "pending")
        
        portfolio = {
            "user_id": current_user["id"],
            "total_portfolio_value": total_portfolio,
            "total_crypto_value": total_crypto_value,
            "total_fiat_value": total_fiat,
            "total_invested": total_invested,
            "pending_investments": pending_investments,
            "portfolio_growth": ((total_portfolio - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "crypto_allocation_percentage": (total_crypto_value / total_portfolio * 100) if total_portfolio > 0 else 0,
            "fiat_allocation_percentage": (total_fiat / total_portfolio * 100) if total_portfolio > 0 else 0,
            "active_strategies": len([s for s in strategies if s.is_active and s.is_approved]),
            "total_strategies": len(strategies),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": portfolio,
            "message": "Portfolio overview retrieved successfully"
        }
        
    except Exception as e:
        print(f"Failed to get portfolio overview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get portfolio overview: {str(e)}",
                "error_code": "PORTFOLIO_ERROR"
            }
        )


@router.get("/holdings")
async def get_token_holdings():
    """
    Get detailed token holdings with current values and performance
    """
    try:
        current_user = {"id":"6872f4a6f0cdf587b2d8f06b"}

        balances = await dashboard_service.get_wallet_balances(current_user["id"])
        
        # Filter out INR and get only crypto holdings
        crypto_holdings = {k: v for k, v in balances.items() if k != "INR" and v > 0}
        
        # Get investment history for each token
        invoices = await investment_strategy_service.get_user_invoices(current_user["id"])
        executed_invoices = [i for i in invoices if i.status == "executed"]
        
        holdings_data = []
        for token, balance in crypto_holdings.items():
            # Calculate total invested in this token
            token_invested = 0
            for invoice in executed_invoices:
                if token in invoice.crypto_tokens:
                    # Calculate amount allocated to this token
                    token_percentage = invoice.allocation.get(token, 0)
                    token_invested += (invoice.amount * token_percentage) / 100
            
            # Mock current price (in real implementation, fetch from price API)
            current_price = _get_mock_token_price(token)
            current_value = balance * current_price
            
            # Calculate performance
            performance_percentage = ((current_value - token_invested) / token_invested * 100) if token_invested > 0 else 0
            
            holdings_data.append({
                "token": token,
                "balance": balance,
                "current_price": current_price,
                "current_value": current_value,
                "total_invested": token_invested,
                "performance_percentage": performance_percentage,
                "profit_loss": current_value - token_invested,
                "allocation_percentage": (current_value / sum(crypto_holdings.values()) * 100) if sum(crypto_holdings.values()) > 0 else 0
            })
        
        # Sort by current value (highest first)
        holdings_data.sort(key=lambda x: x["current_value"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user["id"],
                "total_holdings_value": sum(h["current_value"] for h in holdings_data),
                "total_invested": sum(h["total_invested"] for h in holdings_data),
                "total_profit_loss": sum(h["profit_loss"] for h in holdings_data),
                "holdings": holdings_data,
                "count": len(holdings_data)
            },
            "message": "Token holdings retrieved successfully"
        }
        
    except Exception as e:
        print(f"Failed to get token holdings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get token holdings: {str(e)}",
                "error_code": "HOLDINGS_ERROR"
            }
        )


@router.get("/investments/history")
async def get_investment_history(
    limit: int = Query(20, ge=1, le=100, description="Number of investments to return"),
    # current_user: User = Depends(get_current_user)
):
    """
    Get investment history with detailed information about each investment
    """
    try:
        current_user = {"id":"6872f4a6f0cdf587b2d8f06b"}
        invoices = await investment_strategy_service.get_user_invoices(current_user["id"])
        print(invoices)
        # Sort by creation date (newest first)
        invoices.sort(key=lambda x: x.created_at, reverse=True)
        
        # Limit results
        recent_invoices = invoices[:limit]
        
        investment_history = []
        for invoice in recent_invoices:
            # Get strategy details
            strategy = await investment_strategy_service.get_strategy(invoice.strategy_id) if invoice.strategy_id else None
            
            investment_data = {
                "invoice_id": invoice.id,
                "amount": invoice.amount,
                "crypto_tokens": invoice.crypto_tokens,
                "allocation": invoice.allocation,
                "reason": invoice.reason,
                "status": invoice.status,
                "payment_status": invoice.payment_status,
                "created_at": invoice.created_at.isoformat(),
                "expires_at": invoice.expires_at.isoformat(),
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "executed_at": invoice.executed_at.isoformat() if invoice.executed_at else None,
                "strategy_name": strategy.name if strategy else "Manual Investment",
                "strategy_type": strategy.strategy_type if strategy else None,
                "trigger_type": strategy.trigger_type if strategy else None
            }
            investment_history.append(investment_data)
        
        # Calculate summary statistics
        total_invested = sum(i["amount"] for i in investment_history if i["status"] in ["paid", "executed"])
        pending_amount = sum(i["amount"] for i in investment_history if i["status"] == "pending")
        executed_count = len([i for i in investment_history if i["status"] == "executed"])
        
        return {
            "success": True,
            "data": {
                "user_id": current_user["id"],
                "investments": investment_history,
                "summary": {
                    "total_invested": total_invested,
                    "pending_amount": pending_amount,
                    "executed_count": executed_count,
                    "total_count": len(investment_history)
                },
                "count": len(investment_history)
            },
            "message": "Investment history retrieved successfully"
        }
        
    except Exception as e:
        print(f"Failed to get investment history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get investment history: {str(e)}",
                "error_code": "INVESTMENT_HISTORY_ERROR"
            }
        )


@router.get("/performance")
async def get_portfolio_performance(
    period: str = Query("30d", description="Performance period: 7d, 30d, 90d, 1y, all"),
    current_user: User = Depends(get_current_user)
):
    """
    Get portfolio performance metrics over specified period
    """
    try:
        # Get investment history
        invoices = await investment_strategy_service.get_user_invoices(current_user.id)
        executed_invoices = [i for i in invoices if i.status == "executed"]
        
        # Calculate period filter
        now = datetime.utcnow()
        if period == "7d":
            start_date = now - timedelta(days=7)
        elif period == "30d":
            start_date = now - timedelta(days=30)
        elif period == "90d":
            start_date = now - timedelta(days=90)
        elif period == "1y":
            start_date = now - timedelta(days=365)
        else:  # all
            start_date = datetime.min
        
        # Filter investments by period
        period_investments = [i for i in executed_invoices if i.executed_at and i.executed_at >= start_date]
        
        # Calculate performance metrics
        total_invested = sum(i.amount for i in period_investments)
        total_investments = len(period_investments)
        
        # Get current portfolio value
        balances = await dashboard_service.get_wallet_balances(current_user.id)
        current_value = sum(balances.values())
        
        # Mock performance calculation (in real implementation, use historical data)
        performance_data = {
            "period": period,
            "total_invested": total_invested,
            "current_value": current_value,
            "total_return": current_value - total_invested,
            "return_percentage": ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
            "total_investments": total_investments,
            "average_investment": total_invested / total_investments if total_investments > 0 else 0,
            "best_performing_token": "BTC",  # Mock data
            "worst_performing_token": "DOGE",  # Mock data
            "volatility": 15.5,  # Mock volatility percentage
            "sharpe_ratio": 1.2,  # Mock Sharpe ratio
            "max_drawdown": -8.5,  # Mock max drawdown percentage
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat()
        }
        
        return {
            "success": True,
            "data": performance_data,
            "message": "Portfolio performance retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get portfolio performance: {str(e)}",
                "error_code": "PERFORMANCE_ERROR"
            }
        )


@router.get("/strategies/performance")
async def get_strategy_performance(current_user: User = Depends(get_current_user)):
    """
    Get performance of individual investment strategies
    """
    try:
        strategies = await investment_strategy_service.get_user_strategies(current_user.id)
        invoices = await investment_strategy_service.get_user_invoices(current_user.id)
        
        strategy_performance = []
        for strategy in strategies:
            # Get invoices for this strategy
            strategy_invoices = [i for i in invoices if i.strategy_id == strategy.id]
            executed_invoices = [i for i in strategy_invoices if i.status == "executed"]
            
            total_invested = sum(i.amount for i in executed_invoices)
            total_executions = len(executed_invoices)
            last_execution = max(i.executed_at for i in executed_invoices) if executed_invoices else None
            
            # Mock performance calculation
            current_value = total_invested * 1.15  # Mock 15% return
            
            performance = {
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                "strategy_type": strategy.strategy_type,
                "trigger_type": strategy.trigger_type,
                "is_active": strategy.is_active,
                "is_approved": strategy.is_approved,
                "total_invested": total_invested,
                "current_value": current_value,
                "total_return": current_value - total_invested,
                "return_percentage": ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
                "total_executions": total_executions,
                "last_execution": last_execution.isoformat() if last_execution else None,
                "created_at": strategy.created_at.isoformat(),
                "crypto_tokens": strategy.crypto_tokens,
                "allocation": strategy.allocation,
                "risk_level": strategy.risk_level
            }
            strategy_performance.append(performance)
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "strategies": strategy_performance,
                "summary": {
                    "total_strategies": len(strategies),
                    "active_strategies": len([s for s in strategies if s.is_active and s.is_approved]),
                    "total_invested": sum(s["total_invested"] for s in strategy_performance),
                    "total_return": sum(s["total_return"] for s in strategy_performance)
                }
            },
            "message": "Strategy performance retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get strategy performance: {str(e)}",
                "error_code": "STRATEGY_PERFORMANCE_ERROR"
            }
        )


@router.get("/transactions")
async def get_wallet_transactions(
    limit: int = Query(20, ge=1, le=100, description="Number of transactions to return"),
    transaction_type: Optional[str] = Query(None, description="Filter by type: investment, transfer, deposit, withdrawal"),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed wallet transactions
    """
    try:
        # Get transactions from dashboard service
        transactions = await dashboard_service.get_recent_transactions(current_user.id, limit)
        
        # Get investment invoices for additional transaction data
        invoices = await investment_strategy_service.get_user_invoices(current_user.id)
        
        # Combine and format transaction data
        formatted_transactions = []
        
        # Add investment transactions
        for invoice in invoices[:limit//2]:  # Include half investment transactions
            transaction = {
                "id": invoice.id,
                "type": "investment",
                "amount": invoice.amount,
                "currency": "INR",
                "status": invoice.status,
                "timestamp": invoice.created_at.isoformat(),
                "description": f"Investment: {invoice.reason}",
                "crypto_tokens": invoice.crypto_tokens,
                "allocation": invoice.allocation,
                "strategy_name": "Investment Strategy" if invoice.strategy_id else "Manual Investment"
            }
            formatted_transactions.append(transaction)
        
        # Add other transactions (from dashboard service)
        for tx in transactions[:limit//2]:
            transaction = {
                "id": tx.get("id", "unknown"),
                "type": tx.get("type", "transfer"),
                "amount": tx.get("amount", 0),
                "currency": tx.get("currency", "INR"),
                "status": "completed",
                "timestamp": tx.get("timestamp", datetime.utcnow().isoformat()),
                "description": tx.get("description", "Transaction"),
                "from": tx.get("from"),
                "to": tx.get("to")
            }
            formatted_transactions.append(transaction)
        
        # Sort by timestamp (newest first)
        formatted_transactions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply type filter if specified
        if transaction_type:
            formatted_transactions = [t for t in formatted_transactions if t["type"] == transaction_type]
        
        return {
            "success": True,
            "data": {
                "user_id": current_user.id,
                "transactions": formatted_transactions[:limit],
                "count": len(formatted_transactions[:limit]),
                "summary": {
                    "total_investments": len([t for t in formatted_transactions if t["type"] == "investment"]),
                    "total_transfers": len([t for t in formatted_transactions if t["type"] == "transfer"]),
                    "total_amount": sum(t["amount"] for t in formatted_transactions)
                }
            },
            "message": "Wallet transactions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get wallet transactions: {str(e)}",
                "error_code": "TRANSACTIONS_ERROR"
            }
        )


def _get_mock_token_price(token: str) -> float:
    """Get mock token price (in real implementation, fetch from price API)"""
    mock_prices = {
        "BTC": 45000.0,
        "ETH": 2800.0,
        "MATIC": 0.85,
        "SOL": 95.0,
        "DOGE": 0.08,
        "USDT": 1.0,
        "USDC": 1.0
    }
    return mock_prices.get(token, 1.0) 