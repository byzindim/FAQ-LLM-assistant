#!/bin/bash

# Скачиваем и запускаем Ollama в фоне
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Ждем запуска Ollama
sleep 10

# Скачиваем модели (используем 3B для CPU)
ollama pull qwen2.5:3b
ollama pull bge-m3

# Запускаем API
uvicorn app.main:app --host 0.0.0.0 --port 7860
