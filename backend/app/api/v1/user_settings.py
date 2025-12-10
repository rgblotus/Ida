from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.infra.database import get_db
from app.infra import User
from app.api.v1.deps import get_current_user
from app.domain.schemas.user_settings import AISettings, AISettingsResponse

router = APIRouter(tags=["settings"])

# In-memory storage for now (you can add a database table later)
user_settings = {}

@router.get("/ai-settings", response_model=AISettingsResponse)
async def get_ai_settings(
    current_user: User = Depends(get_current_user)
):
    """Get AI settings for the current user"""
    user_id = current_user.id
    
    # Return user's settings or defaults
    settings = user_settings.get(user_id, {
        "llm_model": "ollama_cloud",
        "embedding_model": "text-embedding-3-small",
        "temperature": 7,
        "max_tokens": 2000,
        "top_k": 5
    })
    
    return {
        **settings,
        "user_id": user_id
    }

@router.put("/ai-settings", response_model=AISettingsResponse)
async def update_ai_settings(
    settings: AISettings,
    current_user: User = Depends(get_current_user)
):
    """Update AI settings for the current user"""
    user_id = current_user.id
    
    # Validate settings
    if settings.temperature < 0 or settings.temperature > 20:
        raise HTTPException(status_code=400, detail="Temperature must be between 0 and 20")
    
    if settings.max_tokens < 100 or settings.max_tokens > 8000:
        raise HTTPException(status_code=400, detail="Max tokens must be between 100 and 8000")
    
    if settings.top_k < 1 or settings.top_k > 20:
        raise HTTPException(status_code=400, detail="Top-K must be between 1 and 20")
    
    # Store settings
    user_settings[user_id] = settings.dict()
    
    return {
        **settings.dict(),
        "user_id": user_id
    }

@router.post("/ai-settings/reset", response_model=AISettingsResponse)
async def reset_ai_settings(
    current_user: User = Depends(get_current_user)
):
    """Reset AI settings to defaults"""
    user_id = current_user.id
    
    defaults = {
        "llm_model": "ollama_cloud",
        "embedding_model": "text-embedding-3-small",
        "temperature": 7,
        "max_tokens": 2000,
        "top_k": 5
    }
    
    user_settings[user_id] = defaults
    
    return {
        **defaults,
        "user_id": user_id
    }
