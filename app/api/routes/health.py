from fastapi import APIRouter, Depends, Request
import httpx
import logging

from app.schemas.api import HealthResponse
from app.core.config import settings
from app.api.deps import get_http_client

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    request: Request,
    client: httpx.AsyncClient = Depends(get_http_client)  # ✅ Используем DI
):
    """
    Deep health check: verifies that Ollama is alive and model is loaded.
    Used by Docker/K8s to decide whether to restart the container.
    
    Теперь использует DI — легко тестировать через dependency_overrides.
    """
    try:
        # Лёгкий запрос — проверяем, что Ollama отвечает
        response = await client.get(f"{settings.ollama_base_url}/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = [m.get("name") for m in models]
        
        ollama_ok = settings.ollama_model in model_names or any(
            settings.ollama_model in name for name in model_names
        )
        
        return HealthResponse(
            status="healthy" if ollama_ok else "degraded",
            ollama_available=ollama_ok,
            model=settings.ollama_model if ollama_ok else None
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            ollama_available=False,
            model=None
        )
