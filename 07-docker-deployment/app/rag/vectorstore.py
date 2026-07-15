import faiss
import numpy as np
import json
import os
import re
from collections import Counter
from app.rag.embeddings import get_embeddings

RAG_DATA_DIR = "/content/drive/MyDrive/faq-assistant-project/06-backups/stage_4_rag_data"

class FAQVectorStore:
    def __init__(self, dim: int = 768):
        self.dim = dim
        self.index_path = os.path.join(RAG_DATA_DIR, "faq.index")
        self.meta_path = os.path.join(RAG_DATA_DIR, "faq_meta.json")
        
        os.makedirs(RAG_DATA_DIR, exist_ok=True)
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
            print(f"✅ Loaded index with {self.index.ntotal} vectors from Drive.")
        else:
            self.index = faiss.IndexFlatIP(dim)
            self.meta = []
            print("🆕 Initialized empty FAISS index.")

    async def add_chunks(self, chunks: list[dict]):
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        print(f"⏳ Embedding {len(texts)} chunks...")
        vectors = await get_embeddings(texts)
        
        faiss.normalize_L2(vectors)
        
        self.index.add(vectors)
        self.meta.extend(chunks)
        
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved index to Drive. Total vectors: {self.index.ntotal}")

    def _tokenize(self, text: str) -> list[str]:
        """Простая токенизация для keyword search."""
        text = text.lower()
        tokens = re.findall(r'[а-яёa-z0-9]+', text)
        stop_words = {'как', 'что', 'где', 'когда', 'кто', 'почему', 'зачем', 'от', 'до', 'в', 'на', 'с', 'по', 'для', 'и', 'или', 'но', 'а'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def _bm25_score(self, query_tokens: list[str], doc_text: str, doc_len_avg: float) -> float:
        """BM25-подобный scoring."""
        doc_tokens = self._tokenize(doc_text)
        doc_len = len(doc_tokens)
        
        term_freq = Counter(doc_tokens)
        
        score = 0.0
        k1 = 1.5
        b = 0.75
        
        for token in query_tokens:
            if token in term_freq:
                tf = term_freq[token]
                norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / doc_len_avg))
                score += norm_tf
        
        return score

    async def search(self, query: str, k: int = 8) -> list[dict]:
        """Гибридный поиск: FAISS + BM25."""
        if self.index.ntotal == 0:
            return []
        
        # 1. FAISS поиск
        q_vec = await get_embeddings([query])
        faiss.normalize_L2(q_vec)
        
        faiss_scores, faiss_indices = self.index.search(q_vec, min(15, self.index.ntotal))
        
        faiss_results = []
        for score, idx in zip(faiss_scores[0], faiss_indices[0]):
            if idx == -1:
                continue
            chunk_data = self.meta[idx]
            faiss_results.append({
                "score": float(score),
                "text": chunk_data["text"],
                "source": chunk_data["source"],
                "header": chunk_data.get("header", "Unknown"),
                "idx": idx
            })
        
        # 2. BM25 поиск
        query_tokens = self._tokenize(query)
        
        doc_lens = [len(self._tokenize(m["text"])) for m in self.meta]
        doc_len_avg = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
        
        keyword_results = []
        for idx, meta in enumerate(self.meta):
            bm25_score = self._bm25_score(query_tokens, meta["text"], doc_len_avg)
            if bm25_score > 0:
                keyword_results.append({
                    "score": bm25_score,
                    "text": meta["text"],
                    "source": meta["source"],
                    "header": meta.get("header", "Unknown"),
                    "idx": idx
                })
        
        keyword_results.sort(key=lambda x: x["score"], reverse=True)
        
        # 3. Объединяем с весами FAISS 0.4, BM25 0.6
        combined = {}
        
        if faiss_results:
            max_faiss = max(r["score"] for r in faiss_results)
            min_faiss = min(r["score"] for r in faiss_results)
            faiss_range = max_faiss - min_faiss if max_faiss != min_faiss else 1.0
            
            for res in faiss_results:
                normalized = (res["score"] - min_faiss) / faiss_range
                combined[res["idx"]] = {
                    "score": normalized * 0.4,
                    "text": res["text"],
                    "source": res["source"],
                    "header": res["header"]
                }
        
        if keyword_results:
            max_kw_score = keyword_results[0]["score"] if keyword_results else 1.0
            for res in keyword_results[:15]:
                normalized_score = res["score"] / max_kw_score if max_kw_score > 0 else 0
                if res["idx"] in combined:
                    combined[res["idx"]]["score"] += normalized_score * 0.6
                else:
                    combined[res["idx"]] = {
                        "score": normalized_score * 0.6,
                        "text": res["text"],
                        "source": res["source"],
                        "header": res["header"]
                    }
        
        # Сортируем и возвращаем топ-k
        final_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        
        return final_results[:k]

vector_store = FAQVectorStore()
