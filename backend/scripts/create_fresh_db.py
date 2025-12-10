#!/usr/bin/env python3
"""
Script to create a fresh PostgreSQL database with the complete schema.
This consolidates all migrations into a single database creation script.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infra.database import engine
from app.infra import Base
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_fresh_database():
    """Create all tables from scratch using SQLAlchemy models."""

    logger.info("🗃️  Creating fresh PostgreSQL database...")

    # Ensure we have an async context by creating and immediately closing a session
    # This prevents "greenlet_spawn has not been called" errors
    from app.infra.database import AsyncSessionLocal
    async with AsyncSessionLocal() as dummy_session:
        pass  # Just create and close to establish async context

    try:
        # Create tables using SQLAlchemy metadata (handles async properly)
        logger.info("📋 Creating tables from SQLAlchemy models...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database schema created successfully!")

        # Show created tables
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()

        logger.info("📊 Created tables:")
        for table in tables:
            logger.info(f"   - {table[0]}")

        logger.info("\n🎯 Database is ready! You can now:")
        logger.info("   1. Run: python init_db.py (to create default user)")
        logger.info("   2. Start the server: uvicorn app.main:app --reload")

    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_fresh_database())