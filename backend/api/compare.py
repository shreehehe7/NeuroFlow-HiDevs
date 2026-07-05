from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import uuid

router = APIRouter()

class CompareRequest(BaseModel):
    query: str
    pipeline_a_id: str
    pipeline_b_id: str

@router.post("/pipelines/compare")
async def compare_pipelines(req: CompareRequest):
    async def mock_run_pipeline(pipeline_id):
        # Mock pipeline run delay
        await asyncio.sleep(0.5)
        return {
            "run_id": str(uuid.uuid4()),
            "generation": "Mock answer based on context.",
            "retrieval_latency_ms": 234,
            "total_latency_ms": 1450,
            "chunks_used": 6,
            "eval_score": 0.87
        }
        
    result_a, result_b = await asyncio.gather(
        mock_run_pipeline(req.pipeline_a_id),
        mock_run_pipeline(req.pipeline_b_id)
    )
    
    return {
        "query": req.query,
        "pipeline_a": result_a,
        "pipeline_b": result_b
    }
