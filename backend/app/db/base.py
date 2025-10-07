from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create optimized async engine with connection pooling
# Note: For async engines, we use NullPool with connection pooling handled by the database
engine = create_async_engine(
    str(settings.POSTGRES_DSN),
    echo=False,
    future=True,
    poolclass=NullPool,  # NullPool is required for async engines
    # Connection pooling is handled by the database connection string
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Get a database session.
    
    Yields:
        AsyncSession: The database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

