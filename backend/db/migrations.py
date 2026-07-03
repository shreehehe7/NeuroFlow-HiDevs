import logging
from db.pool import get_pool

logger = logging.getLogger(__name__)

async def apply_migrations():
    pool = get_pool()
    if not pool:
        return
    try:
        async with pool.acquire() as conn:
            # Check if tables exist
            res = await conn.fetchval("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'documents');")
            if res:
                logger.info("Schema already applied.")
            else:
                logger.info("Waiting for docker-entrypoint-initdb.d to apply schema...")
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
