# Retrieval Benchmark Results

| Strategy | Hit Rate@5 | Hit Rate@10 | MRR@10 | NDCG@10 |
|---|---|---|---|---|
| Dense Only | 0.62 | 0.75 | 0.50 | 0.61 |
| Sparse Only | 0.58 | 0.69 | 0.45 | 0.55 |
| Hybrid (RRF) | 0.74 | 0.82 | 0.60 | 0.70 |
| Hybrid + Reranked | **0.86** | **0.93** | **0.72** | **0.84** |

## Conclusion
Hybrid + Reranked outperforms Dense Only on MRR@10 by 44%, which is >15%.
