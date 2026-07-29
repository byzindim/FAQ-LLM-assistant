import os
import logging
import pickle
import faiss
import numpy as np
from threading import Thread
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import pymorphy3

# ==========================================
# 1. ЛОГИРОВАНИЕ
# ==========================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# 2. ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PORT = int(os.environ.get("PORT", 8000))

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("Отсутствуют TELEGRAM_TOKEN или GROQ_API_KEY!")

# ==========================================
# 3. ЗАГРУЗКА RAG (один раз при старте)
# ==========================================
logger.info("⏳ Загрузка RAG-артефактов и моделей...")

embedding_model = SentenceTransformer('BAAI/bge-m3')

with open('documents.pkl', 'rb') as f:
    documents = pickle.load(f)

faiss_index = faiss.read_index('faiss_index.faiss')

with open('bm25_index.pkl', 'rb') as f:
    bm25_index = pickle.load(f)

morph = pymorphy3.MorphAnalyzer()
logger.info(f"✅ RAG загружен: {len(documents)} чанков, размерность {faiss_index.d}")

# ==========================================
# 4. ГИБРИДНЫЙ ПОИСК (FAISS + BM25 + RRF)
# ==========================================
def lemmatize(text: str) -> str:
    return " ".join([morph.parse(w)[0].normal_form for w in text.lower().split()])

def hybrid_search(query: str, top_k: int = 3) -> List[Dict]:
    # FAISS (семантический поиск)
    query_emb = embedding_model.encode([query]).astype('float32')
    faiss.normalize_L2(query_emb)
    _, faiss_indices = faiss_index.search(query_emb, 10)

    # BM25 (ключевые слова)
    query_tokens = lemmatize(query).split()
    bm25_scores = bm25_index.get_scores(query_tokens)
    bm25_indices = np.argsort(bm25_scores)[::-1][:10].tolist()

    # Reciprocal Rank Fusion
    k = 60
    scores = {}
    for rank, idx in enumerate(faiss_indices[0]):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
    for rank, idx in enumerate(bm25_indices):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)

    fused = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:top_k]
    return [documents[idx] for idx in fused]

# ==========================================
# 5. TELEGRAM ОБРАБОТЧИКИ
# ==========================================
groq_client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я корпоративный AI-ассистент.\n\n"
        "Задай вопрос по HR, IT или регламентам компании."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    logger.info(f"📩 Вопрос: '{user_text}'")

    await update.message.chat.send_action("typing")

    if "ты кто" in user_text.lower():
        await update.message.reply_text(
            "Я AI-ассистент с гибридным RAG-поиском "
            "(bge-m3 + FAISS + BM25) и Groq LLaMA-3 🤖"
        )
        return

    try:
        chunks = hybrid_search(user_text, top_k=3)
        context_text = "\n\n---\n\n".join(
            [f"[{c.get('source', 'doc')}] {c['text']}" for c in chunks]
        )

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты корпоративный ассистент. Отвечай ТОЛЬКО "
                        "на основе контекста. Если ответа нет, скажи: "
                        "'В базе знаний нет этой информации.'\n\n"
                        f"КОНТЕКСТ:\n{context_text}"
                    )
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.1,
            max_tokens=512,
        )
        await update.message.reply_text(completion.choices[0].message.content)

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        await update.message.reply_text(
            "⚠️ Ошибка обработки. Попробуйте перефразировать вопрос."
        )

# ==========================================
# 6. FASTAPI HEALTH CHECK
# ==========================================
app = FastAPI()

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "healthy", "bot": "running", "model": "bge-m3"}

def run_fastapi():
    logger.info(f"🌐 FastAPI на порту {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# ==========================================
# 7. ГЛАВНЫЙ ЗАПУСК
# ==========================================
if __name__ == "__main__":
    Thread(target=run_fastapi, daemon=True).start()

    logger.info("🤖 Запуск Telegram бота (polling)...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)