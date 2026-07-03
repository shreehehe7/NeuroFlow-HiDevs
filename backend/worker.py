import asyncio
import logging
from db.pool import init_db_pool, close_db_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting NeuroFlow Worker...")
    await init_db_pool()
    try:
        while True:
            logger.info("Worker heartbeat...")
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        logger.info("Worker cancelled, shutting down...")
    finally:
        await close_db_pool()

if __name__ == "__main__":
    asyncio.run(main())
