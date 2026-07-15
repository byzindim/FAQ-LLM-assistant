# ==============================================================================
# ЭТАП 1: Builder - собираем зависимости
# ==============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==============================================================================
# ЭТАП 2: Runtime - финальный образ
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для runtime (меньше, чем в builder)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные Python-пакеты из builder
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY app/ ./app/
COPY scripts/ ./scripts/

# Создаем директорию для RAG-артефактов (будет смонтирована из volume)
RUN mkdir -p /app/rag_artifacts

# Переменные окружения по умолчанию
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OLLAMA_HOST=http://ollama:11434 \
    RAG_DIR=/app/rag_artifacts \
    PORT=8000

# Открываем порт для FastAPI
EXPOSE 8000

# Health check для проверки работоспособности
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
