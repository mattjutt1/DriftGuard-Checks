"""Tests for LLM response caching system."""

import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from promptops.cache import LLMResponseCache, CacheEntry


class TestCacheInitialization:
    """Test cache initialization and setup."""

    def test_init_with_default_path(self):
        """Test cache initializes with default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            with pytest.MonkeyPatch.context() as mp:
                mp.setenv("XDG_CACHE_HOME", temp_dir)

                cache = LLMResponseCache()

                # Should create database in XDG_CACHE_HOME/promptops/
                expected_db = Path(temp_dir) / "promptops" / "llm_cache.db"
                assert Path(cache.db_path) == expected_db
                assert Path(cache.db_path).exists()

    def test_init_with_custom_path(self):
        """Test cache with custom database path."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            cache = LLMResponseCache(db_path=temp_db.name)
            assert cache.db_path == temp_db.name

    def test_init_with_custom_ttl(self):
        """Test cache with custom default TTL."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            cache = LLMResponseCache(db_path=temp_db.name, default_ttl_hours=48)
            assert cache.default_ttl_hours == 48

    def test_database_tables_created(self):
        """Test that cache table is created."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            cache = LLMResponseCache(db_path=temp_db.name)

            # Check that table exists with correct schema
            with sqlite3.connect(temp_db.name) as conn:
                cursor = conn.execute("""
                    SELECT sql FROM sqlite_master
                    WHERE type='table' AND name='cache_entries'
                """)
                schema = cursor.fetchone()[0]

                # Check for required columns
                assert "key TEXT PRIMARY KEY" in schema
                assert "content_hash TEXT NOT NULL" in schema
                assert "provider TEXT NOT NULL" in schema
                assert "model TEXT NOT NULL" in schema
                assert "response_content TEXT NOT NULL" in schema


class TestCacheKeyGeneration:
    """Test cache key computation."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_cache_key_deterministic(self, cache):
        """Test that cache keys are deterministic."""
        messages = [{"role": "user", "content": "Hello"}]

        key1 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")
        key2 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length

    def test_cache_key_different_messages(self, cache):
        """Test that different messages produce different keys."""
        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "Goodbye"}]

        key1 = cache._compute_cache_key(messages1, "openai", "gpt-4o-mini")
        key2 = cache._compute_cache_key(messages2, "openai", "gpt-4o-mini")

        assert key1 != key2

    def test_cache_key_different_provider(self, cache):
        """Test that different providers produce different keys."""
        messages = [{"role": "user", "content": "Hello"}]

        key1 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")
        key2 = cache._compute_cache_key(messages, "anthropic", "claude-3-5-sonnet-20241022")

        assert key1 != key2

    def test_cache_key_with_kwargs(self, cache):
        """Test that kwargs affect cache key."""
        messages = [{"role": "user", "content": "Hello"}]

        key1 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")
        key2 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini", temperature=0.7)

        assert key1 != key2

    def test_cache_key_kwargs_order_independent(self, cache):
        """Test that kwargs order doesn't affect cache key."""
        messages = [{"role": "user", "content": "Hello"}]

        key1 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini", temperature=0.7, max_tokens=100)
        key2 = cache._compute_cache_key(messages, "openai", "gpt-4o-mini", max_tokens=100, temperature=0.7)

        assert key1 == key2


class TestContentHashing:
    """Test content hash computation for deduplication."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_content_hash_deterministic(self, cache):
        """Test that content hashes are deterministic."""
        response = {
            "content": "Hello world",
            "model": "gpt-4o-mini",
            "provider": "openai",
            "usage": {"tokens": 100}
        }

        hash1 = cache._compute_content_hash(response)
        hash2 = cache._compute_content_hash(response)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_content_hash_same_content_different_metadata(self, cache):
        """Test that metadata differences don't affect content hash."""
        response1 = {
            "content": "Hello world",
            "model": "gpt-4o-mini",
            "provider": "openai",
            "usage": {"tokens": 100},
            "created_at": "2025-01-01T00:00:00Z"
        }

        response2 = {
            "content": "Hello world",
            "model": "gpt-4o-mini",
            "provider": "openai",
            "usage": {"tokens": 200},  # Different metadata
            "created_at": "2025-01-02T00:00:00Z"
        }

        hash1 = cache._compute_content_hash(response1)
        hash2 = cache._compute_content_hash(response2)

        # Should be same because core content is same
        assert hash1 == hash2

    def test_content_hash_different_content(self, cache):
        """Test that different content produces different hashes."""
        response1 = {
            "content": "Hello world",
            "model": "gpt-4o-mini",
            "provider": "openai"
        }

        response2 = {
            "content": "Goodbye world",
            "model": "gpt-4o-mini",
            "provider": "openai"
        }

        hash1 = cache._compute_content_hash(response1)
        hash2 = cache._compute_content_hash(response2)

        assert hash1 != hash2


