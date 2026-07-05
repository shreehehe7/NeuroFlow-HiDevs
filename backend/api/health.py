from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    # Mocking status
    return {
        "status": "degraded",
        "checks": {
            "postgres": {"status": "ok", "latency_ms": 3},
            "redis": {"status": "ok", "latency_ms": 1},
            "mlflow": {"status": "ok", "latency_ms": 45},
            "circuit_breakers": {
                "openai": {"state": "closed", "failure_count": 0},
                "anthropic": {"state": "open", "opened_at": "2024-01-15T10:23:00Z"}
            },
            "queue_depth": 23,
            "worker_count": 2
        }
    }
