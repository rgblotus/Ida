import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infra.database import get_db
from app.core.config import settings
from app.infra import Base
import app.infra.redis as redis_module

# Override DB with in-memory SQLite (for speed + isolation)
SQLITE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    """Create tables once per test session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(test_db_setup):
    """Create a new DB session for each test."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def mock_redis():
    """Mock Redis client to avoid external dependency."""
    mock = AsyncMock()
    mock.setex = AsyncMock()
    mock.exists = AsyncMock(return_value=1)
    mock.delete = AsyncMock()
    return mock

@pytest_asyncio.fixture
async def client(db_session, mock_redis, monkeypatch):
    """Create async httpx test client with overridden dependencies."""
    
    # Mock the redis_client at module level
    monkeypatch.setattr(redis_module, "redis_client", mock_redis)
    
    async def override_get_db():
        yield db_session

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()