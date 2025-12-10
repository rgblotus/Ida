#!/usr/bin/env python3
"""
Script to inspect Milvus collection schemas and diagnose field issues
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

def inspect_collection(collection_name: str):
    """Inspect a specific collection schema"""
    try:
        logger.info(f"🔍 Inspecting collection: {collection_name}")

        # Initialize services
        embedding_service = EmbeddingService('sentence-transformers/all-MiniLM-L6-v2')
        vector_store_service = VectorStoreService(settings, embedding_service)

        # Inspect schema
        schema_info = vector_store_service.inspect_collection_schema(collection_name)

        if "error" in schema_info:
            logger.error(f"❌ Error inspecting collection: {schema_info['error']}")
            return

        print(f"\n📊 Collection: {collection_name}")
        print(f"   Entities: {schema_info['num_entities']}")
        print(f"   Description: {schema_info.get('description', 'None')}")
        print(f"   Fields:")

        for field in schema_info['fields']:
            nullable = "✅" if field.get('nullable', True) else "❌"
            default = f" (default: {field.get('default_value')})" if field.get('default_value') else ""
            print(f"     - {field['name']}: {field['dtype']} {nullable}{default}")

        # Check for common missing fields
        field_names = [f['name'] for f in schema_info['fields']]
        required_fields = ['title', 'subject', 'author', 'document_id', 'filename', 'chunk_index', 'collection']
        missing_fields = [field for field in required_fields if field not in field_names]

        if missing_fields:
            print(f"\n⚠️  Missing required fields: {missing_fields}")
            print("💡 This might cause 'insert missed field' errors")
        else:
            print("\n✅ All required fields present")

    except Exception as e:
        logger.error(f"❌ Error inspecting collection: {e}")

def list_all_collections():
    """List all collections and their basic info"""
    try:
        logger.info("📋 Listing all collections...")

        # Initialize services
        embedding_service = EmbeddingService('sentence-transformers/all-MiniLM-L6-v2')
        vector_store_service = VectorStoreService(settings, embedding_service)

        collections = vector_store_service.list_collections()

        if not collections:
            print("📭 No collections found")
            return

        print(f"\n📚 Found {len(collections)} collections:")
        for collection_name in collections:
            schema_info = vector_store_service.inspect_collection_schema(collection_name)
            if "error" not in schema_info:
                entities = schema_info.get('num_entities', 0)
                print(f"   - {collection_name}: {entities} entities")
            else:
                print(f"   - {collection_name}: Error inspecting")

    except Exception as e:
        logger.error(f"❌ Error listing collections: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - list all collections
        list_all_collections()
    elif len(sys.argv) == 2:
        # One argument - inspect specific collection
        collection_name = sys.argv[1]
        inspect_collection(collection_name)
    else:
        print("Usage:")
        print("  python inspect_milvus_schema.py                # List all collections")
        print("  python inspect_milvus_schema.py <collection>   # Inspect specific collection")
        sys.exit(1)