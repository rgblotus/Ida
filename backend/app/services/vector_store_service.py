from langchain_milvus import Milvus
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
from typing import List, Dict, Optional
import logging
from sklearn.decomposition import PCA
import numpy as np
from pathlib import Path
from app.core.hardware import detect_device, get_hardware_info

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing Milvus vector store operations"""
    
    def __init__(self, settings, embedding_service):
        self.settings = settings
        self.embedding_service = embedding_service
        self._connect()
    
    def _connect(self):
        """Connect to Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.settings.MILVUS_HOST,
                port=self.settings.MILVUS_PORT
            )
            logger.info(f"Connected to Milvus at {self.settings.MILVUS_HOST}:{self.settings.MILVUS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def create_collection_store(self, collection_name: str) -> Milvus:
        """
        Create or get Milvus collection as LangChain vector store
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            Milvus vector store instance
        """
        try:
            vector_store = Milvus(
                embedding_function=self.embedding_service.embeddings,
                collection_name=collection_name,
                connection_args={
                    "host": self.settings.MILVUS_HOST,
                    "port": self.settings.MILVUS_PORT
                },
                auto_id=True,
            )
            logger.info(f"Created/Retrieved Milvus collection: {collection_name}")
            return vector_store
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to collection with schema validation
        """
        # Ensure all required fields are present in metadata for different collection schemas
        validated_metadatas = []
        for metadata in metadatas:
            # Add required fields if missing
            validated_metadata = dict(metadata)  # Copy

            # Generate title if missing
            if 'title' not in validated_metadata and 'filename' in validated_metadata:
                title = Path(validated_metadata['filename']).stem
                if len(title) > 100:
                    title = title[:97] + "..."
                validated_metadata['title'] = title
            elif 'title' not in validated_metadata:
                validated_metadata['title'] = "Untitled Document"

            # Ensure multiple field name variants for compatibility
            title_value = validated_metadata['title']
            validated_metadata['subject'] = title_value
            validated_metadata['name'] = title_value

            # Ensure document_id is present and correct type
            if 'document_id' in validated_metadata:
                validated_metadata['document_id'] = int(validated_metadata['document_id'])

            # Ensure chunk_index is present and correct type
            if 'chunk_index' in validated_metadata:
                validated_metadata['chunk_index'] = int(validated_metadata['chunk_index'])

            # Ensure total_chunks is present and correct type
            if 'total_chunks' in validated_metadata:
                validated_metadata['total_chunks'] = int(validated_metadata['total_chunks'])

            # Add default values for commonly expected fields
            defaults = {
                'collection_name': validated_metadata.get('collection', 'default'),
                'content_type': 'text',
                'language': 'en',
                'source_type': 'document',
                'author': validated_metadata.get('author', validated_metadata.get('creator', 'Unknown')),
                'publisher': validated_metadata.get('producer', 'Unknown'),
                'date': validated_metadata.get('creationdate', 'Unknown'),
                'keywords': '',
                'description': validated_metadata.get('title', ''),
            }

            for key, default_value in defaults.items():
                if key not in validated_metadata:
                    validated_metadata[key] = default_value

            validated_metadatas.append(validated_metadata)

        metadatas = validated_metadatas

        # Now perform the actual insertion
        try:
            vector_store = self.create_collection_store(collection_name)
            doc_ids = vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to {collection_name}")
            return doc_ids
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {e}")
            raise
    
    def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = 5,
        filter: Optional[Dict] = None
    ):
        """
        Search for similar documents
        
        Args:
            collection_name: Name of the collection
            query: Query text
            k: Number of results to return
            filter: Optional metadata filter
        
        Returns:
            List of similar documents
        """
        try:
            vector_store = self.create_collection_store(collection_name)
            
            if filter:
                results = vector_store.similarity_search(
                    query,
                    k=k,
                    expr=self._build_filter_expr(filter)
                )
            else:
                results = vector_store.similarity_search(query, k=k)
            
            logger.info(f"Found {len(results)} similar documents in {collection_name}")
            return results
        except Exception as e:
            logger.error(f"Failed to search in {collection_name}: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        collection_name: str,
        query: str,
        k: int = 5
    ):
        """Search with similarity scores"""
        try:
            vector_store = self.create_collection_store(collection_name)
            results = vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Failed to search with scores in {collection_name}: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = utility.list_collections()
            logger.info(f"Found {len(collections)} collections")
            return collections
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        try:
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            else:
                logger.warning(f"Collection {collection_name} does not exist")
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            raise

    def delete_documents_by_id(self, collection_name: str, document_id: int):
        """Delete all vectors for a specific document ID"""
        try:
            if not utility.has_collection(collection_name):
                logger.warning(f"Collection {collection_name} does not exist")
                return

            collection = Collection(collection_name)
            collection.load()

            # Count entities before deletion
            initial_count = collection.num_entities

            # Delete entities where document_id matches
            expr = f"document_id == {document_id}"
            delete_result = collection.delete(expr=expr)

            # Flush to ensure deletion is persisted
            collection.flush()

            # Count entities after deletion
            final_count = collection.num_entities

            deleted_count = initial_count - final_count
            logger.info(f"Deleted {deleted_count} vectors for document_id {document_id} from {collection_name} (was {initial_count}, now {final_count})")
        except Exception as e:
            logger.error(f"Failed to delete document {document_id} from {collection_name}: {e}")
            raise

    def recreate_collection(self, collection_name: str) -> bool:
        """Recreate a collection to fix schema issues"""
        try:
            # Delete existing collection
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                logger.info(f"Dropped existing collection: {collection_name}")

            # Create new collection (will be created when first document is added)
            logger.info(f"Collection {collection_name} will be recreated on next document insert")
            return True
        except Exception as e:
            logger.error(f"Failed to recreate collection {collection_name}: {e}")
            return False

    def inspect_collection_schema(self, collection_name: str) -> Dict:
        """Inspect the schema of an existing collection"""
        try:
            if not utility.has_collection(collection_name):
                return {"error": f"Collection {collection_name} does not exist"}

            collection = Collection(collection_name)
            schema = collection.schema

            fields_info = []
            for field in schema.fields:
                fields_info.append({
                    "name": field.name,
                    "dtype": str(field.dtype),
                    "nullable": getattr(field, 'nullable', True),
                    "default_value": getattr(field, 'default_value', None)
                })

            return {
                "collection_name": collection_name,
                "fields": fields_info,
                "description": collection.description,
                "num_entities": collection.num_entities
            }
        except Exception as e:
            logger.error(f"Failed to inspect collection {collection_name}: {e}")
            return {"error": str(e)}
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """Get statistics for a collection"""
        try:
            if not utility.has_collection(collection_name):
                return {"exists": False}
            
            collection = Collection(collection_name)
            collection.load()
            
            stats = {
                "exists": True,
                "num_entities": collection.num_entities,
                "description": collection.description,
            }
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats for {collection_name}: {e}")
            return {"exists": False, "error": str(e)}
    
    def get_3d_visualization_data(self, collection_name: str, document_id: Optional[int] = None) -> Dict:
        """
        Get 3D visualization data for all vectors in collection

        Args:
            collection_name: Name of the collection

        Returns:
            Dict with 3D coordinates, metadata, and labels
        """
        try:
            if not utility.has_collection(collection_name):
                return {"error": f"Collection {collection_name} does not exist"}

            collection = Collection(collection_name)
            collection.load()

            # Query all vectors and metadata, optionally filtered by document_id
            expr = ""
            if document_id is not None:
                expr = f"document_id == {document_id}"

            results = collection.query(
                expr=expr,
                output_fields=["*", "vector"],  # Get all scalar fields + vector
                limit=10000  # Reasonable limit for visualization
            )

            if not results:
                return {"points": [], "metadata": [], "labels": []}

            # Extract vectors and metadata
            vectors = []
            metadatas = []

            for result in results:
                vectors.append(result['vector'])
                # Remove vector from metadata copy
                metadata = {k: v for k, v in result.items() if k != 'vector'}
                metadatas.append(metadata)

            vectors = np.array(vectors)

            # Use CPU sklearn PCA (optimal for visualization - fast and reliable)
            logger.info("🖥️  Using CPU sklearn PCA (optimal for 3D visualization)")
            from sklearn.decomposition import PCA
            pca = PCA(n_components=3)
            points_3d = pca.fit_transform(vectors)

            # Handle edge cases
            if len(vectors) < 3:
                # Not enough data for meaningful PCA
                if len(vectors) == 0:
                    return {"points": [], "metadata": [], "labels": []}
                # Pad with zeros for 3D visualization
                points_3d = np.zeros((len(vectors), 3))
                points_3d[:, :vectors.shape[1]] = vectors[:, :3]

            # Convert to list for JSON serialization
            points_3d = points_3d.tolist()

            # Create labels from metadata (e.g., document filename)
            labels = []
            for metadata in metadatas:
                label = metadata.get('filename', 'Unknown')
                chunk_info = f"chunk_{metadata.get('chunk_index', 0)}"
                labels.append(f"{label} - {chunk_info}")

            return {
                "points": points_3d,
                "metadata": metadatas,
                "labels": labels,
                "total_points": len(points_3d)
            }

        except Exception as e:
            logger.error(f"Failed to get 3D visualization data for {collection_name}: {e}")
            return {"error": str(e)}

    def _build_filter_expr(self, filter_dict: Dict) -> str:
        """Build Milvus filter expression from dict"""
        # Simple implementation - can be enhanced
        expressions = []
        for key, value in filter_dict.items():
            if isinstance(value, str):
                expressions.append(f'{key} == "{value}"')
            else:
                expressions.append(f'{key} == {value}')
        return " && ".join(expressions)
