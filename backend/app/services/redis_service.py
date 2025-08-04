"""
Redis service for caching optimization results and user sessions.
Provides async Redis operations with connection pooling and error handling.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from ..core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """
    Async Redis service for caching and session management.
    
    Provides high-level operations for:
    - Optimization result caching
    - User session management
    - Rate limiting data
    - Background task status
    """
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool and client."""
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=20,
                retry_on_timeout=True,
                decode_responses=True,
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            self._initialized = True
            
            logger.info("Redis service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis service: {e}")
            raise
    
    async def close(self) -> None:
        """Close Redis connections."""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False
        logger.info("Redis service closed")
    
    def _ensure_initialized(self) -> None:
        """Ensure Redis service is initialized."""
        if not self._initialized or not self.client:
            raise RuntimeError("Redis service not initialized. Call initialize() first.")
    
    async def ping(self) -> bool:
        """Test Redis connection."""
        try:
            self._ensure_initialized()
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    # Cache operations
    async def set_cache(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """
        Set a cached value with optional expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (default: settings.REDIS_CACHE_TTL)
            serialize: Whether to JSON serialize the value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._ensure_initialized()
            
            if serialize:
                value = json.dumps(value, default=str)
            
            ttl = expire or settings.REDIS_CACHE_TTL
            
            result = await self.client.setex(key, ttl, value)
            return result
            
        except Exception as e:
            logger.error(f"Failed to set cache key '{key}': {e}")
            return False
    
    async def get_cache(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """
        Get a cached value.
        
        Args:
            key: Cache key
            deserialize: Whether to JSON deserialize the value
            default: Default value if key not found
            
        Returns:
            Any: Cached value or default
        """
        try:
            self._ensure_initialized()
            
            value = await self.client.get(key)
            
            if value is None:
                return default
            
            if deserialize:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to deserialize cache value for key '{key}'")
                    return value
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get cache key '{key}': {e}")
            return default
    
    async def delete_cache(self, key: str) -> bool:
        """Delete a cached value."""
        try:
            self._ensure_initialized()
            result = await self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key '{key}': {e}")
            return False
    
    async def exists_cache(self, key: str) -> bool:
        """Check if a cache key exists."""
        try:
            self._ensure_initialized()
            result = await self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check cache key '{key}': {e}")
            return False
    
    # Optimization result caching
    async def cache_optimization_result(
        self,
        task_id: str,
        result: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """Cache optimization result with metadata."""
        cache_data = {
            "result": result,
            "cached_at": datetime.utcnow().isoformat(),
            "task_id": task_id,
        }
        
        key = f"optimization:{task_id}"
        return await self.set_cache(key, cache_data, expire)
    
    async def get_optimization_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get cached optimization result."""
        key = f"optimization:{task_id}"
        return await self.get_cache(key)
    
    # User session management
    async def set_user_session(
        self,
        session_id: str,
        user_data: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """Set user session data."""
        session_data = {
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
        }
        
        key = f"session:{session_id}"
        ttl = expire or settings.REDIS_SESSION_TTL
        return await self.set_cache(key, session_data, ttl)
    
    async def get_user_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data."""
        key = f"session:{session_id}"
        return await self.get_cache(key)
    
    async def delete_user_session(self, session_id: str) -> bool:
        """Delete user session."""
        key = f"session:{session_id}"
        return await self.delete_cache(key)
    
    # Background task status
    async def set_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Set background task status."""
        task_data = {
            "task_id": task_id,
            "status": status,  # pending, running, completed, failed
            "progress": progress,  # 0-100
            "message": message,
            "result": result,
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        key = f"task:{task_id}"
        return await self.set_cache(key, task_data, 3600)  # 1 hour TTL
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get background task status."""
        key = f"task:{task_id}"
        return await self.get_cache(key)
    
    # Rate limiting
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window: int,
        prefix: str = "rate_limit"
    ) -> Dict[str, Any]:
        """
        Check rate limit for an identifier.
        
        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
            prefix: Redis key prefix
            
        Returns:
            Dict with rate limit info
        """
        try:
            self._ensure_initialized()
            
            key = f"{prefix}:{identifier}"
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window)
            
            # Use a sliding window log approach
            pipe = self.client.pipeline()
            
            # Remove expired entries
            await pipe.zremrangebyscore(key, 0, window_start.timestamp())
            
            # Count current requests
            current_count = await pipe.zcard(key)
            
            if current_count < limit:
                # Add current request
                await pipe.zadd(key, {str(now.timestamp()): now.timestamp()})
                await pipe.expire(key, window)
                
                return {
                    "allowed": True,
                    "current_count": current_count + 1,
                    "limit": limit,
                    "window": window,
                    "reset_time": (now + timedelta(seconds=window)).isoformat(),
                }
            else:
                return {
                    "allowed": False,
                    "current_count": current_count,
                    "limit": limit,
                    "window": window,
                    "reset_time": (now + timedelta(seconds=window)).isoformat(),
                }
                
        except Exception as e:
            logger.error(f"Rate limit check failed for {identifier}: {e}")
            # On error, allow the request (fail open)
            return {
                "allowed": True,
                "current_count": 0,
                "limit": limit,
                "window": window,
                "error": str(e),
            }
    
    # Utility methods
    async def get_keys_pattern(self, pattern: str) -> List[str]:
        """Get keys matching a pattern."""
        try:
            self._ensure_initialized()
            keys = await self.client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"Failed to get keys with pattern '{pattern}': {e}")
            return []
    
    async def clear_cache_pattern(self, pattern: str) -> int:
        """Clear all cache keys matching a pattern."""
        try:
            self._ensure_initialized()
            keys = await self.get_keys_pattern(pattern)
            if keys:
                result = await self.client.delete(*keys)
                return result
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern '{pattern}': {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            self._ensure_initialized()
            info = await self.client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# Global Redis service instance
redis_service = RedisService()