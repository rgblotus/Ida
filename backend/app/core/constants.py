"""Application constants and configuration values"""

# LLM Constants
class LLMConstants:
    MAX_TEMPERATURE = 2.0
    MIN_TEMPERATURE = 0.0
    DEFAULT_TEMPERATURE = 0.7
    TEMPERATURE_SCALE = 10.0  # For converting UI scale (0-20) to API scale (0-2)
    CHAT_HISTORY_LIMIT = 10
    MAX_TITLE_LENGTH = 50

    VALID_LLM_MODELS = ["ollama_cloud", "ollama_local", "openai"]
    VALID_ROLES = ["user", "assistant", "system"]

# Vector Store Constants
class VectorStoreConstants:
    DEFAULT_TOP_K = 5
    MAX_TOP_K = 20
    MIN_TOP_K = 1

# File Upload Constants
class FileConstants:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.md'}

# API Constants
class APIConstants:
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

# Error Messages
class ErrorMessages:
    COLLECTION_NOT_FOUND = "Collection not found"
    SESSION_NOT_FOUND = "Session not found"
    MESSAGE_NOT_FOUND = "Message not found"
    INVALID_LLM_MODEL = "Invalid LLM model specified"
    INVALID_TEMPERATURE = "Temperature must be between 0 and 2"
    INVALID_TOP_K = "Top-K must be between 1 and 20"