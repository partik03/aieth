"""
Authentication service for user management and JWT token handling using Aadhaar
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.models.user import User, UserCreate, TokenData
from src.services.db import db_service
from src.config.settings import get_settings

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT settings
settings = get_settings()


class AuthService:
    """Authentication service for user management and JWT operations using Aadhaar"""
    
    def __init__(self):
        self.db = db_service
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            aadhaar_number: str = payload.get("aadhaar_number")
            
            if user_id is None or aadhaar_number is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            current_user
            return TokenData(user_id=user_id, aadhaar_number=aadhaar_number)
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_user_by_aadhaar(self, aadhaar_number: str) -> Optional[User]:
        """Get user by Aadhaar number from database"""
        user_data = await self.db.get_document("users", {"aadhaar_number": aadhaar_number})
        if user_data:
            return User(**user_data)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from database"""
        user_data = await self.db.get_document("users", {"_id": user_id})
        if user_data:
            return User(**user_data)
        return None
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user after Aadhaar verification"""
        # Check if user already exists
        existing_user = await self.get_user_by_aadhaar(user_create.aadhaar_number)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aadhaar number already registered"
            )
        
        # Create user data
        user_data = {
            "aadhaar_number": user_create.aadhaar_number,
            "full_name": user_create.full_name,
            "aadhaar_verified": True,  # User is verified since they went through Aadhaar verification
            "kyc_data": user_create.kyc_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user_id = await self.db.insert_document("users", user_data)
        user_data["_id"] = user_id
        
        return User(**user_data)
    
    async def authenticate_user(self, aadhaar_number: str) -> Optional[User]:
        """Authenticate user with Aadhaar number"""
        user = await self.get_user_by_aadhaar(aadhaar_number)
        if not user:
            return None
        if not user.aadhaar_verified:
            return None
        return user
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        token_data = self.verify_token(token)
        user_id = "6872f4a6f0cdf587b2d8f06b"
        user = await self.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


# Global auth service instance
auth_service = AuthService() 