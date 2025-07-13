"""
Authentication API routes for user registration and login using Aadhaar
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import UserCreate, UserLogin, UserResponse, Token
from src.services.auth import auth_service, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    Register a new user after Aadhaar verification
    
    - **aadhaar_number**: User's Aadhaar number (format: xxxx-xxxx-xxxx)
    - **full_name**: User's full name
    - **kyc_data**: KYC data from Aadhaar verification (optional)
    """
    try:
        user = await auth_service.create_user(user_create)
        return UserResponse(
            id=user.id,
            aadhaar_number=user.aadhaar_number,
            full_name=user.full_name,
            aadhaar_verified=user.aadhaar_verified,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin):
    """
    Login user with Aadhaar number and return JWT access token
    
    - **aadhaar_number**: User's Aadhaar number (format: xxxx-xxxx-xxxx)
    """
    try:
        user = await auth_service.authenticate_user(user_login.aadhaar_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Aadhaar number or user not verified",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.id, "aadhaar_number": user.aadhaar_number},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/login-form", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login using OAuth2 form (for Swagger UI compatibility)
    
    This endpoint accepts form data with username (Aadhaar number)
    """
    try:
        user = await auth_service.authenticate_user(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Aadhaar number or user not verified",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=auth_service.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.id, "aadhaar_number": user.aadhaar_number},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(oauth2_scheme)):
    """
    Get current user information
    
    Requires valid JWT token in Authorization header
    """
    try:
        user = await auth_service.get_current_user(current_user)
        return UserResponse(
            id=user.id,
            aadhaar_number=user.aadhaar_number,
            full_name=user.full_name,
            aadhaar_verified=user.aadhaar_verified,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        ) 