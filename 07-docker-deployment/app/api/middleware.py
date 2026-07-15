import time
import uuid
import logging
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


def setup_logging():
    """
    Configure structlog for JSON output.
    Why structlog? Standard logging produces plain text.
    structlog produces JSON — easy to parse in ELK/Loki/Datadog.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,  # Подхватывает request_id из контекста
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()  # 🔥 Ключевое: вывод в JSON
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),  # ✅ ИСПРАВЛЕНО: structlog, не struct
        cache_logger_on_first_use=True
    )


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates/extracts request_id
    2. Puts it in structlog context (all logs in this request will have it)
    3. Measures latency and adds X-Process-Time header
    """
    
    async def dispatch(self, request: Request, call_next):
        # 1. Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # 2. Кладём в контекст structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path
        )
        
        # 3. Замеряем latency
        start = time.perf_counter()
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Если роут упал — всё равно логируем
            latency_ms = int((time.perf_counter() - start) * 1000)
            structlog.get_logger().error(
                "Request failed",
                latency_ms=latency_ms,
                error=str(e)
            )
            raise
        
        latency_ms = int((time.perf_counter() - start) * 1000)
        
        # 4. Добавляем заголовки в ответ
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(latency_ms)
        
        # 5. Логируем завершение
        structlog.get_logger().info(
            "Request completed",
            status_code=response.status_code,
            latency_ms=latency_ms
        )
        
        return response
