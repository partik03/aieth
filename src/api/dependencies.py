"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.models.user import User
from src.services.auth import auth_service, oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get current authenticated user
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    return await auth_service.get_current_user(token)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get current active user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    # For now, all users are considered active
    # You can add additional checks here if needed
    return current_user


async def require_aadhaar_verification(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require Aadhaar verification
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user if Aadhaar verified
        
    Raises:
        HTTPException: If user is not Aadhaar verified
    """
    if not current_user.aadhaar_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aadhaar verification required for this operation"
        )
    return current_user 