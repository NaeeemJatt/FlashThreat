#!/usr/bin/env python3
"""
Database initialization script for FlashThreat.
This script initializes the database using Alembic migrations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
from sqlalchemy import text
from app.core.config import settings
from app.db.base import engine, Base
from app.models import *  # Import all models to ensure they're registered


async def init_database():
    """Initialize the database with all tables and data."""
    print("Initializing FlashThreat database...")
    
    try:
        # Check if database is accessible
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("Database connection successful")
        
        # Create database tables
        print("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created")
        
        # Create initial admin user if it doesn't exist
        print("Creating initial admin user...")
        await create_initial_users()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        sys.exit(1)


async def create_initial_users():
    """Create initial admin and analyst users if they don't exist."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.user import User, UserRole
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    async with AsyncSession(engine) as session:
        # Check if admin user exists
        admin_result = await session.execute(
            select(User).where(User.email == "admin@flashthreat.local")
        )
        admin_user = admin_result.scalar_one_or_none()
        
        if not admin_user:
            admin_user = User(
                email="admin@flashthreat.local",
                password_hash=pwd_context.hash("admin123"),
                role=UserRole.ADMIN
            )
            session.add(admin_user)
            print("Created admin user (admin@flashthreat.local / admin123)")
        else:
            print("Admin user already exists")
        
        # Check if analyst user exists
        analyst_result = await session.execute(
            select(User).where(User.email == "analyst@flashthreat.local")
        )
        analyst_user = analyst_result.scalar_one_or_none()
        
        if not analyst_user:
            analyst_user = User(
                email="analyst@flashthreat.local",
                password_hash=pwd_context.hash("analyst123"),
                role=UserRole.ANALYST
            )
            session.add(analyst_user)
            print("Created analyst user (analyst@flashthreat.local / analyst123)")
        else:
            print("Analyst user already exists")
        
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_database())
