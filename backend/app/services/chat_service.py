from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.infra import ChatSession, Message, User, Collection
from app.services.rag_service import RAGService
from app.services.speech_service import SpeechService
from app.core.constants import LLMConstants
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, rag_service: RAGService, speech_service: SpeechService, llm_service):
        self.rag_service = rag_service
        self.speech_service = speech_service
        self.llm_service = llm_service

    async def _generate_title(self, message_content: str, llm_model: str) -> str:
        """Generate a short title based on the first message without LLM call"""
        try:
            # Simple title generation based on content
            content = message_content.lower().strip()

            # Common patterns
            if any(word in content for word in ['hello', 'hi', 'hey', 'greetings']):
                return "Greeting Chat"
            elif any(word in content for word in ['help', 'assist', 'support']):
                return "Help Request"
            elif any(word in content for word in ['calculate', 'math', 'integral', 'derivative', 'solve']):
                return "Math Problem"
            elif any(word in content for word in ['weather', 'temperature', 'forecast']):
                return "Weather Discussion"
            elif any(word in content for word in ['code', 'programming', 'python', 'javascript']):
                return "Programming Help"
            elif len(content) > 10:
                # Use first few words as title
                words = content.split()[:3]
                title = " ".join(words).title()
                if len(title) > 20:
                    title = title[:30] + "..."
                return title
            else:
                return "New Chat"

        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return "New Chat"

    async def get_session(self, session_id: int, user_id: int, db: AsyncSession) -> ChatSession:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    async def create_session(
        self,
        user_id: int,
        collection_id: int,
        llm_model: str,
        title: str,
        temperature: int,
        max_tokens: int,
        top_k: int,
        db: AsyncSession,
        system_prompt: str = None,
        custom_instructions: str = None,
        prompt_template: str = None,
        ai_personality: str = None,
        response_style: str = None,
        voice: str = None
    ) -> ChatSession:
        # Verify collection exists and belongs to user
        result = await db.execute(
            select(Collection).where(
                Collection.id == collection_id,
                Collection.user_id == user_id
            )
        )
        collection = result.scalar_one_or_none()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found or access denied")

        # Validate LLM model
        from app.core.validation import validate_llm_model
        llm_model = validate_llm_model(llm_model)

        session = ChatSession(
            user_id=user_id,
            collection_id=collection_id,
            llm_model=llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_k=top_k,
            title=title,
            system_prompt=system_prompt,
            custom_instructions=custom_instructions,
            prompt_template=prompt_template,
            ai_personality=ai_personality,
            response_style=response_style,
            voice=voice
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    async def list_sessions(self, user_id: int, db: AsyncSession) -> List[ChatSession]:
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .options(selectinload(ChatSession.collection))
            .order_by(ChatSession.updated_at.desc())
        )
        return result.scalars().all()

    async def delete_session(self, session_id: int, user_id: int, db: AsyncSession):
        session = await self.get_session(session_id, user_id, db)
        await db.delete(session)
        await db.commit()

    async def update_session_title(self, session_id: int, title: str, user_id: int, db: AsyncSession):
        session = await self.get_session(session_id, user_id, db)
        session.title = title
        session.updated_at = datetime.utcnow()
        await db.commit()

    async def get_messages(self, session_id: int, user_id: int, db: AsyncSession) -> List[Message]:
        await self.get_session(session_id, user_id, db) # Verify access
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def send_message(
        self,
        session_id: int,
        user_id: int,
        message_content: str,
        db: AsyncSession
    ) -> Dict:
        """
        Send message, get RAG response, generate TTS/Translation.
        Returns Dict with answer, sources, audio_url, translated_content, message_id, etc.
        """
        session = await self.get_session(session_id, user_id, db)

        # Get history
        history = await self.get_messages(session_id, user_id, db)

        # Auto-rename session if it's the first message and title is default or auto-generated
        if len(history) == 0 and (session.title == "New Chat" or session.title.startswith("Auto:")):
              try:
                  new_title = await self._generate_title(message_content, session.llm_model)
                  session.title = new_title
                  await db.commit()
              except Exception as e:
                  logger.error(f"Failed to auto-rename session: {e}")

        chat_history = [{"role": m.role, "content": m.content} for m in history[-LLMConstants.CHAT_HISTORY_LIMIT:]]

        # Get collection for name
        result = await db.execute(select(Collection).where(Collection.id == session.collection_id))
        collection = result.scalar_one_or_none()
        if not collection:
              raise HTTPException(status_code=404, detail="Collection not found")

        # RAG Generation
        temp_float = session.temperature / LLMConstants.TEMPERATURE_SCALE
        rag_response = await self.rag_service.chat(
            collection_name=collection.name,
            message=message_content,
            chat_history=chat_history,
            llm_model=session.llm_model,
            temperature=temp_float,
            top_k=session.top_k,
            system_prompt=session.system_prompt,
            custom_instructions=session.custom_instructions
        )

        # Persist User Message
        user_msg = Message(session_id=session_id, role="user", content=message_content)
        db.add(user_msg)

        # Persist Assistant Message (audio and translation generated on-demand)
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=rag_response["answer"],
            sources=rag_response["sources"],
            llm_used=rag_response.get("llm_used", session.llm_model),
            audio_url=None,  # Generate on-demand when sound icon clicked
            translated_content=None  # Generate on-demand when translation requested
        )
        db.add(assistant_msg)

        session.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(assistant_msg)

        return {
            "message_id": assistant_msg.id,
            "content": rag_response["answer"],
            "sources": rag_response["sources"],
            "llm_used": rag_response.get("llm_used", session.llm_model),
            "created_at": assistant_msg.created_at,
            "audio_url": None,  # On-demand
            "translated_content": None  # On-demand
        }

    async def generate_message_audio(self, message_id: int, db: AsyncSession) -> Dict:
        logger.info(f"Generating audio for message {message_id}")
        result = await db.execute(
            select(Message)
            .where(Message.id == message_id)
            .options(selectinload(Message.session))
        )
        message = result.scalar_one_or_none()
        if not message:
            logger.error(f"Message {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")

        # Get voice from the session the message belongs to
        voice = message.session.voice or "auto"
        logger.info(f"Using voice: {voice} for message {message_id}")
        audio_url = await self.speech_service.generate_audio(message.content, voice=voice)
        logger.info(f"Audio generated: {audio_url} for message {message_id}")

        # Update message with audio URL
        message.audio_url = audio_url
        await db.commit()

        return {"audio_url": audio_url}

    async def translate_message(self, message_id: int, target_lang: str, db: AsyncSession) -> Dict:
        logger.info(f"Translating message {message_id} to {target_lang}")
        result = await db.execute(select(Message).where(Message.id == message_id))
        message = result.scalar_one_or_none()
        if not message:
            logger.error(f"Message {message_id} not found")
            raise HTTPException(status_code=404, detail="Message not found")

        translated = await self.speech_service.translate_text(message.content, target_lang)
        logger.info(f"Translation completed for message {message_id}")

        # Update message with translated content
        message.translated_content = translated
        await db.commit()

        return {"translated_content": translated}

    async def get_available_languages(self) -> list:
        """Get available translation languages"""
        return await self.speech_service.get_available_languages()
