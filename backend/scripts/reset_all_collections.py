#!/usr/bin/env python3
"""
Script to reset all Milvus collections to fix schema issues
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

def reset_all_collections():
    """Reset all collections to fix schema issues"""
    try:
        logger.info("🔄 Resetting all Milvus collections...")

        # Initialize services
        embedding_service = EmbeddingService('sentence-transformers/all-MiniLM-L6-v2')
        vector_store_service = VectorStoreService(settings, embedding_service)

        # Get all collections
        collections = vector_store_service.list_collections()

        if not collections:
            logger.info("📭 No collections found to reset")
            return

        logger.info(f"📚 Found {len(collections)} collections to reset")

        # Reset each collection
        reset_count = 0
        for collection_name in collections:
            try:
                success = vector_store_service.recreate_collection(collection_name)
                if success:
                    reset_count += 1
                    logger.info(f"✅ Reset collection: {collection_name}")
                else:
                    logger.error(f"❌ Failed to reset collection: {collection_name}")
            except Exception as e:
                logger.error(f"❌ Error resetting collection {collection_name}: {e}")

        logger.info(f"🎯 Successfully reset {reset_count}/{len(collections)} collections")
        logger.info("💡 Collections will be recreated when documents are uploaded")

    except Exception as e:
        logger.error(f"❌ Error resetting collections: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete all vector data in your collections!")
    confirm = input("Are you sure you want to continue? (type 'yes' to confirm): ")

    if confirm.lower() == 'yes':
        reset_all_collections()
    else:
        print("❌ Operation cancelled")
        sys.exit(0)