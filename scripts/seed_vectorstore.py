import sys
import asyncio
import nest_asyncio
import os
nest_asyncio.apply()

sys.path.insert(0, '/content')

from app.rag.chunker import markdown_chunker
from app.rag.vectorstore import vector_store

async def main():
    all_chunks = []
    
    # Читаем твои markdown файлы из knowledge_base
    kb_path = '/content/app/knowledge_base'
    if not os.path.exists(kb_path):
        print(f"❌ Папка {kb_path} не найдена!")
        return
        
    for fname in os.listdir(kb_path):
        if fname.endswith('.md'):
            with open(os.path.join(kb_path, fname), encoding="utf-8") as f:
                content = f.read()
            chunks = markdown_chunker(content, source=fname)
            all_chunks.extend(chunks)
            print(f"📄 {fname}: {len(chunks)} chunks")
            
    print(f"\n📚 Total: {len(all_chunks)} semantic chunks.")
    await vector_store.add_chunks(all_chunks)

asyncio.run(main())
