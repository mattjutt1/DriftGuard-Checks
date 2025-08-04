"""
Authentication middleware and dependencies for FastAPI.
Provides JWT authentication, user authentication, and request validation.
"""

import logging
from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .security import verify_token, extract_user_id_from_token
from ..db.session import get_db
from ..models.user import User
from ..services.redis_service import redis_service

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class AuthenticationError(HTTPException):
    """Custom authentication error."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        AuthenticationError: If authentication fails
    """
    if not credentials:
        raise AuthenticationError("Missing authentication credentials")
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials, "access")
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationError("Invalid token: missing user ID")
        
        # Check if token is blacklisted (optional)
        blacklisted = await redis_service.get_cache(f"blacklist:{credentials.credentials}")
        if blacklisted:
            raise AuthenticationError("Token has been revoked")
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()
        
        if not user:
            raise AuthenticationError("User not found")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is disabled")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Authentication failed")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: The active user
        
    Raises:
        AuthenticationError: If user is not active
    """
    if not current_user.is_active:
        raise AuthenticationError("User account is disabled")
    
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current superuser.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: The superuser
        
    Raises:
        AuthorizationError: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise AuthorizationError("Insufficient permissions: admin access required")
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Optional[User]: The authenticated user or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


class RateLimitChecker:
    """Rate limiting dependency."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
    
    async def __call__(
        self,
        current_user: Optional[User] = Depends(get_optional_user)
    ):
        """
        Check rate limits for the current user or IP.
        
        Args:
            current_user: Current authenticated user (optional)
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Use user ID if authenticated, otherwise use IP (would need request context)
        identifier = str(current_user.id) if current_user else "anonymous"
        
        # Check minute limit
        minute_check = await redis_service.check_rate_limit(
            identifier, self.requests_per_minute, 60, "rate_limit_minute"
        )
        
        if not minute_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "limit": self.requests_per_minute,
                    "window": "1 minute",
                    "reset_time": minute_check["reset_time"]
                }
            )
        
        # Check hour limit
        hour_check = await redis_service.check_rate_limit(
            identifier, self.requests_per_hour, 3600, "rate_limit_hour"
        )
        
        if not hour_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "limit": self.requests_per_hour,
                    "window": "1 hour",
                    "reset_time": hour_check["reset_time"]
                }
            )
        
        # Check daily limit
        day_check = await redis_service.check_rate_limit(
            identifier, self.requests_per_day, 86400, "rate_limit_day"
        )
        
        if not day_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "limit": self.requests_per_day,
                    "window": "1 day",
                    "reset_time": day_check["reset_time"]
                }
            )


# Pre-configured rate limiters
standard_rate_limit = RateLimitChecker()
strict_rate_limit = RateLimitChecker(
    requests_per_minute=30,
    requests_per_hour=500,
    requests_per_day=5000
)
optimization_rate_limit = RateLimitChecker(
    requests_per_minute=10,
    requests_per_hour=100,
    requests_per_day=1000
)


async def blacklist_token(token: str, expires_in: int = 86400) -> bool:
    """
    Blacklist a JWT token (for logout).
    
    Args:
        token: The token to blacklist
        expires_in: Expiration time in seconds
        
    Returns:
        bool: True if successful
    """
    try:
        await redis_service.set_cache(
            f"blacklist:{token}",
            {"blacklisted_at": datetime.utcnow().isoformat()},
            expire=expires_in
        )
        return True
    except Exception as e:
        logger.error(f"Failed to blacklist token: {e}")
        return False


async def validate_api_key(api_key: str) -> bool:
    """
    Validate API key (if using API key authentication).
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if valid
    """
    # This could be implemented to support API key authentication
    # For now, we'll focus on JWT authentication
    return False


class APIKeyChecker:
    """API key authentication dependency (optional)."""
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> bool:
        """
        Check API key authentication.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            bool: True if valid API key
            
        Raises:
            AuthenticationError: If API key is invalid
        """
        if not credentials:
            raise AuthenticationError("Missing API key")
        
        if not await validate_api_key(credentials.credentials):
            raise AuthenticationError("Invalid API key")
        
        return True


# Export commonly used dependencies
__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_optional_user",
    "standard_rate_limit",
    "strict_rate_limit",
    "optimization_rate_limit",
    "RateLimitChecker",
    "blacklist_token",
    "AuthenticationError",
    "AuthorizationError",
]