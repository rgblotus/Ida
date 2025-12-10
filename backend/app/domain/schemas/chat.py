from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class ChatMessageRequest(BaseModel):
    session_id: int
    message: str

class ChatMessageResponse(BaseModel):
    message_id: int
    content: str
    sources: List[dict]
    llm_used: str
    created_at: datetime
    audio_url: Optional[str] = None
    translated_content: Optional[str] = None

class CreateSessionRequest(BaseModel):
    collection_id: int
    llm_model: str = "ollama_cloud"
    temperature: int = 7  # 0-20 (0.0-2.0)
    max_tokens: int = 2000
    top_k: int = 5
    title: Optional[str] = "New Chat"

    # AI Settings
    system_prompt: Optional[str] = None
    custom_instructions: Optional[str] = None
    prompt_template: Optional[str] = None
    ai_personality: Optional[str] = None
    response_style: Optional[str] = None
    voice: Optional[str] = None
    voice: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    title: str
    collection_id: int
    collection_name: str
    llm_model: str
    temperature: int
    max_tokens: int
    top_k: int
    created_at: datetime
    updated_at: datetime

    # AI Settings
    system_prompt: Optional[str] = None
    custom_instructions: Optional[str] = None
    prompt_template: Optional[str] = None
    ai_personality: Optional[str] = None
    response_style: Optional[str] = None

class MessageResponse(BaseModel):
    id: Optional[int] = None # Optional for ephemeral
    role: str
    content: str
    sources: Optional[List[dict]]
    llm_used: Optional[str]
    created_at: datetime
    audio_url: Optional[str] = None
    translated_content: Optional[str] = None