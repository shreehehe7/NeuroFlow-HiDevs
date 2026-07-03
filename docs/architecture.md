# NeuroFlow System Architecture

This document describes the design and data flow of the five core subsystems of NeuroFlow.

## 1. Ingestion Subsystem
**Purpose:** Accepts raw files (PDF, DOCX, images, CSV, web URLs), extracts content per modality, chunks, embeds, and writes to the vector store.

**Data Flow:**
1. **Input:** File uploaded via API or URL provided.
2. **Parsing & Extraction:** 
   - PDF/DOCX: Text extraction and OCR for images.
   - Images: Vision model extraction / captioning.
   - CSV: Structured data conversion.
   - Web URLs: Scraping and HTML parsing.
3. **Chunking:** Extracted text is split into chunks (e.g., semantic or fixed-size based on the chunking strategy).
4. **Embedding:** Chunks are passed to an embedding model (e.g., OpenAI `text-embedding-3-small` or local model).
5. **Storage:** The vectors and metadata (source, timestamp, chunk index) are written to the Vector Store (pgvector).
6. **Output:** First queryable vector available in the database.

*Diagram conceptually:* File -> Extractor -> Chunker -> Embedder -> Vector Store.

## 2. Retrieval Subsystem
**Purpose:** Given a user query, runs embedding similarity search, keyword search, and metadata filtering in parallel, fuses results, reranks, and returns a context window.

**Data Flow:**
1. **Input:** User query (text).
2. **Query Processing:** 
   - Generates embedding for the query.
   - Extracts keywords and metadata filters.
3. **Parallel Search:**
   - **Dense Search (Vector):** Embedding similarity search in pgvector.
   - **Sparse Search (Keyword):** BM25 or full-text search in PostgreSQL.
   - **Filtering:** Metadata filtering applied to both.
4. **Fusion:** Combines results using Reciprocal Rank Fusion (RRF).
5. **Reranking:** Passes fused top-K results through a cross-encoder reranker (e.g., Cohere Rerank or BGE-Reranker) to score relevance.
6. **Output:** Ranked context window passed to Generation Subsystem.

## 3. Generation Subsystem
**Purpose:** Assembles the context window into a prompt, routes to the appropriate LLM, streams the response, and logs for evaluation.

**Data Flow:**
1. **Input:** User query + Ranked context window.
2. **Prompt Assembly:** Formats the system prompt, retrieved context, and user query.
3. **Routing:** Selects the optimal LLM (by cost tier, capability, latency, or domain) based on query complexity.
4. **Generation:** Sends prompt to the selected LLM.
5. **Streaming:** Streams the response token by token back to the client via Server-Sent Events (SSE).
6. **Logging:** Once generation is complete, asynchronously logs the full input (prompt, context) and output (completion) to the Evaluation Subsystem.

## 4. Evaluation Subsystem
**Purpose:** Asynchronously scores every generation on faithfulness, answer relevance, context precision, and context recall. Stores scores in Postgres and computes rolling aggregates.

**Data Flow:**
1. **Input:** Logged input/output pair (query, context, generated answer).
2. **LLM-as-a-Judge Evaluation:**
   - **Faithfulness:** Are claims grounded in the context?
   - **Answer Relevance:** Does it address the user's question?
   - **Context Precision:** Are retrieved chunks actually used?
   - **Context Recall:** Were relevant chunks retrieved?
3. **Storage:** Saves the scores to Postgres.
4. **Aggregation:** Computes rolling aggregates (e.g., hourly/daily averages).
5. **Output:** Quality metrics available for dashboards.

## 5. Fine-Tuning Subsystem
**Purpose:** Extracts high-quality prompt/completion pairs, formats as training data, submits jobs, tracks experiments, and updates routing.

**Data Flow:**
1. **Extraction:** Queries the evaluation log for pairs where Faithfulness > 0.8 AND User Rating >= 4.
2. **Formatting:** Converts extracted data into JSONL format suitable for fine-tuning.
3. **Execution:** Submits fine-tuning jobs (e.g., via OpenAI API or local infrastructure).
4. **Tracking:** Logs experiments and metrics in MLflow.
5. **Deployment:** When the fine-tuned model outperforms the base model on validation sets, updates the Generation Subsystem's routing matrix to send similar queries to the new model.
