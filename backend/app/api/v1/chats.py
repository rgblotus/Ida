from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import List, Optional

from app.infra.database import get_db
from app.infra import User, Message, Collection
from app.infra.chat import ChatSession
from app.api.v1.deps import get_current_user
from app.services.chat_service import ChatService
from app.services.service_manager import get_chat_service
from app.infra.chat import ChatSession

router = APIRouter(tags=["chat"])

# Pydantic models
from app.domain.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    CreateSessionRequest,
    SessionResponse,
    MessageResponse
)
from pydantic import BaseModel
from typing import Optional

class UpdateAISettingsRequest(BaseModel):
    system_prompt: Optional[str] = None
    custom_instructions: Optional[str] = None
    prompt_template: Optional[str] = None
    ai_personality: Optional[str] = None
    response_style: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_k: Optional[int] = None
    voice: Optional[str] = None

@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message in a chat session"""
    response = await chat_service.send_message(
        session_id=request.session_id,
        user_id=current_user.id,
        message_content=request.message,
        db=db
    )
    
    return ChatMessageResponse(
        message_id=response["message_id"],
        content=response["content"],
        sources=response["sources"],
        llm_used=response["llm_used"],
        created_at=response["created_at"],
        audio_url=response["audio_url"],
        translated_content=response["translated_content"]
    )

@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Create a new chat session"""
    session = await chat_service.create_session(
        user_id=current_user.id,
        collection_id=request.collection_id,
        llm_model=request.llm_model,
        title=request.title or "New Chat",
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        top_k=request.top_k,
        db=db,
        system_prompt=request.system_prompt,
        custom_instructions=request.custom_instructions,
        prompt_template=request.prompt_template,
        ai_personality=request.ai_personality,
        response_style=request.response_style,
        voice=getattr(request, 'voice', None)
    )
    
    # Load collection for response
    result = await db.execute(select(Collection).where(Collection.id == session.collection_id))
    collection = result.scalar_one_or_none()
    
    return SessionResponse(
        id=session.id,
        title=session.title,
        collection_id=session.collection_id,
        collection_name=collection.name if collection else "Unknown",
        llm_model=session.llm_model,
        temperature=session.temperature,
        max_tokens=session.max_tokens,
        top_k=session.top_k,
        created_at=session.created_at,
        updated_at=session.updated_at,
        system_prompt=session.system_prompt,
        custom_instructions=session.custom_instructions,
        prompt_template=session.prompt_template,
        ai_personality=session.ai_personality,
        response_style=session.response_style,
        voice=session.voice
    )

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """List all chat sessions for current user"""
    sessions = await chat_service.list_sessions(
        user_id=current_user.id,
        db=db
    )
    
    return [
        SessionResponse(
            id=s.id,
            title=s.title,
            collection_id=s.collection_id,
            collection_name=s.collection.name if s.collection else "Unknown",
            llm_model=s.llm_model,
            temperature=s.temperature,
            max_tokens=s.max_tokens,
            top_k=s.top_k,
            created_at=s.created_at,
            updated_at=s.updated_at,
            system_prompt=s.system_prompt,
            custom_instructions=s.custom_instructions,
            prompt_template=s.prompt_template,
            ai_personality=s.ai_personality,
            response_style=s.response_style,
            voice=s.voice
        )
        for s in sessions
    ]

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all messages in a session"""
    messages = await chat_service.get_messages(
        session_id=session_id,
        user_id=current_user.id,
        db=db
    )
    
    return [
        MessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            sources=m.sources,
            llm_used=m.llm_used,
            created_at=m.created_at,
            audio_url=m.audio_url,
            translated_content=m.translated_content
        )
        for m in messages
    ]

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Delete a chat session"""
    await chat_service.delete_session(
        session_id=session_id,
        user_id=current_user.id,
        db=db
    )
    return {"message": "Session deleted successfully"}

@router.patch("/sessions/{session_id}/title")
async def update_session_title(
    session_id: int,
    title: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Update session title"""
    await chat_service.update_session_title(
        session_id=session_id,
        title=title,
        user_id=current_user.id,
        db=db
    )
    return {"message": "Title updated successfully"}

@router.patch("/sessions/{session_id}/ai-settings")
async def update_session_ai_settings(
    session_id: int,
    request: UpdateAISettingsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update AI settings for a specific chat session"""
    from app.core.validation import validate_llm_model, validate_temperature, validate_top_k

    # Verify session ownership
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update AI settings
    if request.system_prompt is not None:
        session.system_prompt = request.system_prompt
    if request.custom_instructions is not None:
        session.custom_instructions = request.custom_instructions
    if request.prompt_template is not None:
        session.prompt_template = request.prompt_template
    if request.ai_personality is not None:
        session.ai_personality = request.ai_personality
    if request.response_style is not None:
        session.response_style = request.response_style
    if request.llm_model is not None:
        session.llm_model = validate_llm_model(request.llm_model)
    if request.temperature is not None:
        session.temperature = int(validate_temperature(request.temperature) * 10)
    if request.max_tokens is not None:
        session.max_tokens = request.max_tokens  # Could add validation
    if request.top_k is not None:
        session.top_k = validate_top_k(request.top_k)
    if request.voice is not None:
        session.voice = request.voice

    session.updated_at = func.now()
    await db.commit()

    return {"message": "AI settings updated successfully"}

@router.post("/messages/{message_id}/audio")
async def generate_message_audio(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Generate audio for a specific message on-demand"""
    # Verify the message belongs to the current user
    result = await db.execute(
        select(Message).join(ChatSession, Message.session_id == ChatSession.id).where(
            Message.id == message_id,
            ChatSession.user_id == current_user.id
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        return await chat_service.generate_message_audio(message_id, db)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to generate audio for message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")

@router.post("/messages/{message_id}/translate")
async def translate_message(
    message_id: int,
    target_lang: str = "hi",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Translate a specific message to Hindi on-demand"""
    # Verify the message belongs to the current user
    result = await db.execute(
        select(Message).join(ChatSession, Message.session_id == ChatSession.id).where(
            Message.id == message_id,
            ChatSession.user_id == current_user.id
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        return await chat_service.translate_message(message_id, target_lang, db)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to translate message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.get("/languages")
async def get_available_languages(
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get available translation languages"""
    return await chat_service.get_available_languages()
