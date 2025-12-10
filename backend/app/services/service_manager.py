"""
Singleton service instances using lru_cache to avoid re-initialization
"""
from functools import lru_cache
from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.speech_service import SpeechService
from app.services.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)

# Flags to track initialization logging
_initialized = {
    'embedding': False,
    'vector_store': False,
    'llm': False,
    'rag': False,
    'speech': False,
    'chat': False
}

@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """Get singleton EmbeddingService instance"""
    if not _initialized['embedding']:
        logger.info("Initializing EmbeddingService (singleton)")
        _initialized['embedding'] = True
    return EmbeddingService(settings.EMBEDDING_MODEL)

@lru_cache(maxsize=1)
def get_vector_store_service() -> VectorStoreService:
    """Get singleton VectorStoreService instance"""
    if not _initialized['vector_store']:
        logger.info("Initializing VectorStoreService (singleton)")
        _initialized['vector_store'] = True
    embedding_service = get_embedding_service()
    return VectorStoreService(settings, embedding_service)

@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """Get singleton LLMService instance"""
    if not _initialized['llm']:
        logger.info("Initializing LLMService (singleton)")
        _initialized['llm'] = True
    return LLMService(settings)

@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Get singleton RAGService instance"""
    if not _initialized['rag']:
        logger.info("Initializing RAGService (singleton)")
        _initialized['rag'] = True
    llm_service = get_llm_service()
    vector_store_service = get_vector_store_service()
    return RAGService(llm_service, vector_store_service)

@lru_cache(maxsize=1)
def get_speech_service() -> SpeechService:
    """Get singleton SpeechService instance"""
    if not _initialized['speech']:
        logger.info("Initializing SpeechService (singleton)")
        _initialized['speech'] = True
    return SpeechService()

@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """Get singleton ChatService instance"""
    if not _initialized['chat']:
        logger.info("Initializing ChatService (singleton)")
        _initialized['chat'] = True
    rag_service = get_rag_service()
    speech_service = get_speech_service()
    llm_service = get_llm_service()
    return ChatService(rag_service, speech_service, llm_service)

def reset_services():
    """Reset all service instances (useful for testing)"""
    global _initialized
    _initialized = {key: False for key in _initialized}
    get_embedding_service.cache_clear()
    get_vector_store_service.cache_clear()
    get_llm_service.cache_clear()
    get_rag_service.cache_clear()
    get_speech_service.cache_clear()
    get_chat_service.cache_clear()
    logger.info("All service caches cleared")
