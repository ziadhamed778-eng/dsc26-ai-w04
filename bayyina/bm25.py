import math
from bayyina.types import Chunk
from bayyina.normalize import tokenize

class BM25Index:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.N = 0
        self.avgdl = 0.0
        self.doc_len = {}  # chunk_id -> طول الفقرة بالكلمات
        self.df = {}       # term -> عدد الفقرات التي تحتوي على الكلمة
        self.tf = {}       # chunk_id -> {term -> تكرار الكلمة في هذه الفقرة}

    def add(self, chunks: list[Chunk]) -> None:
        self.N = len(chunks)
        if self.N == 0:
            self.avgdl = 0.0
            return

        total_dl = 0
        for chunk in chunks:
            tokens = tokenize(chunk.text)
            dl = len(tokens)
            self.doc_len[chunk.chunk_id] = dl
            total_dl += dl
            
            # حساب تكرار الكلمات في الفقرة الواحدة (Term Frequency)
            term_counts = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1
            
            self.tf[chunk.chunk_id] = term_counts
            
            # حساب عدد الفقرات اللي ظهرت فيها الكلمة (Document Frequency)
            for term in term_counts:
                self.df[term] = self.df.get(term, 0) + 1
                
        self.avgdl = total_dl / self.N

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        if self.N == 0:
            return []
            
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
            
        # كل كلمة في السؤال بتتحسب مرة واحدة بس
        query_terms = set(query_tokens)
        
        scores = {}
        for term in query_terms:
            if term not in self.df:
                continue
                
            # حساب الـ Inverse Document Frequency (IDF)
            df = self.df[term]
            idf = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))
            
            # حساب الـ Score لكل فقرة تحتوي على الكلمة
            for chunk_id, term_counts in self.tf.items():
                if term in term_counts:
                    tf = term_counts[term]
                    dl = self.doc_len[chunk_id]
                    
                    # معادلة BM25
                    score = idf * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
                    scores[chunk_id] = scores.get(chunk_id, 0.0) + score
                    
        # تصفية النتائج (الـ Score لازم يكون أكبر من صفر)
        results = [(cid, score) for cid, score in scores.items() if score > 0]
        
        # ترتيب النتائج: الـ Score من الكبير للصغير، ولو تساووا نرتب بالـ chunk_id أبجدياً
        results.sort(key=lambda x: (-x[1], x[0]))
        
        return results[:top_k]