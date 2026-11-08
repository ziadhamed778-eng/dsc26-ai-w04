import numpy as np
from bayyina.types import Chunk, Hit, Embedder, Reranker
from bayyina.bm25 import BM25Index

def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores = {}
    for ranking in rankings:
        # الترتيب بيبدأ من 1 بناءً على التعليمات
        for rank, chunk_id in enumerate(ranking, 1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            
    # ترتيب النتائج: الـ Score من الكبير للصغير، ولو تساووا نرتب بالـ chunk_id أبجدياً
    results = list(scores.items())
    results.sort(key=lambda x: (-x[1], x[0]))
    return results

class HybridRetriever:
    def __init__(self, chunks: list[Chunk], embedder: Embedder, *, k1: float = 1.5,
                 b: float = 0.75, reranker: Reranker | None = None):
        self.chunks_dict = {c.chunk_id: c for c in chunks}
        self.embedder = embedder
        self.reranker = reranker
        
        # 1. تجهيز BM25
        self.bm25 = BM25Index(k1=k1, b=b)
        self.bm25.add(chunks)
        
        self.chunk_ids = [c.chunk_id for c in chunks]
        
        # 2. تجهيز الـ Embeddings
        # تمرير كل النصوص كـ قائمة (List) دفعة واحدة ليتم معالجتها كـ Batch سليم
        if chunks:
            self.chunk_embeddings = self.embedder.embed([c.text for c in chunks])
        else:
            self.chunk_embeddings = np.array([])

    def search(self, query: str, top_k: int = 5, candidates: int = 50) -> list[Hit]:
        if not query.strip() or not self.chunk_ids:
            return []
            
        # 1. البحث باستخدام BM25
        bm25_results = self.bm25.search(query, top_k=candidates)
        bm25_ranking = [chunk_id for chunk_id, _ in bm25_results]
        
        # 2. البحث بالمعنى (Dense Search)
        # تمرير السؤال داخل قائمة [query] واستخراج النتيجة الأولى [0]
        query_emb = self.embedder.embed([query])[0]
        
        # الضرب الاتجاهي مباشرة لأن الأبعاد أصبحت صحيحة (N, 512) مع (512,)
        dot_products = np.dot(self.chunk_embeddings, query_emb)
        
        # دمج الـ IDs مع الـ Scores وترتيبها
        dense_scored = [(self.chunk_ids[i], float(dot_products[i])) for i in range(len(self.chunk_ids))]
        dense_scored.sort(key=lambda x: (-x[1], x[0]))
        dense_ranking = [chunk_id for chunk_id, _ in dense_scored[:candidates]]
            
        # 3. دمج النتائج باستخدام RRF
        fused_results = rrf([bm25_ranking, dense_ranking], k=60)
        fused_candidates = fused_results[:candidates]
        
        # 4. بناء الـ Hits بناءً على النتائج المدمجة
        hits = []
        for chunk_id, score in fused_candidates:
            chunk = self.chunks_dict[chunk_id]
            hits.append(Hit(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                start=chunk.start,
                end=chunk.end,
                text=chunk.text,
                score=score
            ))
            
        # 5. إعادة الترتيب (Reranking) لو متاح
        if self.reranker is not None and hits:
            rerank_scores = self.reranker(query, hits)
            for hit, new_score in zip(hits, rerank_scores):
                hit.score = new_score
            hits.sort(key=lambda h: (-h.score, h.chunk_id))
            
        return hits[:top_k]