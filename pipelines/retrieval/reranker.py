import asyncio
from typing import List
from sentence_transformers import CrossEncoder
from . import RetrievalResult

class Reranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    async def rerank(self, query: str, candidates: List[RetrievalResult]) -> List[RetrievalResult]:
        if not candidates:
            return []
            
        pairs = [(query, chunk.content) for chunk in candidates]
        scores = self.model.predict(pairs)
        
        for idx, score in enumerate(scores):
            candidates[idx].score = float(score)
            
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates
