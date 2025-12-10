#!/usr/bin/env python3
"""
Script to test Hindi translation functionality
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.speech_service import SpeechService
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_translation():
    """Test Hindi translation functionality"""
    try:
        logger.info("🧪 Testing Hindi translation...")

        # Initialize speech service (this loads the translator)
        speech_service = SpeechService()

        # Test basic translation
        test_texts = [
            "Hello world",
            "How are you?",
            "Thank you very much",
            "I love programming",
            "This is a test message"
        ]

        logger.info("📝 Testing translation with sample texts:")
        for text in test_texts:
            try:
                translated = await speech_service.translate_text(text)
                logger.info(f"   EN: {text}")
                logger.info(f"   HI: {translated}")
                logger.info("   ---")
            except Exception as e:
                logger.error(f"   ❌ Failed to translate: {text} - {e}")

        # Test health check
        logger.info("🏥 Checking translation health...")
        health = await speech_service.health_check()

        if health.get('translation_available'):
            logger.info("✅ Translation is working!")
            logger.info(f"   Sample translation: {health.get('sample_translation')}")
        else:
            logger.error("❌ Translation is not available")

        return True

    except Exception as e:
        logger.error(f"❌ Translation test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_translation())
    if success:
        logger.info("🎉 Translation test completed successfully!")
    else:
        logger.error("💥 Translation test failed!")
        sys.exit(1)