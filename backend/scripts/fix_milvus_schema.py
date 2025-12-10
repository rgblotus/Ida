#!/usr/bin/env python3
"""
Script to fix Milvus collection schema issues by recreating collections
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store_service import VectorStoreService
from app.services.embedding_service import EmbeddingService
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_collection_schema(collection_name: str):
    """Recreate a collection to fix schema issues"""
    try:
        logger.info(f"🔧 Fixing schema for collection: {collection_name}")

        # Initialize services
        embedding_service = EmbeddingService('sentence-transformers/all-MiniLM-L6-v2')
        vector_store_service = VectorStoreService(settings, embedding_service)

        # Recreate collection
        success = vector_store_service.recreate_collection(collection_name)

        if success:
            logger.info(f"✅ Successfully recreated collection: {collection_name}")
            logger.info("📝 You can now re-upload documents to this collection")
        else:
            logger.error(f"❌ Failed to recreate collection: {collection_name}")

    except Exception as e:
        logger.error(f"❌ Error fixing collection schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_milvus_schema.py <collection_name>")
        print("Example: python fix_milvus_schema.py default")
        sys.exit(1)

    collection_name = sys.argv[1]
    fix_collection_schema(collection_name)