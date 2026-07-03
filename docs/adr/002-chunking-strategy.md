# ADR 002: Chunking Strategy

## Context
When ingesting documents, we must split the text into manageable chunks before embedding. Options include:
1. Fixed-size chunking (e.g., 512 tokens with 50-token overlap).
2. Sentence-boundary chunking (splitting exactly on sentences or paragraphs).
3. Semantic chunking (using an LLM or ML model to split based on topical shifts).

## Decision
We will use a **hybrid chunking strategy**: starting with **Sentence-boundary chunking** grouped up to a maximum token limit (e.g., 512 tokens) as the default. We will switch to **Semantic chunking** for dense, unstructured documents (like conversational transcripts or complex research papers) where fixed boundaries destroy context.

## Consequences
- **Positive:** Sentence-boundary ensures that chunks rarely cut off mid-thought, preserving better context than naive fixed-size chunking.
- **Positive:** Improves retrieval accuracy by keeping semantic units intact.
- **Negative:** Semantic chunking is computationally more expensive and slower to process during ingestion.
- **Negative:** Managing multiple chunking strategies adds complexity to the Ingestion Subsystem and pipeline configurations.
