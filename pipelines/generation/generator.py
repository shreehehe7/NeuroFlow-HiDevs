import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, llm_client, db_pool, redis_client=None):
        self.llm = llm_client
        self.db = db_pool
        self.redis = redis_client

    async def _mock_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        # Mocking stream since we don't have real LLM setup
        words = "Based on [Source 1], attention is all you need.".split(" ")
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)

    async def generate_stream(self, run_id: uuid.UUID, prompt: str, context_metadata: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        # Log prompt to pipeline_runs
        logger.info(f"Logging prompt for run_id {run_id}")
        
        full_response = ""
        
        # Keepalive background task concept (handled in API typically, but could be yielded)
        
        # Stream tokens
        async for chunk in self._mock_stream(prompt):
            full_response += chunk
            yield {"type": "token", "delta": chunk}
            
        # Parse citations (Mocking parsing call for now, assuming citation parser is used in the caller or here)
        from .citations import CitationParser
        parser = CitationParser()
        # Create mock context sources based on metadata
        mock_sources = [{"document_name": src, "chunk_id": uuid.uuid4()} for src in context_metadata.get("sources", [])]
        citations = parser.parse_citations(full_response, mock_sources)
        
        # Strip chain of thought if present
        if "<think>" in full_response:
            # logic to strip <think> tags goes here
            pass
            
        # Update pipeline_runs with final result
        logger.info(f"Updating run_id {run_id} as complete")
        
        # Asynchronously enqueue eval job (do not await)
        if self.redis:
            asyncio.create_task(self._enqueue_eval(run_id))
            
        yield {
            "type": "done",
            "run_id": str(run_id),
            "citations": [
                {
                    "source": c.reference,
                    "chunk_id": str(c.chunk_id) if c.chunk_id else None,
                    "document": c.document_name,
                    "page": c.page_number,
                    "invalid": c.invalid_citation
                }
                for c in citations
            ]
        }
        
    async def _enqueue_eval(self, run_id: uuid.UUID):
        # Enqueue evaluation job to Redis
        logger.info(f"Enqueueing eval for run_id {run_id}")
