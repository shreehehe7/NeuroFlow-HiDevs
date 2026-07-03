# Data Models

This document outlines the core data models for NeuroFlow, focusing on the relational entities and vector representations stored in PostgreSQL (with pgvector).

## 1. Document Model
Represents a source file or URL ingested into the system.

- `id`: UUID (Primary Key)
- `source_type`: Enum (`file`, `url`)
- `source_uri`: String (URL or local/S3 path)
- `metadata`: JSONB (e.g., author, domain, original filename)
- `status`: Enum (`processing`, `completed`, `failed`)
- `created_at`: Timestamp
- `updated_at`: Timestamp

## 2. Chunk Model (Vector Store)
Represents a text chunk extracted from a Document, along with its embedding.

- `id`: UUID (Primary Key)
- `document_id`: UUID (Foreign Key -> Document.id)
- `chunk_index`: Integer (Order of the chunk in the document)
- `text_content`: Text (The raw extracted text)
- `embedding`: Vector (pgvector type, dimensional size based on the chosen model)
- `metadata`: JSONB (Chunk-specific metadata, e.g., page number, section header)

## 3. Query Log Model
Records user queries and the generated responses for evaluation and tracing.

- `id`: UUID (Primary Key)
- `user_id`: UUID (Optional, Foreign Key)
- `query_text`: Text
- `generated_answer`: Text
- `context_used`: JSONB (Array of Chunk IDs and their retrieval scores)
- `model_used`: String (e.g., "gpt-4o-mini")
- `latency_ms`: Integer
- `created_at`: Timestamp

## 4. Evaluation Score Model
Stores the automated LLM-as-a-judge metrics for a specific Query Log.

- `id`: UUID (Primary Key)
- `query_id`: UUID (Foreign Key -> QueryLog.id)
- `faithfulness`: Float (0.0 to 1.0)
- `answer_relevance`: Float (0.0 to 1.0)
- `context_precision`: Float (0.0 to 1.0)
- `context_recall`: Float (0.0 to 1.0)
- `user_rating`: Integer (Optional, 1 to 5, provided by the end user)
- `evaluated_at`: Timestamp

## 5. Pipeline Configuration Model
Stores named configurations for RAG pipelines.

- `id`: UUID (Primary Key)
- `name`: String (Unique)
- `chunk_size`: Integer
- `chunk_overlap`: Integer
- `embed_model`: String
- `llm_model`: String
- `system_prompt`: Text
- `created_at`: Timestamp

## 6. Fine-Tuning Job Model
Tracks the status and metrics of models trained on evaluation logs.

- `id`: UUID (Primary Key)
- `base_model`: String
- `dataset_size`: Integer
- `status`: Enum (`queued`, `training`, `completed`, `failed`)
- `metrics`: JSONB (e.g., {"loss": 0.12})
- `fine_tuned_model_id`: String (Provider ID of the resulting model)
- `created_at`: Timestamp
- `completed_at`: Timestamp
