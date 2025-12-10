from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from typing import List, Tuple, Optional, Any
import logging
from app.core.constants import LLMConstants
import os
logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for managing LLM interactions with multiple Ollama instances and OpenAI
    Priority: Ollama Cloud -> Ollama Local -> OpenAI
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.ollama_cloud_llm = None
        self.ollama_local_llm = None
        self.openai_llm = None
        # Delay initialization to avoid startup issues
        # Will initialize on first use
    
    
    def _initialize_llms(self):
        """Initialize Ollama Cloud, Ollama Local, and OpenAI LLMs"""

        # GPU optimization for NVIDIA cards - detect and configure properly
        import torch
        from app.core.hardware import detect_device, get_hardware_info

        device = detect_device()
        hw_info = get_hardware_info()

        if device == 'cuda' and hw_info['gpu_available']:
            logger.info(f"🚀 NVIDIA GPU detected: {hw_info['gpu_names'][0]} - enabling GPU acceleration")
            # Configure for GPU usage with memory optimization
            os.environ['PYTORCH_ALLOC_CONF'] = 'max_split_size_mb:512'
            os.environ['TORCH_USE_CUDA_DSA'] = '1'  # Enable CUDA device-side assertions for debugging

            # Set GPU as default device
            if hasattr(torch, 'set_default_device'):
                torch.set_default_device('cuda')
            else:
                torch.cuda.set_device(0)

            # Enable CUDA optimizations
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.enabled = True

        else:
            logger.info("🖥️  Using CPU - no NVIDIA GPU detected")
            # CPU-only configuration
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

            if hasattr(torch, 'set_default_device'):
                torch.set_default_device('cpu')

        # Smart device handling for transformers to prevent meta tensor issues
        try:
            import transformers
            original_from_pretrained = transformers.AutoModelForCausalLM.from_pretrained
            def patched_from_pretrained(*args, **kwargs):
                # Use auto device mapping for optimal performance
                if 'device_map' not in kwargs:
                    if device == 'cuda':
                        kwargs['device_map'] = 'auto'  # Let transformers handle GPU placement
                    else:
                        kwargs['device_map'] = None   # CPU only

                # Optimize data types for the device
                if device == 'cuda' and 'torch_dtype' not in kwargs:
                    kwargs['torch_dtype'] = torch.float16  # Use half precision on GPU
                elif device == 'cpu' and 'torch_dtype' in kwargs and kwargs['torch_dtype'] == torch.float16:
                    kwargs['torch_dtype'] = torch.float32  # float16 not optimal on CPU

                return original_from_pretrained(*args, **kwargs)
            transformers.AutoModelForCausalLM.from_pretrained = patched_from_pretrained
        except ImportError:
            pass  # transformers not available, skip patching

        # Initialize Ollama Cloud (Primary)
        # Strict check: Skip if API key is placeholder or not provided
        if (self.settings.OLLAMA_CLOUD_API_KEY and
            self.settings.OLLAMA_CLOUD_API_KEY not in ["your-ollama-cloud-api-key-here", "placeholder", ""]):
            try:
                # Try minimal config first to avoid meta tensor issues
                self.ollama_cloud_llm = ChatOllama(
                    base_url=self.settings.OLLAMA_CLOUD_URL,
                    model=self.settings.OLLAMA_MODEL,
                )
                logger.info(f"Ollama Cloud initialized with model: {self.settings.OLLAMA_MODEL}")

            except Exception as e:
                logger.error(f"Failed to initialize Ollama Cloud: {e}")
                self.ollama_cloud_llm = None
        else:
            logger.info("Ollama Cloud API key not configured, skipping cloud initialization")
            self.ollama_cloud_llm = None

        # Initialize Ollama Local (Fallback 1 / Primary Local)
        try:
            self.ollama_local_llm = ChatOllama(
                base_url=self.settings.OLLAMA_LOCAL_URL,
                model=self.settings.OLLAMA_MODEL,
                temperature=0.7,
            )
            logger.info(f"Ollama Local initialized with model: {self.settings.OLLAMA_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama Local: {e}")
            self.ollama_local_llm = None

        # Initialize OpenAI (Fallback 2) - least likely to have meta tensor issues
        if (self.settings.OPENAI_API_KEY and
            self.settings.OPENAI_API_KEY not in ["your-openai-api-key-here", "placeholder", ""]):
            try:
                self.openai_llm = ChatOpenAI(
                    api_key=self.settings.OPENAI_API_KEY,
                    model=self.settings.OPENAI_MODEL,
                    temperature=0.7,
                )
                logger.info(f"OpenAI initialized with model: {self.settings.OPENAI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.openai_llm = None
        else:
            logger.info("OpenAI API key not provided, skipping initialization")
            self.openai_llm = None

        # Log available LLMs
        available = []
        if self.ollama_cloud_llm: available.append("Ollama Cloud")
        if self.ollama_local_llm: available.append("Ollama Local")
        if self.openai_llm: available.append("OpenAI")
        logger.info(f"LLM initialization complete. Available: {available}")

    def _ensure_initialized(self):
        """Lazy initialization of LLMs"""
        if self.ollama_cloud_llm is None and self.ollama_local_llm is None and self.openai_llm is None:
            self._initialize_llms()

    def get_primary_llm_type(self) -> str:
        """Get the type of the primary available LLM"""
        self._ensure_initialized()
        if self.ollama_cloud_llm:
            return "ollama_cloud"
        elif self.ollama_local_llm:
            return "ollama_local"
        elif self.openai_llm:
            return "openai"
        else:
            # If nothing is initialized, default to cloud and let it fail/guide user
            return "ollama_cloud"
    
    def get_llm(self, preferred: str = "ollama_cloud", temperature: float = LLMConstants.DEFAULT_TEMPERATURE) -> Tuple[Any, str]:
        """
        Get LLM instance with fallback logic
        Priority: ollama_cloud -> ollama_local -> openai

        Args:
            preferred: Preferred LLM ("ollama_cloud", "ollama_local", or "openai")
            temperature: Temperature setting (0.0 - 2.0)

        Returns:
            Tuple of (LLM instance, actual_llm_used)
        """
        self._ensure_initialized()

        # Try preferred LLM first
        if preferred == "ollama_cloud" and self.ollama_cloud_llm:
            return ChatOllama(
                base_url=self.settings.OLLAMA_CLOUD_URL,
                model=self.settings.OLLAMA_MODEL,
                temperature=temperature,
                api_key=self.settings.OLLAMA_CLOUD_API_KEY
            ), "ollama_cloud"
        elif preferred == "ollama_local" and self.ollama_local_llm:
            return ChatOllama(
                base_url=self.settings.OLLAMA_LOCAL_URL,
                model=self.settings.OLLAMA_MODEL,
                temperature=temperature,
            ), "ollama_local"
        elif preferred == "openai" and self.openai_llm:
            return ChatOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_MODEL,
                temperature=temperature,
            ), "openai"

        # Fallback chain: cloud -> local -> openai
        if self.ollama_cloud_llm:
            logger.warning(f"Preferred LLM '{preferred}' not available, using Ollama Cloud")
            return ChatOllama(
                base_url=self.settings.OLLAMA_CLOUD_URL,
                model=self.settings.OLLAMA_MODEL,
                temperature=temperature,
                api_key=self.settings.OLLAMA_CLOUD_API_KEY
            ), "ollama_cloud"
        elif self.ollama_local_llm:
            logger.warning(f"Ollama Cloud not available, falling back to Ollama Local")
            return ChatOllama(
                base_url=self.settings.OLLAMA_LOCAL_URL,
                model=self.settings.OLLAMA_MODEL,
                temperature=temperature,
            ), "ollama_local"
        elif self.openai_llm:
            logger.warning(f"Ollama not available, falling back to OpenAI")
            return ChatOpenAI(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_MODEL,
                temperature=temperature,
            ), "openai"
        else:
            raise Exception("No LLM available. Please check Ollama or OpenAI configuration.")
    
    async def invoke_with_fallback(
        self,
        messages: List[BaseMessage],
        preferred: str = "ollama_cloud",
        temperature: float = LLMConstants.DEFAULT_TEMPERATURE
    ) -> Tuple[str, str]:
        """
        Invoke LLM with automatic fallback chain
        
        Args:
            messages: List of messages to send to LLM
            preferred: Preferred LLM ("ollama_cloud", "ollama_local", or "openai")
            temperature: Temperature setting
        
        Returns:
            Tuple of (response_content, llm_used)
        """
        # Try preferred LLM
        try:
            llm, llm_name = self.get_llm(preferred, temperature)
            response = await llm.ainvoke(messages)
            logger.info(f"Successfully got response from {llm_name}")
            return response.content, llm_name
        except Exception as e:
            logger.error(f"Error with {preferred}: {e}")
        
        # Try fallback chain
        fallback_order = []
        if preferred != "ollama_cloud":
            fallback_order.append("ollama_cloud")
        if preferred != "ollama_local":
            fallback_order.append("ollama_local")
        if preferred != "openai":
            fallback_order.append("openai")
        
        for fallback in fallback_order:
            try:
                llm, llm_name = self.get_llm(fallback, temperature)
                response = await llm.ainvoke(messages)
                logger.info(f"Successfully fell back to {llm_name}")
                return response.content, llm_name
            except Exception as e:
                logger.error(f"Fallback to {fallback} failed: {e}")
                continue
        
        raise Exception("All LLMs failed. Please check your configuration.")
    
    def is_available(self, llm_type: str) -> bool:
        """Check if a specific LLM is available"""
        if llm_type == "ollama_cloud":
            return self.ollama_cloud_llm is not None
        elif llm_type == "ollama_local":
            return self.ollama_local_llm is not None
        elif llm_type == "openai":
            return self.openai_llm is not None
        return False
    
    def get_available_llms(self) -> List[str]:
        """Get list of available LLMs"""
        self._ensure_initialized()
        available = []
        if self.ollama_cloud_llm:
            available.append("ollama_cloud")
        if self.ollama_local_llm:
            available.append("ollama_local")
        if self.openai_llm:
            available.append("openai")
        return available
