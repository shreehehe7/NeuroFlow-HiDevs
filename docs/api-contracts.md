# API Contracts

## 1. POST /ingest — File/URL Ingestion
**Path:** `/ingest`
**Method:** `POST`
**Request Body:**
```json
{
  "source_type": "file|url",
  "url": "https://example.com" (optional),
  "file_id": "string" (optional, if file uploaded via multipart previously or directly sent),
  "metadata": {
    "author": "string",
    "domain": "string"
  }
}
```
*(Alternatively, handled via multipart/form-data for actual file uploads)*
**Response Body:**
```json
{
  "document_id": "uuid",
  "status": "processing",
  "chunks_created": 0
}
```
**Error Codes:**
- `400 Bad Request`: Invalid file format or missing URL.
- `413 Payload Too Large`: File exceeds size limit.
**Auth Requirement:** Bearer Token (JWT).
**Rate Limit:** 10 requests per minute.

## 2. POST /query — RAG Query Execution
**Path:** `/query`
**Method:** `POST`
**Request Body:**
```json
{
  "query": "string",
  "filters": {
    "domain": "string"
  }
}
```
**Response Body:**
```json
{
  "query_id": "uuid",
  "answer": "string",
  "context_used": [
    {
      "chunk_id": "uuid",
      "text": "string",
      "score": 0.95
    }
  ]
}
```
*(If standard synchronous request. If streamed, see below).*
**Error Codes:**
- `400 Bad Request`: Query string empty.
**Auth Requirement:** Bearer Token (JWT).
**Rate Limit:** 60 requests per minute.

## 3. GET /query/{query_id}/stream — SSE Stream for Generation
**Path:** `/query/{query_id}/stream`
**Method:** `GET`
**Request Body:** None
**Response Body:** `text/event-stream`
```text
data: {"token": "Hello"}
data: {"token": " world"}
data: {"[DONE]"}
```
**Error Codes:**
- `404 Not Found`: Query ID does not exist or expired.
**Auth Requirement:** Bearer Token (JWT).
**Rate Limit:** 60 requests per minute.

## 4. GET /evaluations — Paginated Evaluation Results
**Path:** `/evaluations`
**Method:** `GET`
**Request Body:** None (Query params: `page`, `limit`)
**Response Body:**
```json
{
  "data": [
    {
      "eval_id": "uuid",
      "query_id": "uuid",
      "faithfulness": 0.9,
      "answer_relevance": 0.85,
      "context_precision": 0.8,
      "context_recall": 0.9
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10
}
```
**Error Codes:**
- `400 Bad Request`: Invalid pagination parameters.
**Auth Requirement:** Admin Bearer Token (JWT).
**Rate Limit:** 100 requests per minute.

## 5. GET /evaluations/aggregate — Rolling Quality Metrics
**Path:** `/evaluations/aggregate`
**Method:** `GET`
**Request Body:** None (Query params: `timeframe=1h|24h|7d`)
**Response Body:**
```json
{
  "timeframe": "24h",
  "average_faithfulness": 0.91,
  "average_answer_relevance": 0.88,
  "total_queries": 1500
}
```
**Error Codes:** None standard.
**Auth Requirement:** Admin Bearer Token.
**Rate Limit:** 30 requests per minute.

## 6. POST /pipelines — Create Named Pipeline Configuration
**Path:** `/pipelines`
**Method:** `POST`
**Request Body:**
```json
{
  "name": "string",
  "config": {
    "chunk_size": 512,
    "embed_model": "text-embedding-3-small",
    "llm_model": "gpt-4o-mini"
  }
}
```
**Response Body:**
```json
{
  "pipeline_id": "uuid",
  "name": "string",
  "created_at": "timestamp"
}
```
**Error Codes:**
- `400 Bad Request`: Invalid config parameters.
**Auth Requirement:** Admin Bearer Token.
**Rate Limit:** 10 requests per minute.

## 7. GET /pipelines/{id}/runs — Pipeline Execution History
**Path:** `/pipelines/{id}/runs`
**Method:** `GET`
**Request Body:** None
**Response Body:**
```json
{
  "pipeline_id": "uuid",
  "runs": [
    {
      "run_id": "uuid",
      "status": "success|failed",
      "duration_ms": 1200,
      "timestamp": "iso-date"
    }
  ]
}
```
**Error Codes:**
- `404 Not Found`: Pipeline ID not found.
**Auth Requirement:** Admin Bearer Token.
**Rate Limit:** 60 requests per minute.

## 8. POST /finetune/jobs — Submit Fine-Tuning Job
**Path:** `/finetune/jobs`
**Method:** `POST`
**Request Body:**
```json
{
  "dataset_filters": {
    "min_faithfulness": 0.8,
    "min_user_rating": 4
  },
  "base_model": "llama-3-8b",
  "hyperparameters": {
    "epochs": 3
  }
}
```
**Response Body:**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "dataset_size": 1500
}
```
**Error Codes:**
- `400 Bad Request`: Insufficient data matching filters.
**Auth Requirement:** Admin Bearer Token.
**Rate Limit:** 5 requests per day.

## 9. GET /finetune/jobs/{id} — Job Status and Metrics
**Path:** `/finetune/jobs/{id}`
**Method:** `GET`
**Request Body:** None
**Response Body:**
```json
{
  "job_id": "uuid",
  "status": "training|completed|failed",
  "metrics": {
    "loss": 0.12
  }
}
```
**Error Codes:**
- `404 Not Found`: Job ID not found.
**Auth Requirement:** Admin Bearer Token.
**Rate Limit:** 60 requests per minute.

## 10. GET /health and GET /metrics
**Path:** `/health`
**Method:** `GET`
**Response Body:**
```json
{
  "status": "ok",
  "db_connected": true,
  "vector_db_connected": true
}
```
**Auth Requirement:** None.

**Path:** `/metrics`
**Method:** `GET`
**Response Body:** Prometheus metrics text format.
**Auth Requirement:** Internal Network / IP Whitelist.
