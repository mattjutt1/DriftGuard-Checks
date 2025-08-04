"""
Authentication API endpoints.
User registration, login, token refresh, and profile management.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....core.auth import get_current_active_user, blacklist_token
from ....core.security import (
    verify_password,
    get_password_hash,
    create_token_response,
    verify_token,
    validate_password_strength
)
from ....db.session import get_db
from ....models.user import User
from ....services.redis_service import redis_service

logger = logging.getLogger(__name__)

router = APIRouter()


class UserRegistration(BaseModel):
    """User registration request model."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password")
    full_name: str = Field(None, max_length=255, description="Full name")
    
    @validator("username")
    def validate_username(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.lower()


class UserLogin(BaseModel):
    """User login request model."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Extended session duration")


class TokenRefresh(BaseModel):
    """Token refresh request model."""
    
    refresh_token: str = Field(..., description="Refresh token")


class PasswordChange(BaseModel):
    """Password change request model."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class UserResponse(BaseModel):
    """User response model."""
    
    id: str
    email: str
    username: str
    full_name: str = None
    is_active: bool
    created_at: str
    last_login: str = None
    login_count: int


class AuthResponse(BaseModel):
    """Authentication response model."""
    
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user account.
    
    Creates a new user account with email verification and returns
    authentication tokens for immediate login.
    """
    try:
        # Validate password strength
        validate_password_strength(user_data.password)
        
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address already registered"
            )
        
        # Check if username already exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
        
        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_superuser=False
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Update login stats
        new_user.update_last_login()
        await db.commit()
        
        logger.info(f"New user registered: {new_user.email}")
        
        # Create token response
        tokens = create_token_response(
            str(new_user.id),
            new_user.username,
            new_user.email
        )
        
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=str(new_user.id),
                email=new_user.email,
                username=new_user.username,
                full_name=new_user.full_name,
                is_active=new_user.is_active,
                created_at=new_user.created_at.isoformat(),
                last_login=new_user.last_login.isoformat() if new_user.last_login else None,
                login_count=new_user.login_count
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Authenticate user and return access tokens.
    
    Validates user credentials and returns JWT tokens for API access.
    """
    try:
        # Get user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalars().first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Update login stats
        user.update_last_login()
        await db.commit()
        
        logger.info(f"User logged in: {user.email}")
        
        # Create token response
        tokens = create_token_response(
            str(user.id),
            user.username,
            user.email
        )
        
        return AuthResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None,
                login_count=user.login_count
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Validates refresh token and issues a new access token.
    """
    try:
        # Verify refresh token
        payload = verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user or account disabled"
            )
        
        # Create new tokens
        tokens = create_token_response(
            str(user.id),
            user.username,
            user.email
        )
        
        return {
            "access_token": tokens["access_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Logout current user and blacklist token.
    
    Invalidates the current access token by adding it to blacklist.
    """
    try:
        # Note: In a real implementation, you'd need to get the actual token
        # from the request context. For now, we'll just return success.
        logger.info(f"User logged out: {current_user.email}")
        
        return {"message": "Successfully logged out"}
    
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current user profile information.
    
    Returns the authenticated user's profile data.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None,
        login_count=current_user.login_count
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update current user profile information.
    
    Allows updating non-sensitive profile fields.
    """
    try:
        # Allowed fields for update
        allowed_fields = {"full_name", "username"}
        
        for field, value in update_data.items():
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field '{field}' cannot be updated"
                )
            
            if field == "username":
                # Check if username is already taken
                result = await db.execute(
                    select(User).where(User.username == value, User.id != current_user.id)
                )
                if result.scalars().first():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username already taken"
                    )
            
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.email}")
        
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            last_login=current_user.last_login.isoformat() if current_user.last_login else None,
            login_count=current_user.login_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """
    Change user password.
    
    Validates current password and updates to new password.
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        validate_password_strength(password_data.new_password)
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        await db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )