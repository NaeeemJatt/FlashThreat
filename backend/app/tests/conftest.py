import asyncio
import os
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import api_router
from app.core.config import settings
from app.db.base import Base, get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Fixture for creating a test database session."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def app(db: AsyncSession) -> FastAPI:
    """Fixture for creating a test FastAPI app."""
    from app.main import app as fastapi_app

    # Override get_db dependency
    async def override_get_db():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = override_get_db

    return fastapi_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Fixture for creating a test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """Fixture for mocking environment variables."""
    original_values = {}

    # Save original values
    for key in [
        "VT_API_KEY",
        "ABUSEIPDB_API_KEY",
        "SHODAN_API_KEY",
        "OTX_API_KEY",
    ]:
        original_values[key] = os.environ.get(key)
        os.environ[key] = f"test_{key.lower()}"

    yield os.environ

    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

