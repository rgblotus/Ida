from pydantic import BaseModel

class AISettings(BaseModel):
    llm_model: str = "ollama_cloud"
    embedding_model: str = "text-embedding-3-small"
    temperature: int = 7  # 0-20 scale
    max_tokens: int = 2000
    top_k: int = 5

class AISettingsResponse(BaseModel):
    llm_model: str
    embedding_model: str
    temperature: int
    max_tokens: int
    top_k: int
    user_id: int