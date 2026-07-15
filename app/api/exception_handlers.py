from fastapi import Request
from fastapi.responses import JSONResponse
import logging

from app.core.exceptions import (
    FAQAssistantError, LLMTimeoutError, 
    OllamaUnavailableError
)

logger = logging.getLogger(__name__)


async def faq_error_handler(request: Request, exc: FAQAssistantError):
    """
    Generic handler for all our custom errors.
    Returns clean JSON instead of HTML traceback.
    """
    logger.error(
        f"FAQAssistantError: {exc.message}",
        extra={"details": exc.details, "path": request.url.path}
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": exc.message,
            "details": exc.details
        }
    )


async def llm_timeout_handler(request: Request, exc: LLMTimeoutError):
    """Specific handler for timeouts — returns 504 Gateway Timeout."""
    logger.warning(f"LLM Timeout: {exc.message}")
    return JSONResponse(
        status_code=504,
        content={
            "error": "llm_timeout",
            "message": "The AI model took too long to respond. Please try again."
        }
    )


async def ollama_unavailable_handler(request: Request, exc: OllamaUnavailableError):
    """Ollama is down — 503 Service Unavailable."""
    logger.error(f"Ollama unavailable: {exc.message}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "AI service is temporarily unavailable. Please try later."
        }
    )
