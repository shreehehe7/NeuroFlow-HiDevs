import asyncio
import logging
from typing import Coroutine, Any

logger = logging.getLogger(__name__)

timeouts = {
    "embedding": 10,
    "chat_completion": 60,
    "reranking": 15,
    "evaluation": 120,
    "file_extraction": 30,
    "url_fetch": 15
}

async def with_timeout(task_type: str, coro: Coroutine) -> Any:
    timeout = timeouts.get(task_type, 30)
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Timeout exceeded for task type {task_type} ({timeout}s)")
        # In real app: increment timeouts:{task_type} counter in Redis
        raise TimeoutError(f"Task {task_type} timed out after {timeout} seconds")
