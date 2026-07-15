import sys
import asyncio
import nest_asyncio
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.rag.vectorstore import vector_store

async def debug_k5():
    # Проблемные вопросы
    questions = [
        "Как сбросить пароль от почты?",
        "Когда выплачиваются премии?"
    ]
    
    for q in questions:
        print(f"\n{'='*80}")
        print(f"❓ Вопрос: {q}")
        print(f"{'='*80}")
        
        # Ищем с k=5
        docs = await vector_store.search(q, k=5)
        
        print(f"\n📚 Найденные чанки ({len(docs)}):")
        for i, doc in enumerate(docs, 1):
            print(f"\n  Чанк {i} (score: {doc['score']:.4f}):")
            print(f"  Источник: {doc['source']}")
            print(f"  Раздел: {doc['header']}")
            print(f"  Текст: {doc['text'][:150]}...")
        
        # Проверяем, есть ли в индексе правильные чанки
        print(f"\n🔍 Проверяем, есть ли правильные чанки в индексе...")
        
        # Для вопроса про сброс пароля ищем "Сброс пароля"
        if "пароль" in q.lower():
            for idx, meta in enumerate(vector_store.meta):
                if "пароль" in meta['text'].lower() or "пароль" in meta.get('header', '').lower():
                    print(f"\n  ✅ Найден чанк с 'пароль' в индексе:")
                    print(f"     Индекс: {idx}")
                    print(f"     Заголовок: {meta['header']}")
                    print(f"     Текст: {meta['text'][:150]}...")
        
        # Для вопроса про премии ищем "преми"
        if "прем" in q.lower():
            for idx, meta in enumerate(vector_store.meta):
                if "прем" in meta['text'].lower() or "прем" in meta.get('header', '').lower():
                    print(f"\n  ✅ Найден чанк с 'преми' в индексе:")
                    print(f"     Индекс: {idx}")
                    print(f"     Заголовок: {meta['header']}")
                    print(f"     Текст: {meta['text'][:150]}...")

asyncio.run(debug_k5())
