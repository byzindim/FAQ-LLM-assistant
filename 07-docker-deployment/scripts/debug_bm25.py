import sys
import re
from collections import Counter

sys.path.insert(0, '/content')

from app.rag.vectorstore import vector_store

def debug_bm25():
    # Тестовый запрос
    query = "Как сбросить пароль от почты?"
    
    # 1. Токенизация запроса
    query_tokens = re.findall(r'[а-яёa-z0-9]+', query.lower())
    print(f"🔤 Токены запроса: {query_tokens}\n")
    
    # 2. Проверяем правильные чанки
    correct_indices = [0, 26]  # "Доступ к почте" и "Премии"
    
    for idx in correct_indices:
        meta = vector_store.meta[idx]
        print(f"{'='*80}")
        print(f"📄 Чанк {idx}: {meta['header']}")
        print(f"{'='*80}")
        
        # Токенизация документа
        doc_tokens = re.findall(r'[а-яёa-z0-9]+', meta['text'].lower())
        print(f"🔤 Токены документа (первые 20): {doc_tokens[:20]}")
        
        # Проверяем, есть ли токены запроса в документе
        matching_tokens = [t for t in query_tokens if t in doc_tokens]
        print(f"✅ Совпадающие токены: {matching_tokens}")
        
        # Считаем BM25 score
        term_freq = Counter(doc_tokens)
        doc_len = len(doc_tokens)
        
        # Средняя длина документа
        all_doc_lens = [len(re.findall(r'[а-яёa-z0-9]+', m['text'].lower())) for m in vector_store.meta]
        doc_len_avg = sum(all_doc_lens) / len(all_doc_lens)
        
        k1 = 1.5
        b = 0.75
        bm25_score = 0.0
        
        for token in query_tokens:
            if token in term_freq:
                tf = term_freq[token]
                norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / doc_len_avg))
                bm25_score += norm_tf
                print(f"   Токен '{token}': tf={tf}, norm_tf={norm_tf:.4f}")
        
        print(f"\n📊 Итоговый BM25 score: {bm25_score:.4f}")
        print()

debug_bm25()
