# Retrospective

## Hardest Technical Challenge
The most technically complex challenge was balancing streaming generation with real-time evaluation instrumentation. Hooking up asynchronous server-sent events (SSE) while simultaneously capturing generation traces, chunk relevance, and LLM payloads to queue background MLflow evaluations required strict state management and robust error boundaries. Implementing the async background worker pools using Redis without creating race conditions during streaming responses taught me a lot about distributed event loops.

## Design Hindsight
Looking back at the Architecture Decision Records, I would likely reconsider relying strictly on PostgreSQL + pgvector as the solitary datastore for all environments. While pgvector simplifies operations tremendously by removing the need for a standalone vector DB like Pinecone or Qdrant, we experienced high I/O bottlenecks when simultaneous bulk ingestions were updating embeddings alongside active RAG query reads. Sharding or decoupling the vector store entirely from relational state would be safer at a higher scale.

## Lessons Learned in Production AI
Tutorials often teach you how to stitch an LLM to a vector database, but they gloss over resilience. Production AI engineering is about handling failure gracefully: LLM providers go down, API rate limits are hit constantly, and vector search often returns completely irrelevant data. Implementing circuit breakers, exponential backoffs, and strict threshold fallbacks taught me that building robust AI systems is actually 80% traditional systems engineering and 20% prompt tuning.

## The Metric Improvement Sprint
Task 48's performance tuning sprint was an eye-opener. I initially assumed that switching to a more advanced LLM would yield the highest quality boost. However, tuning the retrieval mechanisms—specifically combining sparse keyword search with dense semantic search (Hybrid RRF) and tweaking the chunk sizes—had a significantly larger impact on our end evaluation metrics. It validated the theory that an LLM is only as intelligent as the context you retrieve for it.
