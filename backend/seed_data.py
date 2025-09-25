import asyncio
import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User, UserRole
from app.db.base import Base

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create async engine
engine = create_async_engine(
    str(settings.POSTGRES_DSN),
    echo=True,
)

# Create async session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_admin_user():
    """Create admin user."""
    async with async_session() as session:
        # Check if admin user already exists
        from sqlalchemy import text
        result = await session.execute(text("SELECT * FROM users WHERE email = 'admin@example.com'"))
        admin = result.fetchone()
        
        if admin:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            password_hash=pwd_context.hash("password123"),
            role=UserRole.ADMIN,
            created_at=datetime.utcnow(),
        )
        session.add(admin)
        
        # Create analyst user
        analyst = User(
            id=uuid.uuid4(),
            email="analyst@example.com",
            password_hash=pwd_context.hash("password123"),
            role=UserRole.ANALYST,
            created_at=datetime.utcnow(),
        )
        session.add(analyst)
        
        await session.commit()
        print("Created admin and analyst users.")


async def main():
    """Main function."""
    print("Creating tables...")
    await create_tables()
    
    print("Creating admin user...")
    await create_admin_user()
    
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())

