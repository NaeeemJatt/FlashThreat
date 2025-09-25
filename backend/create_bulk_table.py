#!/usr/bin/env python3
"""
Script to create the bulk_jobs table manually.
Run this script to create the table without using Alembic migrations.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.base import engine

async def create_bulk_table():
    """Create the bulk_jobs table."""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bulk_jobs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        total_iocs INTEGER NOT NULL DEFAULT 0,
        processed_iocs INTEGER NOT NULL DEFAULT 0,
        completed_iocs INTEGER NOT NULL DEFAULT 0,
        failed_iocs INTEGER NOT NULL DEFAULT 0,
        original_filename VARCHAR(255) NOT NULL,
        file_size INTEGER NOT NULL,
        ioc_list JSON NOT NULL,
        results JSON,
        error_message TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        force_refresh BOOLEAN NOT NULL DEFAULT FALSE
    );
    """
    
    try:
        async with engine.begin() as conn:
            await conn.execute(text(create_table_sql))
            print("✅ Successfully created bulk_jobs table")
    except Exception as e:
        print(f"❌ Error creating bulk_jobs table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(create_bulk_table())
