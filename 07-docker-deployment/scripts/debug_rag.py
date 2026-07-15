import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.rag.vectorstore import vector_store

async def debug_search():
    # Проблемные вопросы
    questions = [
        "Когда выплачиваются премии?",
        "Какой формат корпоративной почты?",
        "Как запросить доступ к 1С?",
        "Как сбросить пароль от почты?"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"❓ Вопрос: {q}")
        print(f"{'='*60}")
        
        docs = await vector_store.search(q, k=5)  # Увеличиваем k до 5
        
        for i, doc in enumerate(docs, 1):
            print(f"\n📄 Чанк {i} (score: {doc['score']:.4f})")
            print(f"   Источник: {doc['source']}")
            print(f"   Раздел: {doc['header']}")
            print(f"   Текст: {doc['text'][:200]}...")  # Первые 200 символов

asyncio.run(debug_search())
