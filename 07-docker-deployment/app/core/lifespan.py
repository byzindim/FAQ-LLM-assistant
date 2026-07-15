import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI.
    Replaces deprecated @app.on_event("startup"/"shutdown").
    """
    # === STARTUP ===
    logger.info("🚀 Starting FAQ-LLM-assistant API...")
    
    # 1. Создаём httpx-клиент и кладём в app.state
    # app.state — это "карман" приложения, доступный отовсюду
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(settings.ollama_timeout),
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=10)
    )
    logger.info(f"✅ HTTP client initialized (timeout={settings.ollama_timeout}s)")
    
    # 2. WARM-UP: прогреваем Ollama, чтобы модель загрузилась в VRAM
    try:
        logger.info(f"🔥 Warming up Ollama model '{settings.ollama_model}'...")
        warmup_response = await app.state.http_client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": "ping",
                "stream": False,
                "options": {"num_predict": 1}  # Генерируем ровно 1 токен — быстро
            }
        )
        warmup_response.raise_for_status()
        logger.info("✅ Ollama warmed up — model is in VRAM")
    except Exception as e:
        # Не падаем! Может, Ollama просто ещё не стартовала
        logger.warning(f"⚠️  Warm-up failed: {e}. First real request may be slow.")
    
    logger.info("🎉 API is ready to accept requests")
    
    yield  # <-- Приложение работает. Здесь оно живёт.
    
    # === SHUTDOWN ===
    logger.info("🛑 Shutting down...")
    await app.state.http_client.aclose()
    logger.info("✅ HTTP client closed")
