"""Test configuration and fixtures."""

import os
import socket
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from driftguard.database import get_db_session
from driftguard.models import Base


# Block network access during tests
@pytest.fixture(autouse=True)
def block_network():
    """Block all network access during tests."""
    original_socket = socket.socket

    def mock_socket(*args, **kwargs):
        raise RuntimeError("Network access blocked during tests")

    with patch('socket.socket', side_effect=mock_socket):
        yield


@pytest.fixture
async def test_db():
    """Create a temporary test database."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    test_database_url = f"sqlite+aiosqlite:///{db_path}"

    # Create test engine
    engine = create_async_engine(
        test_database_url,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    session_factory = async_sessionmaker(engine, class_=AsyncSession)

    yield session_factory

    # Cleanup
    await engine.dispose()
    os.close(db_fd)
    Path(db_path).unlink()


@pytest.fixture
async def db_session(test_db):
    """Get a database session for testing."""
    async with test_db() as session:
        yield session


@pytest.fixture
def override_db_dependency(db_session):
    """Override the database dependency for testing."""
    from driftguard.main import app
    app.dependency_overrides[get_db_session] = lambda: db_session
    yield
    app.dependency_overrides.clear()
