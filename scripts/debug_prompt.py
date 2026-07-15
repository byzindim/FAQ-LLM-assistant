import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.rag.vectorstore import vector_store
from app.prompts.base import RAG_JSON_TEMPLATE

async def debug_prompt():
    # Проблемные вопросы
    questions = [
        "Как получить доступ к корпоративной почте?",
        "Как сбросить пароль от почты?",
        "Когда выплачиваются премии?"
    ]
    
    for q in questions:
        print(f"\n{'='*80}")
        print(f"❓ Вопрос: {q}")
        print(f"{'='*80}")
        
        # 1. Что находит FAISS
        docs = await vector_store.search(q, k=3)
        
        print(f"\n📚 Найденные чанки ({len(docs)}):")
        for i, doc in enumerate(docs, 1):
            print(f"\n  Чанк {i} (score: {doc['score']:.4f}):")
            print(f"  Источник: {doc['source']}")
            print(f"  Раздел: {doc['header']}")
            print(f"  Текст: {doc['text'][:200]}...")
        
        # 2. Формируем контекст
        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(f"[Документ {i}] Источник: {doc['source']} | Раздел: {doc['header']}\n{doc['text']}")
        context = "\n\n---\n\n".join(formatted)
        
        # 3. Показываем финальный промпт
        prompt = RAG_JSON_TEMPLATE.format(context=context, question=q)
        
        print(f"\n📝 ФИНАЛЬНЫЙ ПРОМПТ (первые 1500 символов):")
        print("-" * 80)
        print(prompt[:1500])
        print("-" * 80)

asyncio.run(debug_prompt())
