"""Response caching system for LLM providers."""

import hashlib
import json
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Cache entry with content and metadata."""
    key: str
    content: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int
    provider: str
    model: str
    content_hash: str


class LLMResponseCache:
    """Content-hash based caching system for LLM responses."""

    def __init__(self, db_path: str = None, default_ttl_hours: int = 24):
        """
        Initialize the cache.

        Args:
            db_path: Path to SQLite database file
            default_ttl_hours: Default time-to-live in hours (0 = no expiration)
        """
        self.db_path = db_path or self._get_default_db_path()
        self.default_ttl_hours = default_ttl_hours
        self._init_database()

    def _get_default_db_path(self) -> str:
        """Get default database path."""
        # Use XDG_CACHE_HOME or fallback to ~/.cache
        cache_dir = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        promptops_dir = Path(cache_dir) / "promptops"
        promptops_dir.mkdir(parents=True, exist_ok=True)
        return str(promptops_dir / "llm_cache.db")

    def _init_database(self):
        """Initialize SQLite database with cache table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    content_hash TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    response_content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    hit_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_content_hash
                ON cache_entries (content_hash)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at
                ON cache_entries (expires_at)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_provider_model
                ON cache_entries (provider, model)
            """)

    def _compute_cache_key(self, messages: List[Dict[str, str]],
                          provider: str, model: str, **kwargs: Any) -> str:
        """
        Compute cache key from request parameters.

        Args:
            messages: Chat messages
            provider: Provider name
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Hex-encoded SHA256 hash as cache key
        """
        # Create deterministic representation of the request
        cache_data = {
            "messages": messages,
            "provider": provider,
            "model": model,
            "kwargs": kwargs
        }

        # Sort keys for consistent hashing
        cache_json = json.dumps(cache_data, sort_keys=True, separators=(',', ':'))

        # Compute SHA256 hash
        return hashlib.sha256(cache_json.encode('utf-8')).hexdigest()

    def _compute_content_hash(self, response: Dict[str, Any]) -> str:
        """
        Compute content hash of response for deduplication.

        Args:
            response: LLM response dictionary

        Returns:
            Hex-encoded SHA256 hash of response content
        """
        # Extract just the content for hashing (ignore metadata like model, provider, timestamps)
        # This allows deduplication across different models/providers that return same content
        content_data = {
            "content": response.get("content", "")
        }

        content_json = json.dumps(content_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(content_json.encode('utf-8')).hexdigest()

    def get(self, messages: List[Dict[str, str]], provider: str, model: str,
           **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available and not expired.

        Args:
            messages: Chat messages
            provider: Provider name
            model: Model name
            **kwargs: Additional parameters

        Returns:
            Cached response or None if not found/expired
        """
        key = self._compute_cache_key(messages, provider, model, **kwargs)
        now = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT response_content, expires_at, hit_count
                FROM cache_entries
                WHERE key = ?
                AND (expires_at IS NULL OR expires_at > ?)
            """, (key, now.isoformat()))

            result = cursor.fetchone()
            if not result:
                return None

            response_json, expires_at, hit_count = result

            # Update hit count and last accessed
            conn.execute("""
                UPDATE cache_entries
                SET hit_count = ?, last_accessed = ?
                WHERE key = ?
            """, (hit_count + 1, now.isoformat(), key))

            # Parse and return response
            try:
                response = json.loads(response_json)
                # Add cache metadata
                response["_cache_hit"] = True
                response["_cache_key"] = key
                return response
            except json.JSONDecodeError:
                # Invalid cached data, ignore
                return None

    def put(self, messages: List[Dict[str, str]], provider: str, model: str,
           response: Dict[str, Any], ttl_hours: Optional[int] = None, **kwargs: Any):
        """
        Cache a response.

        Args:
            messages: Chat messages
            provider: Provider name
            model: Model name
            response: Response to cache
            ttl_hours: Time-to-live in hours (None = use default, 0 = no expiration)
            **kwargs: Additional parameters
        """
        key = self._compute_cache_key(messages, provider, model, **kwargs)
        content_hash = self._compute_content_hash(response)
        now = datetime.utcnow()

        # Calculate expiration time
        if ttl_hours is None:
            ttl_hours = self.default_ttl_hours

        expires_at = None
        if ttl_hours > 0:
            expires_at = now + timedelta(hours=ttl_hours)

        # Remove cache metadata before storing
        clean_response = {k: v for k, v in response.items() if not k.startswith("_cache")}
        response_json = json.dumps(clean_response)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO cache_entries
                (key, content_hash, provider, model, response_content,
                 created_at, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (key, content_hash, provider, model, response_json,
                  now.isoformat(), expires_at.isoformat() if expires_at else None,
                  now.isoformat()))

    def invalidate(self, messages: List[Dict[str, str]], provider: str, model: str,
                  **kwargs: Any) -> bool:
        """
        Remove a specific entry from cache.

        Args:
            messages: Chat messages
            provider: Provider name
            model: Model name
            **kwargs: Additional parameters

        Returns:
            True if entry was found and removed
        """
        key = self._compute_cache_key(messages, provider, model, **kwargs)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            return cursor.rowcount > 0

    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM cache_entries
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (now.isoformat(),))

            return cursor.rowcount

    def clear_provider(self, provider: str, model: str = None) -> int:
        """
        Clear cache entries for a specific provider/model.

        Args:
            provider: Provider name
            model: Optional model name (if None, clears all models for provider)

        Returns:
            Number of entries removed
        """
        with sqlite3.connect(self.db_path) as conn:
            if model is not None:
                cursor = conn.execute("""
                    DELETE FROM cache_entries
                    WHERE provider = ? AND model = ?
                """, (provider, model))
            else:
                cursor = conn.execute("""
                    DELETE FROM cache_entries
                    WHERE provider = ?
                """, (provider,))

            return cursor.rowcount

    def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries removed
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM cache_entries")
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        now = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            # Total entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            total_entries = cursor.fetchone()[0]

            # Expired entries
            cursor = conn.execute("""
                SELECT COUNT(*) FROM cache_entries
                WHERE expires_at IS NOT NULL AND expires_at <= ?
            """, (now.isoformat(),))
            expired_entries = cursor.fetchone()[0]

            # Total hits
            cursor = conn.execute("SELECT COALESCE(SUM(hit_count), 0) FROM cache_entries")
            total_hits = cursor.fetchone()[0]

            # By provider
            cursor = conn.execute("""
                SELECT provider, model, COUNT(*), COALESCE(SUM(hit_count), 0)
                FROM cache_entries
                GROUP BY provider, model
            """)
            provider_stats = []
            for provider, model, count, hits in cursor.fetchall():
                provider_stats.append({
                    "provider": provider,
                    "model": model,
                    "entries": count,
                    "hits": hits
                })

            # Storage info
            cursor = conn.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor = conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            storage_bytes = page_count * page_size

            return {
                "total_entries": total_entries,
                "active_entries": total_entries - expired_entries,
                "expired_entries": expired_entries,
                "total_hits": total_hits,
                "hit_rate": total_hits / max(total_entries, 1),
                "storage_bytes": storage_bytes,
                "storage_mb": storage_bytes / (1024 * 1024),
                "provider_stats": provider_stats,
                "database_path": self.db_path
            }

    def find_similar(self, content_hash: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find entries with the same content hash (deduplication).

        Args:
            content_hash: Content hash to search for
            limit: Maximum number of results

        Returns:
            List of cache entries with same content
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, provider, model, created_at, hit_count, last_accessed
                FROM cache_entries
                WHERE content_hash = ?
                ORDER BY hit_count DESC, created_at DESC
                LIMIT ?
            """, (content_hash, limit))

            results = []
            for row in cursor.fetchall():
                key, provider, model, created_at, hit_count, last_accessed = row
                results.append({
                    "key": key,
                    "provider": provider,
                    "model": model,
                    "created_at": created_at,
                    "hit_count": hit_count,
                    "last_accessed": last_accessed,
                    "content_hash": content_hash
                })

            return results

    def cleanup_by_size(self, max_entries: int) -> int:
        """
        Remove least recently used entries to stay under size limit.

        Args:
            max_entries: Maximum number of entries to keep

        Returns:
            Number of entries removed
        """
        with sqlite3.connect(self.db_path) as conn:
            # Count current entries
            cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
            current_count = cursor.fetchone()[0]

            if current_count <= max_entries:
                return 0

            entries_to_remove = current_count - max_entries

            # Remove least recently used entries
            cursor = conn.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY
                        CASE
                            WHEN last_accessed IS NULL THEN created_at
                            ELSE last_accessed
                        END ASC
                    LIMIT ?
                )
            """, (entries_to_remove,))

            return cursor.rowcount
