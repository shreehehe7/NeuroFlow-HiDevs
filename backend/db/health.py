import redis.asyncio as redis
import aiohttp
import logging
from db.pool import get_pool
from config import settings

logger = logging.getLogger(__name__)

async def check_postgres() -> bool:
    pool = get_pool()
    if not pool:
        return False
    try:
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Postgres health check failed: {e}")
        return False

async def check_redis() -> bool:
    try:
        r = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password)
        res = await r.ping()
        await r.aclose()
        return res
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False

async def check_mlflow() -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.mlflow_tracking_uri}/") as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"MLflow health check failed: {e}")
        return False
