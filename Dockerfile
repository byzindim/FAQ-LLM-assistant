FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для pymorphy3 и faiss
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код и RAG-артефакты
COPY . .

# Render требует порт (мы используем 8000 для health check)
EXPOSE 8000

# Запуск единого файла, который поднимет и API, и бота
CMD ["python", "bot.py"]