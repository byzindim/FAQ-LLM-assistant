# ЭТАП 7: Docker + Деплой (Контейнеризация)

**Статус:** ГОТОВО К ДЕПЛОЮ

---

## Что в этой папке

- `Dockerfile` - Мультистейдж-сборка для production
- `docker-compose.yml` - Оркестрация сервисов (Ollama + FastAPI + опционально Langfuse)
- `requirements.txt` - Python-зависимости
- `.env.example` - Шаблон переменных окружения
- `hf_spaces/` - Файлы для деплоя на Hugging Face Spaces
- `app/` - Исходный код FastAPI
- `scripts/` - Скрипты оценки и отладки
- `rag_artifacts/` - RAG-база (FAISS, BM25, 211 чанков)

---

## Локальный запуск (Docker)

### 1. Клонируй репозиторий:
```bash
git clone https://github.com/твой-ник/faq-assistant.git
cd faq-assistant/07-docker-deployment
```

### 2. Создай .env файл:
```bash
cp .env.example .env
# Отредактируй .env и вставь свои ключи Langfuse (если нужно)
```

### 3. Запусти через docker-compose:
```bash
docker-compose up --build
```

### 4. Открой API:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 5. Останови контейнеры:
```bash
docker-compose down
```

---

## Деплой на Hugging Face Spaces (БЕСПЛАТНО)

### Шаг 1: Создай Space на HF
1. Зайди на https://huggingface.co
2. Нажми New Space
3. Выбери:
   - Name: faq-assistant (или любое другое)
   - SDK: **Docker**
   - Visibility: Public

### Шаг 2: Загрузи файлы из папки hf_spaces/
1. В своем Space нажми Files - Add file - Upload files
2. Загрузи:
   - hf_spaces/Dockerfile (переименуй в Dockerfile)
   - hf_spaces/start.sh
   - hf_spaces/requirements.txt
   - Папку app/ целиком
   - Папку rag_artifacts/ целиком

3. Нажми Commit changes

### Шаг 3: Настрой переменные окружения (опционально)
1. В Space зайди в Settings - Variables and secrets
2. Добавь:
   - LANGFUSE_PUBLIC_KEY
   - LANGFUSE_SECRET_KEY
   - LANGFUSE_HOST

### Шаг 4: Жди сборки (5-10 минут)
HF Spaces автоматически соберет Docker-образ и запустит его.

### Шаг 5: Открой публичную ссылку
```
https://huggingface.co/spaces/твой-ник/faq-assistant
```

API будет доступен по адресу:
```
https://твой-ник-faq-assistant.hf.space/docs
```

---

## Middle-Level инсайты

### Почему мультистейдж-сборка?
- **Builder stage:** Устанавливаем все зависимости с компиляторами (gcc, g++)
- **Runtime stage:** Копируем только готовые пакеты, без компиляторов
- **Результат:** Образ уменьшается с ~2 GB до ~500 MB

### Почему health checks?
- Docker автоматически перезапускает контейнер, если health check падает
- depends_on: condition: service_healthy гарантирует, что API стартует только после Ollama

### Почему volumes?
- ollama_data: сохраняет скачанные модели между перезапусками
- rag_artifacts: позволяет обновлять базу знаний без пересборки образа

### Почему qwen2.5:3b для HF Spaces?
- HF Spaces дает только CPU (2 vCPU, 16 GB RAM)
- Модель 7B на CPU отвечает ~3-5 секунд на токен (слишком медленно)
- Модель 3B отвечает ~1-2 секунды на токен (приемлемо для демо)
- В production с GPU можно использовать 7B без изменений кода

---

## Метрики системы

- **Accuracy:** 100.0% (211 вопросов)
- **Error Rate:** 0%
- **Latency (GPU T4):** ~3.4 сек
- **Latency (CPU):** ~6-10 сек (зависит от модели)
- **Docker image size:** ~500 MB (мультистейдж)

---

## Следующие шаги

- **Этап 8:** Финальная оценка и A/B-тест (Голый RAG vs Агент)
- **Этап 9:** Безопасность и инъекции (rate limiting, auth)
- **Этап 10:** Упаковка в портфолио (видео-демо, презентация)

---

**Готов к деплою!**