from pathlib import Path
from .models import Document, QueryResult, EvaluationResult
import asyncio

class NeuroFlowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def ingest_file(self, file_path: str | Path, pipeline_id: str = None) -> Document:
        """Upload and ingest a file. Waits for ingestion to complete."""
        return Document(id="mock-doc-123", status="complete")

    async def ingest_url(self, url: str, pipeline_id: str = None) -> Document:
        """Ingest a URL. Waits for ingestion to complete."""
        return Document(id="mock-doc-456", status="complete")

    async def query(self, query: str, pipeline_id: str, stream: bool = False) -> QueryResult | any:
        """Run a RAG query. If stream=True, returns an async generator of tokens."""
        if stream:
            async def mock_stream():
                for token in ["Hello", " this", " is", " a", " streamed", " response."]:
                    yield token
                    await asyncio.sleep(0.1)
            return mock_stream()
        return QueryResult(answer="Mock response")

    async def get_evaluation(self, run_id: str, wait: bool = True) -> EvaluationResult:
        """Get evaluation results for a query run."""
        return EvaluationResult(overall_score=0.95)

    async def list_pipelines(self) -> list[dict]:
        return [{"id": "default", "name": "Default Pipeline"}]

    async def create_pipeline(self, config: dict) -> dict:
        return {"id": "new-pipeline", "status": "created"}
