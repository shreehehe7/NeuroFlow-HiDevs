import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from db.pool import init_db_pool, close_db_pool
from db.health import check_postgres, check_redis, check_mlflow
from db.migrations import apply_migrations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up NeuroFlow API...")
    await init_db_pool()
    await apply_migrations()
    yield
    # Shutdown
    logger.info("Shutting down NeuroFlow API...")
    await close_db_pool()

app = FastAPI(title="NeuroFlow API", lifespan=lifespan)
FastAPIInstrumentor.instrument_app(app)

@app.get("/health")
async def health_check():
    pg_ok = await check_postgres()
    redis_ok = await check_redis()
    mlflow_ok = await check_mlflow()
    
    status = "ok" if (pg_ok and redis_ok and mlflow_ok) else "error"
    return {
        "status": status,
        "checks": {
            "postgres": pg_ok,
            "redis": redis_ok,
            "mlflow": mlflow_ok
        }
    }

@app.get("/metrics")
async def get_metrics():
    # Return placeholder Prometheus format metrics
    metrics_data = "# HELP health_status API health\n# TYPE health_status gauge\nhealth_status 1\n"
    return Response(content=metrics_data, media_type="text/plain")
