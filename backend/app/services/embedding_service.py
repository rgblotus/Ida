#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

from typing import List
import logging

from app.core.hardware import detect_device

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings using HuggingFace models with GPU support"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embeddings = None
        self._initialize()

    def _initialize(self):
        """Initialize the embedding model with GPU optimization"""
        try:
            from app.core.hardware import get_hardware_info
            device = detect_device()  # Auto-detect GPU/CPU
            hw_info = get_hardware_info()

            # GPU optimizations
            if device == 'cuda' and hw_info['gpu_available']:
                logger.info(f"🚀 Initializing embeddings on GPU: {hw_info['gpu_names'][0]}")

                # Additional GPU optimizations
                import torch
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.enabled = True

                # Set memory optimization
                import os
                os.environ['PYTORCH_ALLOC_CONF'] = 'max_split_size_mb:512'

                # Initialize directly on GPU to avoid meta tensor issues
                model_kwargs = {'device': device, 'model_kwargs': {'low_cpu_mem_usage': True}}

            else:
                logger.info("🖥️  Initializing embeddings on CPU")
                device = 'cpu'
                model_kwargs = {'device': device, 'model_kwargs': {'low_cpu_mem_usage': True}}

            # SentenceTransformer has limited encode_kwargs support
            # Use basic configuration to avoid parameter errors
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs=model_kwargs,
                encode_kwargs={'normalize_embeddings': True}
            )

            # Log performance info
            device_name = hw_info['gpu_names'][0] if device == 'cuda' and hw_info['gpu_names'] else 'CPU'
            logger.info(f"✅ Embedding model initialized: {self.model_name} on {device_name}")
            logger.info(f"   Device: {device.upper()}")
            logger.info(f"   GPU acceleration: {'Enabled' if device == 'cuda' else 'Disabled'}")
            if device == 'cuda':
                logger.info("   Direct GPU initialization: Enabled (avoids meta tensor issues)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {e}")
            raise

    def _fallback_to_cpu(self):
        """Fallback to CPU embeddings if GPU fails"""
        try:
            logger.warning("🔄 Falling back to CPU embeddings due to GPU error")

            # Clear GPU memory if possible
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Reinitialize on CPU
            model_kwargs = {'device': 'cpu', 'model_kwargs': {'low_cpu_mem_usage': True}}
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs=model_kwargs,
                encode_kwargs={'normalize_embeddings': True}
            )

            logger.info("✅ Successfully fell back to CPU embeddings")

        except Exception as e:
            logger.error(f"❌ Failed to fallback to CPU embeddings: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple documents

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        if not self.embeddings:
            raise Exception("Embedding model not initialized")

        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            error_msg = str(e).lower()
            if 'cuda' in error_msg or 'device-side assert' in error_msg:
                logger.warning(f"CUDA error in embed_documents, falling back to CPU: {e}")
                self._fallback_to_cpu()
                return self.embeddings.embed_documents(texts)
            else:
                raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        if not self.embeddings:
            raise Exception("Embedding model not initialized")

        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            error_msg = str(e).lower()
            if 'cuda' in error_msg or 'device-side assert' in error_msg:
                logger.warning(f"CUDA error in embed_query, falling back to CPU: {e}")
                self._fallback_to_cpu()
                return self.embeddings.embed_query(text)
            else:
                raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        # For all-MiniLM-L6-v2, dimension is 384
        test_embedding = self.embed_query("test")
        return len(test_embedding)

