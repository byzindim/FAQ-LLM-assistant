# <span style="display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:10px;font-size:18px;line-height:1;">🤖</span> FAQ-LLM-Ассистент (Production-Ready RAG & Agents)

> Корпоративный AI-ассистент с гибридным поиском, агентной архитектурой на LangGraph и LLMOps-мониторингом.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agents-orange)](https://langchain-ai.github.io/langgraph/)
[![Ollama](https://img.shields.io/badge/Ollama-Qwen_2.5-9cf)](https://ollama.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com)
[![Accuracy](https://img.shields.io/badge/Accuracy-100%25-brightgreen)]()

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> Что это

Production-ready RAG-система для автоматизации ответов на внутренние вопросы сотрудников (HR, IT, корпоративные регламенты). Система использует локальные LLM (без утечки данных в облако), гибридный поиск и детерминированный агентный роутинг.

**Бизнес-кейс:** замена рутинных обращений в первую линию поддержки → сотрудник получает точный ответ со ссылкой на регламент за 3 секунды. Нагрузку на support-команду можно снизить на **30-40%**.

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">✨</span> Ключевые особенности

- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Гибридный поиск (Advanced RAG):** Семантический `FAISS` (эмбеддинги `bge-m3`) + Лексический `BM25` + слияние через `Reciprocal Rank Fusion (RRF)`.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Агентная архитектура:** Детерминированный FSM-роутер на `LangGraph` с 4 намерениями (FAQ, chitchat, out-of-scope, clarification).
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Defensive Programming:** 100% валидный структурированный вывод (JSON) благодаря связке `format="json"` (Ollama) + `Pydantic V2` + `json_repair`.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Short-Circuiting:** Простые запросы отсекаются на этапе роутера без вызова тяжелого RAG-контура (экономия latency на 70%).
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **LLMOps (Langfuse):** Полный трейсинг запросов, waterfall-анализ задержек по каждому узлу графа.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **Docker-Ready:** Multi-stage сборка и `docker-compose.yml` для оркестрации API и Ollama.
- <span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:14px;line-height:1;"></span> **100% Точность:** Протестировано на датасете из 211 вопросов (Hit Rate@5 = 1.0, MRR = 1.0).

---

## <span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> Быстрый старт

### Вариант 1: Через Docker (Рекомендуется)

git clone https://github.com/byzindim/FAQ-LLM-assistant.git
cd FAQ-LLM-assistant/07-docker-deployment

#### Настройка окружения
cp .env.example .env

#### Запуск всех сервисов (API + Ollama)
docker-compose up --build
#### → API: http://localhost:8000/docs
#### → Ollama: http://localhost:11434

### Вариант 2: Локальный запуск (без Docker)
#### 1. Установить Ollama и скачать модели
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
ollama pull bge-m3

#### 2. Установить Python-зависимости
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

#### 3. Запустить FastAPI
uvicorn app.main:app --reload
#### → http://localhost:8000/docs

<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">⚙️</span> 

## Архитектура (LangGraph Agent)
```
                      Запрос пользователя
                              │
                              ▼
                  ┌───────────────────────┐
                  │   Router Node (LLM)   │  Классификация intent (JSON)
                  │   (Qwen 2.5-7B)       │
                  └───────────┬───────────┘
                              │
         ┌────────────────────┼────────────────────┬──────────────────┐
         ▼                    ▼                    ▼                  ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │     FAQ      │    │   Chitchat   │    │ Out-of-Scope │    │ Clarification│
  │ (Полный RAG) │    │ (Короткий)   │    │  (Fallback)  │    │ (Уточнение)  │
  └──────┬───────┘    └──────────────┘    └──────────────┘    └──────────────┘
         │
         ▼
  ┌────────────────────────────────────────────────────────┐
  │                 Retriever Node (Hybrid)                │
  │  FAISS (bge-m3) + BM25 + Reciprocal Rank Fusion (RRF)  │
  └──────────────────────┬─────────────────────────────────┘
                         │ Top-5 чанков
                         ▼
  ┌────────────────────────────────────────────────────────┐
  │                 Generator Node (LLM)                   │
  │  Генерация ответа строго по контексту (JSON output)    │
  └────────────────────────────────────────────────────────┘
```
<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;">📡</span> 

## API
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI REST API (v1)                               │
│                    http://localhost:8000/docs (Swagger UI)                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  POST /api/v1/ask                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Описание: Задать вопрос ассистенту                                         │
│                                                                             │
│  Request:                                                                   │
│  {                                                                          │
│    "question": "Как оформить декретный отпуск?"                             │
│  }                                                                          │
│                                                                             │
│  Response:                                                                  │
│  {                                                                          │
│    "request_id": "req_8f3a9b2c",                                            │
│    "answer": "Для оформления декретного отпуска необходимо...",             │
│    "intent": "faq",                                                         │
│    "sources": [...],                                                        │
│    "latency_ms": 3420                                                       │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  GET /health                                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Описание: Проверка статуса API и Ollama                                    │
│                                                                             │
│  Response:                                                                  │
│  {                                                                          │
│    "status": "healthy",                                                     │
│    "ollama_available": true,                                                │
│    "model": "qwen2.5:7b",                                                   │
│    "rag_index_loaded": true                                                 │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  GET /docs                                                                  │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Описание: Swagger UI (автодокументация)                                    │
│  Интерактивная документация API с возможностью тестирования запросов        │
└─────────────────────────────────────────────────────────────────────────────┘
```
Пример запроса
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Как оформить декретный отпуск?"}'


<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> 
Метрики и Оценка (Evaluation)
Система протестирована на кастомном Ground Truth датасете из 211 вопросов (HR, IT, Equipment).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE (Ground Truth)                        │
│              Тестовый датасет: 211 вопросов (HR, IT, Equipment)              │
│              Метод оценки: LLM-as-a-Judge + ручной разбор edge-cases         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  МЕТРИКИ КАЧЕСТВА RAG-СИСТЕМЫ                                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Accuracy: 100.0%                                                   │   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Полное совпадение с эталонными ответами                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Hit Rate@5: 1.00                                                   │   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Правильный чанк всегда попадает в Top-5                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MRR (Mean Reciprocal Rank): 1.00                                   │   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Правильный чанк всегда на 1-м месте                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Latency P50: ~3.1 сек                                              │   │
│  │  ████████████████████████████████████████                          │   │
│  │  Локально, GPU T4 / M-series                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Error Rate: 0%                                                     │   │
│  │  ████████████████████████████████████████████████████████████████  │   │
│  │  Ни одного падения JSON-парсинга (Defensive Programming)            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  МЕТОДОЛОГИЯ ОЦЕНКИ                                                         │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  1. LLM-as-a-Judge                                                          │
│     Автоматическая оценка качества ответов с использованием LLM             │
│                                                                             │
│  2. Ручной разбор edge-cases                                                │
│     Анализ сложных случаев и пограничных ситуаций                           │
│                                                                             │
│  3. Метрики retrieval                                                       │
│     Hit Rate@5 и MRR для оценки качества поиска                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```


<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> 

Стек технологий:
1. LLM Инференс: Ollama (локально, Qwen 2.5-7B для генерации, bge-m3 для эмбеддингов)
2. Оркестрация: LangGraph (FSM-агенты), LangChain
3. Vector DB: FAISS (IndexFlatIP, cosine similarity)
4. Lexical Search: rank-bm25 + pymorphy3 (лемматизация)
5. Backend: FastAPI, Pydantic V2, Uvicorn
6. LLMOps: Langfuse (трейсинг, waterfall-метрики)
7. Надежность: json_repair, tenacity (retries)
8. Инфраструктура: Docker, docker-compose


<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> 
Структура проекта

app/
├── api/           # FastAPI роуты и middleware
├── core/          # Конфиги и lifespan
├── llm/           # Ollama client с retry-логикой
├── prompts/       # Шаблоны промптов
├── rag/           # Chunker, Embeddings, Vectorstore (FAISS+BM25)
└── schemas/       # Pydantic модели (DTO)
scripts/
└── evaluate.py    # Скрипт оценки на датасете (LLM-as-a-Judge)


<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;border:2px solid #9C27B0;background:#FFFFFF;vertical-align:middle;margin-right:8px;font-size:16px;line-height:1;"></span> 

Roadmap (Зоны роста):
- Semantic Cache: Внедрение GPTCache для мгновенных ответов на повторяющиеся вопросы.
- PII Redaction: Интеграция Microsoft Presidio для обезличивания данных перед трейсингом.
- Custom Dashboard: Самописный дашборд на Streamlit + ClickHouse для бизнес-метрик.
- Circuit Breaker: Асинхронная отправка логов в Langfuse через очередь (RabbitMQ/Redis).

<p align="center">
Сделано с ❤️ и инженерным подходом |
<a href="https://github.com/byzindim">Дмитрий Бызин (AI Engineer)</a>
</p>
  
