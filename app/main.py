import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.exceptions import (
    FAQAssistantError, LLMTimeoutError, OllamaUnavailableError
)
from app.api.exception_handlers import (
    faq_error_handler, llm_timeout_handler, ollama_unavailable_handler
)
from app.api.middleware import RequestTracingMiddleware, setup_logging
from app.api.routes import faq, health


# 1. Настраиваем логи ПЕРЕД всем остальным
setup_logging()
logger = logging.getLogger(__name__)


# 2. Создаём приложение
app = FastAPI(
    title="FAQ LLM Assistant",
    description="Corporate AI assistant for HR/IT support",
    version="0.3.0",
    lifespan=lifespan,  # 🔥 Подключаем lifespan из Шага 2
    docs_url="/docs",
    redoc_url="/redoc"
)


# 3. Регистрируем exception handlers
app.add_exception_handler(LLMTimeoutError, llm_timeout_handler)
app.add_exception_handler(OllamaUnavailableError, ollama_unavailable_handler)
app.add_exception_handler(FAQAssistantError, faq_error_handler)


# 4. Регистрируем middleware (порядок важен! Последний добавленный — первый выполняется)
app.add_middleware(RequestTracingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене — конкретные домены
    allow_methods=["*"],
    allow_headers=["*"],
)


# 5. Подключаем роуты
app.include_router(faq.router)
app.include_router(health.router)


# 6. Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "FAQ LLM Assistant",
        "version": "0.3.0",
        "docs": "/docs"
    }


# 7. Точка входа для запуска
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development"
    )
