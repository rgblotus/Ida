"""
Initialize the RAG application database and create default collections
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.infra.database import AsyncSessionLocal
from app.infra import User, Collection
from app.core.config import settings
from app.core.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_default_user():
    """Create a default demo user with proper password hashing"""
    async with AsyncSessionLocal() as db:
        # Check if user exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "demo@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            # Hash the password properly
            hashed_password = hash_password("demo123")
            user = User(
                email="demo@example.com",
                hashed_password=hashed_password
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"✅ Created default user: {user.email}")
        else:
            logger.info(f"ℹ️  User already exists: {user.email}")
        
        return user

async def create_default_collection(user):
    """Create a default collection"""
    async with AsyncSessionLocal() as db:
        # Check if collection exists
        from sqlalchemy import select
        result = await db.execute(
            select(Collection).where(
                Collection.name == "default",
                Collection.user_id == user.id
            )
        )
        collection = result.scalar_one_or_none()
        
        if not collection:
            collection = Collection(
                name="default",
                description="Default collection for documents",
                user_id=user.id
            )
            db.add(collection)
            await db.commit()
            await db.refresh(collection)
            logger.info(f"✅ Created default collection: {collection.name}")
        else:
            logger.info(f"ℹ️  Collection already exists: {collection.name}")
        
        return collection

async def main():
    """Main initialization function"""
    logger.info("🚀 Initializing RAG Application Database...")
    
    # Create default user
    logger.info("👤 Creating default user...")
    user = await create_default_user()
    
    # Create default collection
    logger.info("📁 Creating default collection...")
    collection = await create_default_collection(user)
    
    # Create upload directory
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info(f"📂 Upload directory created: {settings.UPLOAD_DIR}")
    
    logger.info("\n✨ Initialization complete!")
    logger.info(f"\n📋 Summary:")
    logger.info(f"   - Database: {settings.DATABASE_URL}")
    logger.info(f"   - Milvus: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    logger.info(f"   - Ollama Model: {settings.OLLAMA_MODEL}")
    logger.info(f"   - Default User: {user.email}")
    logger.info(f"   - Default Password: demo123")
    logger.info(f"   - Default Collection: {collection.name}")
    logger.info(f"\n🎯 Next steps:")
    logger.info(f"   1. Start the server: uv run uvicorn app.main:app --reload")
    logger.info(f"   2. Visit API docs: http://localhost:8000/api/docs")
    logger.info(f"   3. Login at: http://localhost:5173/login")
    logger.info(f"   4. Upload documents and start chatting!")

if __name__ == "__main__":
    asyncio.run(main())
