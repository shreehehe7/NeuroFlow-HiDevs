from fastapi import APIRouter, Request, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
import uuid
import json
import asyncio

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    pipeline_id: uuid.UUID
    stream: bool = True

@router.post("/query")
async def handle_query(req: QueryRequest):
    run_id = uuid.uuid4()
    if not req.stream:
        return {"run_id": str(run_id), "status": "processing"}
        
    return {"run_id": str(run_id)}

@router.get("/query/{run_id}/stream")
async def stream_query(run_id: str, request: Request):
    async def event_generator():
        # Keepalive every 15s handled by sse_starlette if configured, or manually
        yield {"data": json.dumps({"type": "retrieval_start"})}
        
        await asyncio.sleep(0.5)
        
        yield {"data": json.dumps({
            "type": "retrieval_complete", 
            "chunk_count": 2, 
            "sources": ["doc.pdf"]
        })}
        
        # Mocking the generation stream
        words = ["Based", " on", " the", " context,", " this", " is", " the", " answer", " [Source 1]"]
        for word in words:
            if await request.is_disconnected():
                break
            yield {"data": json.dumps({"type": "token", "delta": word})}
            await asyncio.sleep(0.1)
            
        yield {"data": json.dumps({
            "type": "done",
            "run_id": run_id,
            "citations": [{
                "source": "Source 1",
                "chunk_id": str(uuid.uuid4()),
                "document": "doc.pdf",
                "page": 1
            }]
        })}
        
    return EventSourceResponse(event_generator())

class RatingRequest(BaseModel):
    rating: int

@router.patch('/runs/{run_id}/rating')
async def rate_run(run_id: str, req: RatingRequest):
    # Mock updating evaluations.user_rating
    return {'status': 'success', 'run_id': run_id, 'user_rating': req.rating}

