import os
import logging
import pickle
import faiss
import numpy as np
from threading import Thread
from typing import List, Dict

import uvicorn
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import pymorphy3

# ==========================================
# 1. НАСТРОЙКИ И ЛОГИРОВАНИЕ
# ==========================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PORT = int(os.environ.get("PORT", 8000))

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("Отсутствуют TELEGRAM_TOKEN или GROQ_API_KEY!")

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ RAG (Загружается ОДИН РАЗ при старте)
# ==========================================
logger.info("⏳ Загрузка RAG-артефактов и моделей...")

# Модель эмбеддингов
embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Загрузка данных
with open('documents.pkl', 'rb') as f:
    documents = pickle.load(f)

faiss_index = faiss.read_index('faiss_index.faiss')
with open('bm25_index.pkl', 'rb') as f:
    bm25_index = pickle.load(f)

morph = pymorphy3.MorphAnalyzer()
logger.info("✅ RAG-система успешно загружена в память!")

# ==========================================
# 3. ЛОГИКА RAG И LANGGRAPH (Упрощенная для бота)
# ==========================================
def lemmatize(text: str) -> str:
    return " ".join([morph.parse(w)[0].normal_form for w in text.lower().split()])

def hybrid_search(query: str, top_k: int = 3) -> List[Dict]:
    """Гибридный поиск: FAISS + BM25 + RRF"""
    # 1. FAISS
    query_emb = embedding_model.encode([query]).astype('float32')
    faiss.normalize_L2(query_emb)
    _, faiss_indices = faiss_index.search(query_emb, 10)
    
    # 2. BM25
    query_tokens = lemmatize(query).split()
    bm25_scores = bm25_index.get_scores(query_tokens)
    bm25_indices = np.argsort(bm25_scores)[::-1][:10].tolist()
    
    # 3. RRF (Reciprocal Rank Fusion)
    k = 60
    scores = {}
    for rank, idx in enumerate(faiss_indices[0]):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
    for rank, idx in enumerate(bm25_indices):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
        
    fused_indices = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
    return [documents[idx] for idx in fused_indices]

# ==========================================
# 4. TELEGRAM ОБРАБОТЧИКИ
# ==========================================
groq_client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я корпоративный AI-ассистент с гибридным RAG-поиском.\n\n"
        "Задай вопрос по HR, IT или регламентам компании."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    logger.info(f"📩 Вопрос: '{user_text}'")
    
    await update.message.chat.send_action("typing")
    
    if "ты кто" in user_text.lower():
        await update.message.reply_text("Я AI-ассистент, работающий на базе LangGraph, Hybrid RAG и Groq LLaMA-3 🤖")
        return

    try:
        # 1. Поиск контекста
        chunks = hybrid_search(user_text, top_k=3)
        context_text = "\n\n---\n\n".join([f"[Источник: {c.get('source', 'doc')}] {c['text']}" for c in chunks])
        
        # 2. Запрос к Groq (имитация узла Generator из LangGraph)
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Ты полезный корпоративный ассистент. Отвечай ИСКЛЮЧИТЕЛЬНО на основе контекста. Если ответа нет, скажи: 'К сожалению, в базе знаний нет этой информации.'\n\nКОНТЕКСТ:\n{context_text}"},
                {"role": "user", "content": user_text}
            ],
            temperature=0.1,
            max_tokens=512,
        )
        answer = completion.choices[0].message.content
        await update.message.reply_text(answer)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте перефразировать вопрос.")

def run_bot():
    logger.info("🤖 Запуск Telegram бота (polling)...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

# ==========================================
# 5. HEALTH CHECK ДЛЯ RENDER
# ==========================================
fastapi_app = FastAPI()

@fastapi_app.get("/")
@fastapi_app.get("/health")
async def health_check():
    return {"status": "healthy", "bot": "running", "rag_loaded": True}

def run_fastapi():
    logger.info(f"🌐 Запуск FastAPI на порту {PORT}...")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=PORT)

# ==========================================
# 6. ГЛАВНЫЙ ЗАПУСК
# ==========================================
if __name__ == "__main__":
    fastapi_thread = Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    run_bot()