from fastapi import HTTPException
from typing import Dict, Any

def check_queue_depth(depth: int) -> Dict[str, Any]:
    if depth > 100:
        raise HTTPException(
            status_code=503,
            detail={"error": "ingestion_queue_full", "queue_depth": depth, "retry_after": 30}
        )
    elif depth > 50:
        return {"status": 202, "warning": "high_queue_depth", "estimated_wait_minutes": 5}
    else:
        return {"status": 200, "message": "OK"}
