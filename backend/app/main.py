import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import setup_logging
from app.api.v1 import auth, weather, user_settings, chats, documents, collections
from app.infra import Base
from app.infra.database import engine

# Setup logging
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Niki RAG API",
    version="0.2.0",
    description="RAG Application with LangChain, Milvus, and Ollama",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={"persistAuthorization": True},
)

# CORS – tighten in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(collections.router, prefix="/api/v1/collections", tags=["collections"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(chats.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])
app.include_router(user_settings.router, prefix="/api/v1/settings", tags=["settings"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.2.0"}

@app.get("/api/v1/llm/status")
async def llm_status():
    """Check LLM availability"""
    from app.services.service_manager import get_llm_service

    llm_service = get_llm_service()
    available_llms = llm_service.get_available_llms()

    return {
        "available_llms": available_llms,
        "ollama_model": settings.OLLAMA_MODEL,
        "primary": "ollama_cloud" if "ollama_cloud" in available_llms else "ollama_local"
    }

@app.get("/api/v1/hardware/status")
async def hardware_status():
    """Check hardware availability and configuration"""
    from app.core.hardware import get_hardware_info

    hardware_info = get_hardware_info()

    return {
        "hardware": hardware_info,
        "services": {
            "embedding_device": "Detecting...",
            "vector_store": "Milvus",
            "llm_providers": ["Ollama", "OpenAI", "Google"]
        }
    }

@app.get("/api/v1/speech/status")
async def speech_status():
    """Check speech services (TTS and translation) availability"""
    from app.services.service_manager import get_speech_service

    speech_service = get_speech_service()
    health = await speech_service.health_check()

    return {
        "speech_services": health,
        "instructions": {
            "if_tts_not_available": "Install system TTS: Ubuntu/Debian: sudo apt install espeak, macOS: built-in, Windows: built-in",
            "if_translation_not_working": "Translation uses offline dictionary - limited vocabulary",
            "test_translation": "Try phrases like 'hello', 'thank you', 'how are you'",
            "test_audio": "Click speaker icon on any AI response"
        }
    }

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    # Database initialization is handled by init_db.py script
    # No need to call it here

    # Create upload directory
    import os
    from app.core.config import settings
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    print(f"✅ Upload directory created: {settings.UPLOAD_DIR}")

    # Pre-initialize services to avoid lazy loading overhead
    print("🚀 Pre-initializing services...")
    try:
        from app.services.service_manager import (
            get_embedding_service,
            get_vector_store_service,
            get_llm_service,
            get_rag_service,
            get_speech_service,
            get_chat_service
        )

        # Initialize in dependency order
        embedding_svc = get_embedding_service()
        print("✅ Embedding service initialized")

        vector_svc = get_vector_store_service()
        print("✅ Vector store service initialized")

        llm_svc = get_llm_service()
        print("✅ LLM service initialized")

        rag_svc = get_rag_service()
        print("✅ RAG service initialized")

        speech_svc = get_speech_service()
        print("✅ Speech service initialized")

        chat_svc = get_chat_service()
        print("✅ Chat service initialized")

        print("🎉 All services pre-initialized successfully!")

    except Exception as e:
        print(f"⚠️  Service pre-initialization failed: {e}")
        print("Services will be initialized lazily as needed")

# Mount static files
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")