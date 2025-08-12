"""Test configuration and fixtures."""

import ipaddress
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


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch):
    """Block outbound network except loopback. AF_UNIX and socketpair remain allowed."""
    original_connect = socket.socket.connect

    def is_localhost(host: str) -> bool:
        try:
            ip = ipaddress.ip_address(host)
            return ip.is_loopback
        except ValueError:
            # Resolve host; allow if any addr is loopback
            try:
                infos = socket.getaddrinfo(host, None)
            except Exception:
                return False
            for fam, *_ in infos:
                try:
                    for _, _, _, _, sa in [socket.getaddrinfo(host, 80, fam, 0, 0, 0)[0]]:
                        if fam in (socket.AF_INET, socket.AF_INET6):
                            ip = ipaddress.ip_address(sa[0])
                            if ip.is_loopback:
                                return True
                except Exception:
                    continue
            return False

    def guarded_connect(self, address):
        # address may be (host, port) or other tuple types; allow non-INET families
        if isinstance(address, tuple) and len(address) >= 1:
            host = address[0]
            # Allow obvious loopback names
            if host in ("localhost",):
                return original_connect(self, address)
            # Allow loopback IPs
            if isinstance(host, str) and is_localhost(host):
                return original_connect(self, address)
            # Otherwise block
            raise RuntimeError("External network blocked during tests")
        return original_connect(self, address)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    # Do not patch socketpair/AF_UNIX; asyncio and TestClient can function
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
async def override_db_dependency():
    """Override the database dependency for testing."""
    from driftguard.main import app

    # Create temporary database
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

    # Override dependency to return fresh session for each request
    async def get_test_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = get_test_session

    yield

    # Cleanup
    app.dependency_overrides.clear()
    await engine.dispose()
    os.close(db_fd)
    Path(db_path).unlink()