class TestCacheOperations:
    """Test cache get/put operations."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name, default_ttl_hours=24)

    def test_put_and_get_basic(self, cache):
        """Test basic put and get operations."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {
            "content": "Hello! How can I help?",
            "model": "gpt-4o-mini",
            "provider": "openai",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }

        # Store response
        cache.put(messages, "openai", "gpt-4o-mini", response)

        # Retrieve response
        cached = cache.get(messages, "openai", "gpt-4o-mini")

        assert cached is not None
        assert cached["content"] == response["content"]
        assert cached["model"] == response["model"]
        assert cached["provider"] == response["provider"]
        assert cached["_cache_hit"] is True
        assert "_cache_key" in cached

    def test_get_nonexistent(self, cache):
        """Test getting non-existent cache entry."""
        messages = [{"role": "user", "content": "Not cached"}]

        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is None

    def test_put_overwrites_existing(self, cache):
        """Test that putting overwrites existing entries."""
        messages = [{"role": "user", "content": "Hello"}]

        # Put first response
        response1 = {"content": "Response 1", "model": "gpt-4o-mini", "provider": "openai"}
        cache.put(messages, "openai", "gpt-4o-mini", response1)

        # Put second response (overwrite)
        response2 = {"content": "Response 2", "model": "gpt-4o-mini", "provider": "openai"}
        cache.put(messages, "openai", "gpt-4o-mini", response2)

        # Should get the second response
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached["content"] == "Response 2"

    def test_put_with_custom_ttl(self, cache):
        """Test putting with custom TTL."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        # Put with 1 hour TTL
        cache.put(messages, "openai", "gpt-4o-mini", response, ttl_hours=1)

        # Should be retrievable
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is not None

    def test_put_with_zero_ttl(self, cache):
        """Test putting with zero TTL (no expiration)."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        # Put with no expiration
        cache.put(messages, "openai", "gpt-4o-mini", response, ttl_hours=0)

        # Should be retrievable
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is not None

    def test_hit_count_increment(self, cache):
        """Test that hit count is incremented on retrieval."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        cache.put(messages, "openai", "gpt-4o-mini", response)

        # Get multiple times
        cache.get(messages, "openai", "gpt-4o-mini")
        cache.get(messages, "openai", "gpt-4o-mini")
        cache.get(messages, "openai", "gpt-4o-mini")

        # Check hit count in database
        with sqlite3.connect(cache.db_path) as conn:
            cursor = conn.execute("SELECT hit_count FROM cache_entries")
            hit_count = cursor.fetchone()[0]
            assert hit_count == 3


class TestCacheExpiration:
    """Test cache expiration functionality."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name, default_ttl_hours=24)

    def test_expired_entries_not_returned(self, cache):
        """Test that expired entries are not returned."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        # Manually insert expired entry
        key = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")
        content_hash = cache._compute_content_hash(response)
        past_time = datetime.utcnow() - timedelta(hours=1)

        with sqlite3.connect(cache.db_path) as conn:
            conn.execute("""
                INSERT INTO cache_entries
                (key, content_hash, provider, model, response_content,
                 created_at, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                key, content_hash, "openai", "gpt-4o-mini",
                json.dumps(response),
                past_time.isoformat(),
                past_time.isoformat(),  # Already expired
                past_time.isoformat()
            ))

        # Should not retrieve expired entry
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is None

    def test_clear_expired(self, cache):
        """Test clearing expired entries."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        # Put entry that will expire soon
        cache.put(messages, "openai", "gpt-4o-mini", response, ttl_hours=1)

        # Manually set expiration to past
        with sqlite3.connect(cache.db_path) as conn:
            past_time = datetime.utcnow() - timedelta(hours=1)
            conn.execute("""
                UPDATE cache_entries
                SET expires_at = ?
            """, (past_time.isoformat(),))

        # Clear expired
        removed = cache.clear_expired()
        assert removed == 1

        # Verify entry is gone
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is None


class TestCacheInvalidation:
    """Test cache invalidation and clearing."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_invalidate_specific_entry(self, cache):
        """Test invalidating a specific cache entry."""
        messages = [{"role": "user", "content": "Hello"}]
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        cache.put(messages, "openai", "gpt-4o-mini", response)

        # Verify it's cached
        assert cache.get(messages, "openai", "gpt-4o-mini") is not None

        # Invalidate
        removed = cache.invalidate(messages, "openai", "gpt-4o-mini")
        assert removed is True

        # Verify it's gone
        assert cache.get(messages, "openai", "gpt-4o-mini") is None

    def test_invalidate_nonexistent(self, cache):
        """Test invalidating non-existent entry."""
        messages = [{"role": "user", "content": "Not cached"}]

        removed = cache.invalidate(messages, "openai", "gpt-4o-mini")
        assert removed is False

    def test_clear_provider(self, cache):
        """Test clearing entries for specific provider."""
        # Add entries for different providers
        messages = [{"role": "user", "content": "Hello"}]
        openai_response = {"content": "OpenAI", "model": "gpt-4o-mini", "provider": "openai"}
        anthropic_response = {"content": "Anthropic", "model": "claude-3-5-sonnet-20241022", "provider": "anthropic"}

        cache.put(messages, "openai", "gpt-4o-mini", openai_response)
        cache.put(messages, "anthropic", "claude-3-5-sonnet-20241022", anthropic_response)

        # Clear OpenAI entries
        removed = cache.clear_provider("openai")
        assert removed == 1

        # OpenAI should be gone, Anthropic should remain
        assert cache.get(messages, "openai", "gpt-4o-mini") is None
        assert cache.get(messages, "anthropic", "claude-3-5-sonnet-20241022") is not None

    def test_clear_provider_and_model(self, cache):
        """Test clearing entries for specific provider and model."""
        messages = [{"role": "user", "content": "Hello"}]

        # Add multiple models for same provider
        cache.put(messages, "openai", "gpt-4o-mini", {"content": "Mini", "model": "gpt-4o-mini", "provider": "openai"})
        cache.put(messages, "openai", "gpt-4o", {"content": "Regular", "model": "gpt-4o", "provider": "openai"})

        # Clear only gpt-4o-mini
        removed = cache.clear_provider("openai", "gpt-4o-mini")
        assert removed == 1

        # Only gpt-4o-mini should be gone
        assert cache.get(messages, "openai", "gpt-4o-mini") is None
        assert cache.get(messages, "openai", "gpt-4o") is not None

    def test_clear_all(self, cache):
        """Test clearing all cache entries."""
        # Add multiple entries
        messages = [{"role": "user", "content": "Hello"}]
        cache.put(messages, "openai", "gpt-4o-mini", {"content": "1", "model": "gpt-4o-mini", "provider": "openai"})
        cache.put(messages, "anthropic", "claude-3-5-sonnet-20241022", {"content": "2", "model": "claude-3-5-sonnet-20241022", "provider": "anthropic"})

        # Clear all
        removed = cache.clear_all()
        assert removed == 2

        # All should be gone
        assert cache.get(messages, "openai", "gpt-4o-mini") is None
        assert cache.get(messages, "anthropic", "claude-3-5-sonnet-20241022") is None


