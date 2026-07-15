import sys
sys.path.insert(0, '/content')

from app.rag.chunker import markdown_chunker

# Читаем hr.md
with open('/content/app/knowledge_base/hr.md', 'r', encoding='utf-8') as f:
    content = f.read()

chunks = markdown_chunker(content, source='hr.md')

print(f"📊 Всего чанков: {len(chunks)}\n")

for i, chunk in enumerate(chunks, 1):
    print(f"📄 Чанк {i}:")
    print(f"   Заголовок: {chunk['header']}")
    print(f"   Текст: {chunk['text'][:150]}...")
    print()
