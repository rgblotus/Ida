from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .collection import Collection

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), default="New Chat", nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    collection_id: Mapped[int] = mapped_column(Integer, ForeignKey("collections.id"), nullable=False)
    llm_model: Mapped[str] = mapped_column(String(100), default="ollama", nullable=False)
    temperature: Mapped[int] = mapped_column(Integer, default=7, nullable=False)  # 0-20 (0.0-2.0)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    # AI Settings
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_personality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    response_style: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voice: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    collection: Mapped["Collection"] = relationship("Collection", back_populates="chat_sessions")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    llm_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    translated_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
