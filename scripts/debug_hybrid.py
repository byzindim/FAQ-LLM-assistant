import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.rag.vectorstore import vector_store

async def debug_hybrid():
    questions = [
        "Как сбросить пароль от почты?",
        "Когда выплачиваются премии?"
    ]
    
    for q in questions:
        print(f"\n{'='*80}")
        print(f"❓ Вопрос: {q}")
        print(f"{'='*80}")
        
        # Вызываем новый search с гибридным поиском
        docs = await vector_store.search(q, k=5)
        
        print(f"\n📚 Найденные чанки ({len(docs)}):")
        for i, doc in enumerate(docs, 1):
            print(f"\n  Чанк {i} (score: {doc['score']:.4f}):")
            print(f"  Источник: {doc['source']}")
            print(f"  Раздел: {doc['header']}")
            print(f"  Текст: {doc['text'][:150]}...")

asyncio.run(debug_hybrid())
