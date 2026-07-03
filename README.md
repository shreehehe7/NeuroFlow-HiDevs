# NeuroFlow

NeuroFlow is an advanced, multi-modal Retrieval-Augmented Generation (RAG) system with integrated continuous evaluation and fine-tuning capabilities.

## Subsystems
- **Ingestion**: Multi-modal file processing and vector embedding.
- **Retrieval**: Parallel hybrid search with Reciprocal Rank Fusion and Cross-Encoder Reranking.
- **Generation**: Dynamic model routing and streaming responses.
- **Evaluation**: Asynchronous LLM-as-a-judge scoring on RAG metrics.
- **Fine-Tuning**: Automated extraction of high-quality examples for continuous model improvement.

See `docs/architecture.md` and `docs/api-contracts.md` for more details.
