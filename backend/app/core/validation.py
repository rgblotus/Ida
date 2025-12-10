"""Input validation utilities for the application"""

from typing import Optional
from fastapi import HTTPException
from app.core.constants import LLMConstants, VectorStoreConstants, ErrorMessages

def validate_llm_model(model: str) -> str:
    """Validate LLM model name"""
    if model not in LLMConstants.VALID_LLM_MODELS:
        raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_LLM_MODEL)
    return model

def validate_temperature(temp: float) -> float:
    """Validate temperature value"""
    if not (LLMConstants.MIN_TEMPERATURE <= temp <= LLMConstants.MAX_TEMPERATURE):
        raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TEMPERATURE)
    return temp

def validate_top_k(k: int) -> int:
    """Validate top-k value"""
    if not (VectorStoreConstants.MIN_TOP_K <= k <= VectorStoreConstants.MAX_TOP_K):
        raise HTTPException(status_code=400, detail=ErrorMessages.INVALID_TOP_K)
    return k

def validate_collection_name(name: Optional[str]) -> Optional[str]:
    """Validate collection name"""
    if name and len(name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Collection name cannot be empty")
    return name

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not text:
        return ""
    return text.strip()[:max_length]

def validate_message_role(role: str) -> str:
    """Validate message role"""
    if role not in LLMConstants.VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}. Must be one of {LLMConstants.VALID_ROLES}")
    return role