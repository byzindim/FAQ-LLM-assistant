FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код приложения
COPY app/ ./app/

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=http://localhost:11434 \
    RAG_DIR=/app/rag_artifacts \
    PORT=7860

# Открываем порт HF Spaces
EXPOSE 7860

# Скрипт запуска (скачивает Ollama и модели)
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
