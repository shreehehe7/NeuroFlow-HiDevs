# ADR 001: Choice of Vector Store

## Context
NeuroFlow requires a vector database to store document embeddings and perform efficient similarity search alongside metadata filtering. We considered dedicated vector databases like Pinecone, Weaviate, and Qdrant, as well as PostgreSQL with the pgvector extension. The system also requires storing structured relational data (evaluations, fine-tuning jobs, metadata).

## Decision
We will use **PostgreSQL with the pgvector extension** as our primary vector store.

## Consequences
- **Positive:** Reduces architectural complexity by using a single database for both relational data (users, evaluations, pipeline configs) and vector data.
- **Positive:** Enables ACID transactions across metadata and vectors, and allows complex JOINs (e.g., joining chunks with evaluation scores directly).
- **Positive:** Lower operational overhead and cost compared to managed services like Pinecone.
- **Negative:** May require manual tuning of indexes (HNSW or IVFFlat) as the dataset scales to hundreds of millions of vectors.
- **Negative:** Compute and memory are shared with relational queries, potentially impacting performance under high concurrent load unless scaled vertically.
