"""
Salary API routes for processing salary data and generating investment strategies
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.models.salary import SalaryRequest, SalaryResponse
from src.services.salary_service import salary_service
from src.services.twitter_service import twitter_service
from src.api.dependencies import get_current_user
from src.models.user import User

router = APIRouter()


@router.post("/salary", response_model=SalaryResponse)
async def process_salary(request: SalaryRequest, current_user: User = Depends(get_current_user)):
    """
    Process salary data and generate investment strategy
    
    - **user_id**: User ID who received salary (from token)
    - **amount**: Salary amount in INR
    - **employer**: Employer name
    - **date**: Salary date
    - Returns salary ID, strategy ID, and generated investment strategy
    """
    try:
        # Use authenticated user's ID instead of request user_id
        request.user_id = current_user.id
        
        # Convert request to dict
        salary_data = request.dict()
        
        # Process salary and generate strategy
        result = await salary_service.process_salary_and_generate_strategy(salary_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": result["message"],
                    "error_code": "SALARY_PROCESSING_FAILED"
                }
            )
        
        return SalaryResponse(
            success=True,
            salary_id=result["salary_id"],
            strategy_id=result["strategy_id"],
            message=result["message"],
            strategy=result.get("strategy")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_ERROR"
            }
        )


@router.get("/trending-tokens")
async def get_trending_tokens():
    """
    Get current trending crypto tokens
    
    Returns the latest trending tokens from Twitter/X
    """
    try:
        tokens = await twitter_service.get_trending_tokens()
        
        return {
            "success": True,
            "tokens": tokens,
            "count": len(tokens),
            "timestamp": "current"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get trending tokens: {str(e)}",
                "error_code": "TRENDING_TOKENS_ERROR"
            }
        )


@router.get("/trending-tokens/history")
async def get_trending_tokens_history(hours: int = 24):
    """
    Get trending tokens history
    
    - **hours**: Number of hours to look back (default: 24)
    - Returns trending tokens history for the specified period
    """
    try:
        history = await twitter_service.get_trending_tokens_history(hours)
        
        return {
            "success": True,
            "history": history,
            "hours": hours,
            "count": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get trending tokens history: {str(e)}",
                "error_code": "HISTORY_ERROR"
            }
        )


@router.get("/trending-tokens/most-trending")
async def get_most_trending_tokens(hours: int = 24):
    """
    Get most frequently trending tokens
    
    - **hours**: Number of hours to analyze (default: 24)
    - Returns tokens ranked by frequency of appearance
    """
    try:
        most_trending = await twitter_service.get_most_trending_tokens(hours)
        
        return {
            "success": True,
            "most_trending": most_trending,
            "hours": hours,
            "top_tokens": list(most_trending.keys())[:5]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get most trending tokens: {str(e)}",
                "error_code": "ANALYSIS_ERROR"
            }
        )


@router.get("/user/{user_id}/salaries")
async def get_user_salaries(user_id: str, limit: int = 10, current_user: User = Depends(get_current_user)):
    """
    Get recent salaries for a user
    
    - **user_id**: User ID (must match authenticated user)
    - **limit**: Number of records to return (default: 10)
    - Returns recent salary records for the user
    """
    try:
        # Ensure user can only access their own data
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only access own data"
            )
        
        salaries = await salary_service.get_user_salaries(user_id, limit)
        
        return {
            "success": True,
            "user_id": user_id,
            "salaries": [dict(salary) for salary in salaries],
            "count": len(salaries)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get user salaries: {str(e)}",
                "error_code": "USER_SALARIES_ERROR"
            }
        )


@router.get("/user/{user_id}/strategies")
async def get_user_strategies(user_id: str, limit: int = 10, current_user: User = Depends(get_current_user)):
    """
    Get recent investment strategies for a user
    
    - **user_id**: User ID (must match authenticated user)
    - **limit**: Number of records to return (default: 10)
    - Returns recent investment strategies for the user
    """
    try:
        # Ensure user can only access their own data
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Can only access own data"
            )
        
        strategies = await salary_service.get_user_strategies(user_id, limit)
        
        return {
            "success": True,
            "user_id": user_id,
            "strategies": [dict(strategy) for strategy in strategies],
            "count": len(strategies)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Failed to get user strategies: {str(e)}",
                "error_code": "USER_STRATEGIES_ERROR"
            }
        ) 