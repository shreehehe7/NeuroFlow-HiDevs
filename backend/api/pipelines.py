from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from typing import Dict, Any, List

router = APIRouter()

# Mock storage
pipelines_db = {}

@router.post("/pipelines")
async def create_pipeline(config: Dict[str, Any]):
    # In real app, validate with PipelineConfig model
    pipeline_id = str(uuid.uuid4())
    pipelines_db[pipeline_id] = {"id": pipeline_id, "config": config, "version": 1, "status": "active"}
    return {"pipeline_id": pipeline_id}

@router.get("/pipelines")
async def list_pipelines():
    return list(pipelines_db.values())

@router.get("/pipelines/{id}")
async def get_pipeline(id: str):
    return pipelines_db.get(id)

@router.patch("/pipelines/{id}")
async def update_pipeline(id: str, config: Dict[str, Any]):
    if id in pipelines_db:
        # Increment version instead of overwrite
        pipelines_db[id]["version"] += 1
        pipelines_db[id]["config"].update(config)
        return pipelines_db[id]
    return {"error": "not found"}

@router.delete("/pipelines/{id}")
async def delete_pipeline(id: str):
    if id in pipelines_db:
        pipelines_db[id]["status"] = "archived"
        return {"status": "archived"}
    return {"error": "not found"}

@router.get("/pipelines/{id}/analytics")
async def get_analytics(id: str):
    # Mock analytics
    return {
        "avg_retrieval_latency": {"p50": 100, "p95": 250, "p99": 400},
        "avg_generation_latency": 1200,
        "cost_per_query": 0.02
    }
