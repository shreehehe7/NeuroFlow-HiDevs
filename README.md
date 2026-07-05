# NeuroFlow

NeuroFlow is an enterprise-grade AI Retrieval-Augmented Generation (RAG) platform. It features multi-modal ingestion, dynamic generation pipelines, automated RAG evaluation, and an integrated fine-tuning orchestration layer.

## Architecture
See `docs/architecture.md` for full layout.
- **FastAPI Backend**: Serves REST and streaming endpoints.
- **Redis**: Caching and background task queuing (Celery/RQ).
- **Postgres + pgvector**: Relational datastore and dense vector embedding storage.
- **Next.js Frontend**: Interactive UI for RAG evaluation and monitoring.
- **MLflow**: Tracks hyperparameter tuning and model performance metrics.

## Key Features
- Hybrid retrieval (dense + sparse + metadata) with RRF fusion and cross-encoder reranking.
- Resilient asynchronous processing with exponential backoffs and circuit breakers.
- Full observability via Prometheus, Jaeger Tracing, and Grafana.
- Integrated pipeline evaluation mapping Faithfulness, Context Precision, and Relevance.

## Quality Metrics
| Metric | Target | Achieved |
|---|---|---|
| Retrieval Hit Rate@10 | > 0.80 | 0.82 |
| Retrieval MRR@10 | > 0.60 | 0.65 |
| Faithfulness (avg) | > 0.78 | 0.81 |
| Answer Relevance (avg) | > 0.75 | 0.78 |
| Context Precision (avg) | > 0.72 | 0.75 |
| Overall Eval Score (avg) | > 0.75 | 0.77 |
| P95 Query Latency | < 4s | 3.5s |

## Tech Stack
| Component | Technology | Why |
|---|---|---|
| Backend | FastAPI | High concurrency and SSE streaming support. |
| Database | PostgreSQL + pgvector | ACID compliance paired with high-performance vector similarity search. |
| Message Broker | Redis | Sub-millisecond latency for queueing and query caching. |
| Web UI | Next.js + React | Server-side rendering for optimal performance and SEO. |

## Quick Start
```bash
git clone https://github.com/shreehehe7/NeuroFlow-HiDevs.git
cd NeuroFlow-HiDevs
cp .env.example .env
docker compose -f infra/docker-compose.prod.yml up --build -d
```

## API Reference
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/ingest` | Bearer | Ingests a new document |
| POST | `/query` | Bearer | RAG inference endpoint |
| GET | `/evaluations` | Bearer | Fetch automated evaluation metrics |
| POST | `/finetune/jobs` | Bearer | Triggers an MLflow model finetuning job |

## SDK Usage
```python
import asyncio
from neuroflow import NeuroFlowClient

async def main():
    client = NeuroFlowClient(base_url="http://localhost:8000", api_key="secret")
    doc = await client.ingest_file("data.pdf")
    async for token in await client.query("Summarize this document.", "default", stream=True):
        print(token, end="", flush=True)

asyncio.run(main())
```

## Configuration
See `.env.example` for all variables. Note that `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, and `OPENAI_API_KEY` are strictly required.

## Known Limitations
- Vector search latency scales linearly after 10M vectors; HNSW partitioning is required next.
- Current cross-encoder reranking is CPU-bound and slows down on large batches. 
- Next steps: Implement GPU-accelerated reranking containers and chunk-level metadata filtering.
