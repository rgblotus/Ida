import os
import logging
import uuid
import asyncio
import subprocess
import io
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple

from transformers import MarianMTModel, MarianTokenizer
from app.core.config import settings
from app.core.hardware import detect_device, get_hardware_info

logger = logging.getLogger(__name__)


class SpeechService:
    """High-quality neural TTS + English→Hindi translation with GPU acceleration"""

    TTS_ENGINE_ORDER = ["edge", "coqui", "piper", "espeak"]  # Quality priority

    def __init__(self):
        # Disable tokenizers parallelism warning
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'

        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)

        self.device = detect_device()
        self.hw_info = get_hardware_info()

        self.tts_engines: Dict[str, Dict[str, Any]] = {}
        self._initialize_tts_engines()
        self._initialize_translator()

    # ----------------------------------------------------------------------
    # TTS ENGINE INITIALIZATION
    # ----------------------------------------------------------------------

    def _initialize_tts_engines(self):
        """Initialize TTS engines in quality order."""
        self._initialize_edge_tts()
        self._initialize_coqui_tts()
        self._initialize_piper_tts()
        self._initialize_espeak_ng()

        available = [name for name, info in self.tts_engines.items() if info.get("available")]
        logger.info(f"🎵 TTS Engines initialized: {available}")
        if self.device == "cuda" and self.hw_info["gpu_available"]:
            logger.info(f"🚀 GPU acceleration available: {self.hw_info['gpu_names'][0]}")

    def _initialize_edge_tts(self):
        try:
            import edge_tts  # noqa
            self.tts_engines["edge"] = {
                "available": True,
                "quality": "excellent",
                "speed": "medium",
                "voices": [
                    "en-US-AriaRUS", "en-US-ZiraRUS", "en-US-BenjaminRUS",
                    "en-GB-George", "en-AU-Catherine"
                ]
            }
            logger.info("🎵 Edge TTS initialized (highest quality)")
        except ImportError:
            self.tts_engines["edge"] = {"available": False}
            logger.info("⚠️ Edge TTS not available (pip install edge-tts)")

    def _initialize_coqui_tts(self):
        try:
            from TTS.api import TTS
            models = TTS.list_models()
            en_models = [m for m in models if "tts_models/en/" in m]
            self.tts_engines["coqui"] = {
                "available": True,
                "quality": "very_good",
                "speed": "slow",
                "models": en_models[:5],
                "gpu_support": self.device == "cuda"
            }
            logger.info(f"🎵 Coqui TTS initialized ({len(en_models)} English models)")
        except ImportError:
            self.tts_engines["coqui"] = {"available": False}
            logger.info("⚠️ Coqui TTS not available (pip install TTS)")

    def _initialize_piper_tts(self):
        try:
            result = subprocess.run(["which", "piper"], capture_output=True, text=True)
            if result.returncode == 0:
                self.tts_engines["piper"] = {
                    "available": True,
                    "quality": "good",
                    "speed": "fast",
                    "voices": ["en_US-lessac-medium", "en_GB-alan-medium"]
                }
                logger.info("🎵 Piper TTS initialized (fast neural)")
            else:
                self.tts_engines["piper"] = {"available": False}
                logger.info("⚠️ Piper TTS not available (see github.com/rhasspy/piper)")
        except Exception:
            self.tts_engines["piper"] = {"available": False}

    def _initialize_espeak_ng(self):
        try:
            result = subprocess.run(
                ["espeak-ng", "--version"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                self.tts_engines["espeak"] = {
                    "available": True,
                    "quality": "poor",
                    "speed": "fast",
                    "voices": ["en-us", "en-gb"]
                }
                logger.info("🎵 espeak-ng initialized (fallback)")
            else:
                self.tts_engines["espeak"] = {"available": False}
        except FileNotFoundError:
            self.tts_engines["espeak"] = {"available": False}
            logger.warning("⚠️ espeak-ng not available (sudo apt install espeak-ng)")

    # ----------------------------------------------------------------------
    # TRANSLATOR INITIALIZATION & TRANSLATION
    # ----------------------------------------------------------------------

    def _initialize_translator(self):
        """Load MarianMT English→Hindi model with GPU fallback."""
        model_name = "Helsinki-NLP/opus-mt-en-hi"
        logger.info("Loading MarianMT translator (offline EN→HI)...")

        # Save original env
        old_cuda = os.environ.get("CUDA_VISIBLE_DEVICES")
        old_torch = os.environ.get("TORCH_DEVICE")

        try:
            import torch

            # Try GPU first
            if self.device == "cuda" and self.hw_info["gpu_available"]:
                try:
                    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
                    os.environ["TORCH_DEVICE"] = "cuda"
                    self.tokenizer = MarianTokenizer.from_pretrained(model_name)
                    self.model = MarianMTModel.from_pretrained(model_name).to("cuda")
                    logger.info(f"✅ Translation model loaded on GPU: {self.hw_info['gpu_names'][0]}")
                    return
                except Exception as e:
                    logger.warning(f"GPU loading failed: {e}, falling back to CPU")
                    if hasattr(self, "model"):
                        del self.model
                    if hasattr(self, "tokenizer"):
                        del self.tokenizer
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            # Fallback to CPU
            os.environ.pop("CUDA_VISIBLE_DEVICES", None)
            os.environ.pop("TORCH_DEVICE", None)
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name).to("cpu")
            logger.info("✅ Translation model loaded on CPU")

        except Exception as e:
            logger.error(f"Failed to load MarianMT: {e}")
            raise
        finally:
            # Restore env
            if old_cuda is not None:
                os.environ["CUDA_VISIBLE_DEVICES"] = old_cuda
            else:
                os.environ.pop("CUDA_VISIBLE_DEVICES", None)
            if old_torch is not None:
                os.environ["TORCH_DEVICE"] = old_torch
            else:
                os.environ.pop("TORCH_DEVICE", None)

    async def translate_text(self, text: str, target_lang: str = "hi") -> Optional[str]:
        if target_lang != "hi":
            logger.warning(f"Unsupported target language: {target_lang}")
            return None
        if not text.strip():
            return ""

        # Split long text into chunks to handle full translation
        max_chunk_length = 400  # Leave room for safety
        chunks = self._split_text_into_chunks(text, max_chunk_length)
        translated_chunks = []

        try:
            import torch
            device = next(self.model.parameters()).device

            for chunk in chunks:
                batch = self.tokenizer([chunk], return_tensors="pt", padding=True, truncation=True, max_length=512)
                batch = {k: v.to(device) for k, v in batch.items()}

                with torch.no_grad():
                    output = self.model.generate(**batch, max_new_tokens=512)
                translated_chunk = self.tokenizer.decode(output[0], skip_special_tokens=True)
                translated_chunks.append(translated_chunk)

            return " ".join(translated_chunks)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # fallback

    def _split_text_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks by sentences, respecting max length."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += (" " + sentence) if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def get_available_languages(self) -> List[Dict[str, Any]]:
        return [
            {
                "from": "en",
                "to": "hi",
                "name": "English → Hindi (MarianMT)",
                "type": "offline_neural_model"
            }
        ]

    # ----------------------------------------------------------------------
    # AUDIO GENERATION — CORE LOGIC
    # ----------------------------------------------------------------------

    async def generate_audio(
        self,
        text: str,
        filename: Optional[str] = None,
        voice: str = "auto",
        engine: str = "auto",
        rate: Optional[int] = None,
        output_format: str = "url"
    ) -> Optional[Union[str, bytes, Tuple[str, bytes]]]:
        if not text.strip():
            logger.warning("Empty text provided for TTS.")
            return None

        selected_engine = self._select_tts_engine(engine)
        if not selected_engine:
            logger.error("No TTS engines available")
            return None

        for attempt, eng in enumerate([selected_engine] + self._get_fallback_chain(selected_engine)):
            try:
                audio_bytes = await self._generate_audio_bytes(text, eng, voice, rate)
                if not audio_bytes or len(audio_bytes) < 1000:
                    continue

                ext = "wav"  # All engines output WAV
                final_filename = filename or f"speech_{uuid.uuid4()}.{ext}"
                relative_path = f"/uploads/{final_filename}"
                filepath = self.upload_dir / final_filename

                if output_format == "bytes":
                    return audio_bytes
                elif output_format == "base64":
                    mime = self._detect_audio_mime_type(audio_bytes)
                    b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    return f"data:{mime};base64,{b64}"
                else:  # "url" or "file"
                    with open(filepath, "wb") as f:
                        f.write(audio_bytes)
                    logger.info(f"✅ Audio generated: {final_filename} ({eng})")
                    return (relative_path, audio_bytes) if output_format == "file" else relative_path

            except Exception as e:
                logger.error(f"TTS attempt {attempt + 1} with {eng} failed: {e}")

        logger.error("All TTS attempts failed.")
        return None

    def _select_tts_engine(self, preferred: str) -> Optional[str]:
        if preferred != "auto" and self.tts_engines.get(preferred, {}).get("available"):
            return preferred
        for eng in self.TTS_ENGINE_ORDER:
            if self.tts_engines.get(eng, {}).get("available"):
                return eng
        return None

    def _get_fallback_chain(self, current: str) -> List[str]:
        try:
            idx = self.TTS_ENGINE_ORDER.index(current)
            return [e for e in self.TTS_ENGINE_ORDER[idx + 1:] if self.tts_engines.get(e, {}).get("available")]
        except ValueError:
            return []

    # ----------------------------------------------------------------------
    # AUDIO GENERATION — ENGINE-SPECIFIC IMPLEMENTATIONS
    # ----------------------------------------------------------------------

    async def _generate_audio_bytes(self, text: str, engine: str, voice: str, rate: Optional[int]) -> Optional[bytes]:
        try:
            if engine == "edge":
                return await self._generate_edge_tts_bytes(text, voice, rate)
            elif engine == "coqui":
                return await self._generate_coqui_tts_bytes(text, voice)
            elif engine == "piper":
                return await self._generate_piper_tts_bytes(text, voice, rate)
            elif engine == "espeak":
                return await self._generate_espeak_tts_bytes(text, voice, rate or 170)
            else:
                logger.error(f"Unknown TTS engine: {engine}")
                return None
        except Exception as e:
            logger.error(f"Error in {engine} TTS: {e}")
            return None

    async def _generate_edge_tts_bytes(self, text: str, voice: str, rate: Optional[int]) -> Optional[bytes]:
        try:
            import edge_tts
            voice = voice if voice != "auto" else "en-US-AriaRUS"
            communicate = edge_tts.Communicate(text, voice)
            if rate is not None:
                communicate.rate = f"{rate:+d}%"

            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data or None
        except Exception as e:
            logger.error(f"Edge TTS failed: {e}")
            return None

    async def _generate_coqui_tts_bytes(self, text: str, voice: str) -> Optional[bytes]:
        try:
            from TTS.api import TTS
            model = "tts_models/en/ljspeech/tacotron2-DDC_ph" if voice == "auto" else voice
            tts = TTS(model).to(self.device if self.device == "cuda" else "cpu")
            buffer = io.BytesIO()
            tts.tts_to_file(text=text, file_path=buffer)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            return None

    async def _generate_piper_tts_bytes(self, text: str, voice: str, rate: Optional[int]) -> Optional[bytes]:
        voice = voice if voice != "auto" else "en_US-lessac-medium"
        temp_file = self.upload_dir / f"temp_piper_{uuid.uuid4()}.wav"
        try:
            cmd = ["piper", "--model", voice, "--output_file", str(temp_file)]
            if rate:
                cmd.extend(["--length_scale", str(1.0 / (rate / 200.0))])
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            proc.stdin.write(text.encode())
            await proc.stdin.drain()
            proc.stdin.close()
            await proc.wait()

            if temp_file.exists():
                with open(temp_file, "rb") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Piper TTS failed: {e}")
        finally:
            if temp_file.exists():
                temp_file.unlink()
        return None

    async def _generate_espeak_tts_bytes(self, text: str, voice: str, rate: int) -> Optional[bytes]:
        temp_file = self.upload_dir / f"temp_espeak_{uuid.uuid4()}.wav"
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, self._espeak_ng_generate, text, str(temp_file), voice, rate)
            if success and temp_file.exists() and temp_file.stat().st_size > 1000:
                with open(temp_file, "rb") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"espeak-ng failed: {e}")
        finally:
            if temp_file.exists():
                temp_file.unlink()
        return None

    def _espeak_ng_generate(self, text: str, filepath: str, voice: str, rate: int) -> bool:
        voice = {"auto": "en-us", "en-us": "en-us", "en-gb": "en-gb"}.get(voice, "en-us")
        cmd = ["espeak-ng", "-v", voice, "-s", str(rate), "-w", filepath, text]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"espeak-ng stderr: {result.stderr}")
        return result.returncode == 0

    def _detect_audio_mime_type(self, audio_bytes: bytes) -> str:
        if len(audio_bytes) >= 12:
            if audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE":
                return "audio/wav"
            if audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
                return "audio/mpeg"
        return "audio/wav"

    # ----------------------------------------------------------------------
    # CONVENIENCE METHODS
    # ----------------------------------------------------------------------

    async def generate_audio_base64(self, text: str, voice: str = "auto", engine: str = "auto") -> Optional[str]:
        return await self.generate_audio(text, voice=voice, engine=engine, output_format="base64")

    async def generate_audio_bytes(self, text: str, voice: str = "auto", engine: str = "auto") -> Optional[bytes]:
        return await self.generate_audio(text, voice=voice, engine=engine, output_format="bytes")

    async def generate_audio_temp_file(self, text: str, voice: str = "auto", engine: str = "auto") -> Optional[str]:
        filename = f"temp_speech_{uuid.uuid4()}.wav"
        return await self.generate_audio(text, filename=filename, voice=voice, engine=engine, output_format="url")

    async def cleanup_old_audio_files(self, max_age_hours: int = 24) -> int:
        try:
            import time
            now = time.time()
            threshold = now - max_age_hours * 3600
            count = 0
            for f in self.upload_dir.glob("speech_*.wav"):
                if f.is_file() and f.stat().st_mtime < threshold:
                    f.unlink()
                    count += 1
            if count:
                logger.info(f"🧹 Cleaned up {count} old audio files")
            return count
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    # ----------------------------------------------------------------------
    # VOICE & ENGINE INFO
    # ----------------------------------------------------------------------

    async def get_available_voices(self) -> Dict[str, List[Dict[str, Any]]]:
        voices = {}
        for engine, info in self.tts_engines.items():
            if not info.get("available"):
                continue

            if engine == "edge":
                voices[engine] = [
                    {"id": "en-US-AriaRUS", "name": "Aria (Female)", "language": "en-US", "quality": "excellent"},
                    {"id": "en-US-ZiraRUS", "name": "Zira (Female)", "language": "en-US", "quality": "excellent"},
                    {"id": "en-US-BenjaminRUS", "name": "Benjamin (Male)", "language": "en-US", "quality": "excellent"},
                    {"id": "en-GB-George", "name": "George (Male)", "language": "en-GB", "quality": "excellent"},
                    {"id": "en-AU-Catherine", "name": "Catherine (Female)", "language": "en-AU", "quality": "excellent"},
                ]
            elif engine == "coqui":
                voices[engine] = [
                    {"id": "tts_models/en/ljspeech/tacotron2-DDC_ph", "name": "Tacotron2-DDC", "language": "en", "quality": "very_good"},
                    {"id": "tts_models/en/ljspeech/glow-tts", "name": "Glow-TTS", "language": "en", "quality": "very_good"},
                ]
            elif engine == "piper":
                voices[engine] = [
                    {"id": "en_US-lessac-medium", "name": "Lessac (US)", "language": "en-US", "quality": "good"},
                    {"id": "en_GB-alan-medium", "name": "Alan (GB)", "language": "en-GB", "quality": "good"},
                ]
            elif engine == "espeak":
                voices[engine] = [
                    {"id": "en-us", "name": "US English", "language": "en-US", "quality": "poor"},
                    {"id": "en-gb", "name": "GB English", "language": "en-GB", "quality": "poor"},
                ]
        return voices

    async def get_voice_quality_info(self) -> Dict[str, Any]:
        return {
            "recommended_engine": "edge",
            "quality_order": self.TTS_ENGINE_ORDER,
            "gpu_accelerated": ["coqui"],
            "tips": {
                "naturalness": "Edge TTS > Coqui TTS > Piper TTS > espeak-ng",
                "speed": "espeak-ng > Piper TTS > Edge TTS > Coqui TTS",
                "languages": "All support English; Edge has most variety",
                "offline": "All except Edge TTS work fully offline",
            }
        }

    # ----------------------------------------------------------------------
    # HEALTH CHECK
    # ----------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        health = {
            "translation_available": False,
            "upload_dir_exists": self.upload_dir.exists(),
            "upload_dir_writable": False,
            "sample_translation": None,
            "gpu_accelerated": self.device == "cuda" and self.hw_info["gpu_available"],
            "gpu_info": self.hw_info["gpu_names"][0] if self.hw_info["gpu_available"] else None,
            "output_formats": ["url", "base64", "bytes", "file"],
            "no_file_options": ["base64", "bytes"],
            "tts_engines": {},
            "audio_cleanup_available": True,
        }

        # Test upload dir
        try:
            test_file = self.upload_dir / ".writable_test"
            test_file.write_text("ok")
            test_file.unlink()
            health["upload_dir_writable"] = True
        except Exception:
            pass

        # Test each TTS engine
        for name, info in self.tts_engines.items():
            engine_health = {
                "available": info.get("available", False),
                "quality": info.get("quality", "unknown"),
                "speed": info.get("speed", "unknown"),
                "gpu_supported": name == "coqui",
                "test_passed": False,
                "output_formats": ["wav"],
            }
            if engine_health["available"]:
                try:
                    audio = await self.generate_audio("Hello", engine=name, output_format="base64")
                    engine_health["test_passed"] = bool(audio and len(audio) > 1000)
                except Exception as e:
                    logger.warning(f"TTS test failed for {name}: {e}")
            health["tts_engines"][name] = engine_health

        # Test translation
        try:
            sample = await self.translate_text("hello world")
            health["sample_translation"] = sample
            health["translation_available"] = True
            device = str(next(self.model.parameters()).device)
            health["translation_device"] = device
            health["translation_gpu_accelerated"] = "cuda" in device
        except Exception as e:
            logger.error(f"Translation test failed: {e}")

        health["tts_available"] = any(e["available"] for e in health["tts_engines"].values())

        health["usage_tips"] = {
            "no_files": "Use output_format='base64' or 'bytes' to avoid saving files",
            "cleanup": "Call cleanup_old_audio_files() periodically",
            "best_quality": "Edge TTS for naturalness; Coqui for GPU",
            "streaming": "Use 'base64' for frontend integration"
        }

        return health