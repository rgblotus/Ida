from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class Message:
    """Domain model for Message entity"""
    id: Optional[int] = None
    session_id: int = 0
    role: str = ""  # user, assistant, system
    content: str = ""
    sources: Optional[List[Dict[str, Any]]] = None
    llm_used: Optional[str] = None
    created_at: Optional[datetime] = None
    audio_url: Optional[str] = None
    translated_content: Optional[str] = None

    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == "user"

    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == "assistant"

    def has_sources(self) -> bool:
        """Check if message has sources"""
        return self.sources is not None and len(self.sources) > 0

    def has_translation(self) -> bool:
        """Check if message has translation"""
        return self.translated_content is not None and self.translated_content.strip() != ""

@dataclass
class ChatSession:
    """Domain model for ChatSession entity"""
    id: Optional[int] = None
    title: str = "New Chat"
    user_id: int = 0
    collection_id: int = 0
    llm_model: str = "ollama_cloud"
    temperature: int = 7  # 0-20 scale
    max_tokens: int = 2000
    top_k: int = 5

    # AI Settings
    system_prompt: Optional[str] = None
    custom_instructions: Optional[str] = None
    prompt_template: Optional[str] = None
    ai_personality: Optional[str] = None
    response_style: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    messages: List[Message] = field(default_factory=list)

    def update_title(self, new_title: str) -> None:
        """Update session title"""
        self.title = new_title.strip() or "New Chat"

    def add_message(self, message: Message) -> None:
        """Add a message to the session"""
        self.messages.append(message)

    def get_message_count(self) -> int:
        """Get total number of messages"""
        return len(self.messages)

    def get_user_messages(self) -> List[Message]:
        """Get all user messages"""
        return [msg for msg in self.messages if msg.is_user_message()]

    def get_assistant_messages(self) -> List[Message]:
        """Get all assistant messages"""
        return [msg for msg in self.messages if msg.is_assistant_message()]

    def update_ai_settings(self, **kwargs) -> None:
        """Update AI settings"""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)