class TestCacheStatistics:
    """Test cache statistics functionality."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_stats_empty_cache(self, cache):
        """Test statistics for empty cache."""
        stats = cache.get_stats()

        assert stats["total_entries"] == 0
        assert stats["active_entries"] == 0
        assert stats["expired_entries"] == 0
        assert stats["total_hits"] == 0
        assert stats["hit_rate"] == 0.0
        assert stats["provider_stats"] == []

    def test_stats_with_entries(self, cache):
        """Test statistics with cache entries."""
        messages = [{"role": "user", "content": "Hello"}]

        # Add entries and generate hits
        cache.put(messages, "openai", "gpt-4o-mini", {"content": "1", "model": "gpt-4o-mini", "provider": "openai"})
        cache.put(messages, "anthropic", "claude-3-5-sonnet-20241022", {"content": "2", "model": "claude-3-5-sonnet-20241022", "provider": "anthropic"})

        # Generate some hits
        cache.get(messages, "openai", "gpt-4o-mini")
        cache.get(messages, "openai", "gpt-4o-mini")

        stats = cache.get_stats()

        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["total_hits"] == 2
        assert stats["hit_rate"] == 1.0  # 2 hits / 2 entries

        # Check provider breakdown
        provider_stats = {(ps["provider"], ps["model"]): ps for ps in stats["provider_stats"]}
        assert ("openai", "gpt-4o-mini") in provider_stats
        assert ("anthropic", "claude-3-5-sonnet-20241022") in provider_stats
        assert provider_stats[("openai", "gpt-4o-mini")]["hits"] == 2
        assert provider_stats[("anthropic", "claude-3-5-sonnet-20241022")]["hits"] == 0


class TestCacheDeduplication:
    """Test content deduplication functionality."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_find_similar_by_content_hash(self, cache):
        """Test finding entries with same content hash."""
        # Create responses with same content
        response1 = {"content": "Same response", "model": "gpt-4o-mini", "provider": "openai"}
        response2 = {"content": "Same response", "model": "gpt-4o", "provider": "openai"}  # Same content, different model

        messages1 = [{"role": "user", "content": "Hello"}]
        messages2 = [{"role": "user", "content": "Hi"}]  # Different prompt, same response

        cache.put(messages1, "openai", "gpt-4o-mini", response1)
        cache.put(messages2, "openai", "gpt-4o", response2)

        # Get content hash and find similar
        content_hash = cache._compute_content_hash(response1)
        similar = cache.find_similar(content_hash)

        assert len(similar) == 2
        models = [entry["model"] for entry in similar]
        assert "gpt-4o-mini" in models
        assert "gpt-4o" in models

    def test_cleanup_by_size_removes_lru(self, cache):
        """Test that size cleanup removes least recently used entries."""
        # Add multiple entries
        for i in range(5):
            messages = [{"role": "user", "content": f"Message {i}"}]
            response = {"content": f"Response {i}", "model": "gpt-4o-mini", "provider": "openai"}
            cache.put(messages, "openai", "gpt-4o-mini", response)

        # Access some entries to update their last_accessed time
        messages_2 = [{"role": "user", "content": "Message 2"}]
        messages_4 = [{"role": "user", "content": "Message 4"}]
        cache.get(messages_2, "openai", "gpt-4o-mini")
        cache.get(messages_4, "openai", "gpt-4o-mini")

        # Clean up to keep only 3 entries
        removed = cache.cleanup_by_size(3)
        assert removed == 2

        # Recently accessed entries should remain
        assert cache.get(messages_2, "openai", "gpt-4o-mini") is not None
        assert cache.get(messages_4, "openai", "gpt-4o-mini") is not None

        stats = cache.get_stats()
        assert stats["total_entries"] == 3


class TestCacheEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def cache(self):
        """Create a temporary cache for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_db:
            yield LLMResponseCache(db_path=temp_db.name)

    def test_empty_messages(self, cache):
        """Test caching with empty messages."""
        messages = []
        response = {"content": "Response", "model": "gpt-4o-mini", "provider": "openai"}

        cache.put(messages, "openai", "gpt-4o-mini", response)
        cached = cache.get(messages, "openai", "gpt-4o-mini")

        assert cached is not None
        assert cached["content"] == "Response"

    def test_large_response_content(self, cache):
        """Test caching large response content."""
        messages = [{"role": "user", "content": "Generate large text"}]
        large_content = "A" * 100000  # 100KB of text
        response = {"content": large_content, "model": "gpt-4o-mini", "provider": "openai"}

        cache.put(messages, "openai", "gpt-4o-mini", response)
        cached = cache.get(messages, "openai", "gpt-4o-mini")

        assert cached is not None
        assert cached["content"] == large_content
        assert len(cached["content"]) == 100000

    def test_unicode_content(self, cache):
        """Test caching with unicode content."""
        messages = [{"role": "user", "content": "Unicode test: 你好世界 🌍"}]
        response = {"content": "Unicode response: こんにちは 🇯🇵", "model": "gpt-4o-mini", "provider": "openai"}

        cache.put(messages, "openai", "gpt-4o-mini", response)
        cached = cache.get(messages, "openai", "gpt-4o-mini")

        assert cached is not None
        assert cached["content"] == "Unicode response: こんにちは 🇯🇵"

    def test_malformed_json_in_cache(self, cache):
        """Test handling malformed JSON in cache database."""
        messages = [{"role": "user", "content": "Hello"}]

        # Manually insert malformed JSON
        key = cache._compute_cache_key(messages, "openai", "gpt-4o-mini")
        with sqlite3.connect(cache.db_path) as conn:
            conn.execute("""
                INSERT INTO cache_entries
                (key, content_hash, provider, model, response_content,
                 created_at, expires_at, hit_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                key, "hash", "openai", "gpt-4o-mini",
                "invalid json content",  # Malformed JSON
                datetime.utcnow().isoformat(),
                None,
                datetime.utcnow().isoformat()
            ))

        # Should return None for malformed JSON
        cached = cache.get(messages, "openai", "gpt-4o-mini")
        assert cached is None
