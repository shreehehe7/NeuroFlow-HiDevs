import asyncpg
import logging
from config import settings

logger = logging.getLogger(__name__)
pool = None

async def init_db_pool():
    global pool
    try:
        dsn = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)
        logger.info("Database pool initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize db pool: {e}")

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed.")

def get_pool():
    return pool
