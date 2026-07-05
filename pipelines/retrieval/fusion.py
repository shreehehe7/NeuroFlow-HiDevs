from typing import List
from . import RetrievalResult

def reciprocal_rank_fusion(
    result_lists: List[List[RetrievalResult]],
    k: int = 60
) -> List[RetrievalResult]:
    scores = {}
    items = {}
    
    for result_list in result_lists:
        for rank, result in enumerate(result_list):
            chunk_id = result.chunk_id
            if chunk_id not in items:
                items[chunk_id] = result
                scores[chunk_id] = 0.0
            scores[chunk_id] += 1.0 / (k + rank + 1)
            
    fused_results = []
    for chunk_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        result = items[chunk_id]
        result.score = score
        fused_results.append(result)
        
    return fused_results
