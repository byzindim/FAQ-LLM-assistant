from fastapi import APIRouter, Request
from app.schemas.api import AskRequest, AskResponse, FAQAnswer
from app.llm.ollama_client import ollama_client
from app.prompts.base import RAG_JSON_TEMPLATE
from app.rag.vectorstore import vector_store
import time
import uuid

router = APIRouter()

def format_rag_context(docs: list[dict]) -> str:
    """Форматируем контекст с метаданными."""
    if not docs:
        return "Контекст не найден."
    formatted = []
    for i, doc in enumerate(docs, 1):
        formatted.append(f"[Документ {i}] Источник: {doc['source']} | Раздел: {doc['header']}\n{doc['text']}")
    return "\n\n---\n\n".join(formatted)

@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, request: Request):
    start_time = time.time()
    
    # 🔥 Простой гибридный поиск с k=8
    docs = await vector_store.search(req.question, k=8)
    
    context = format_rag_context(docs)
    prompt = RAG_JSON_TEMPLATE.format(context=context, question=req.question)
    
    # Вызов LLM
    faq_answer: FAQAnswer = await ollama_client.generate_structured(prompt)
    
    # Обогащаем ответ метаданными из RAG
    try:
        if faq_answer.confidence > 0.7 and docs:
            faq_answer.source = docs[0]["source"]
    except Exception:
        pass
    
    # Преобразуем FAQAnswer в AskResponse
    latency_ms = int((time.time() - start_time) * 1000)
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    
    response = AskResponse(
        request_id=request_id,
        answer=faq_answer.answer,
        category=faq_answer.category,
        confidence=faq_answer.confidence,
        source=faq_answer.source,
        latency_ms=latency_ms
    )
    
    return response
