import asyncio
import logging
from .metrics.faithfulness import evaluate_faithfulness
from .metrics.answer_relevance import evaluate_answer_relevance
from .metrics.context_precision import evaluate_context_precision
from .metrics.context_recall import evaluate_context_recall

logger = logging.getLogger(__name__)

class EvaluationJudge:
    def __init__(self, db_pool, llm_router=None):
        self.db = db_pool
        self.router = llm_router

    async def evaluate(self, run_id: str, query: str, answer: str, context: str, chunks: list[str]):
        # Run all metrics in parallel
        faith, relevance, precision, recall = await asyncio.gather(
            evaluate_faithfulness(query, answer, context),
            evaluate_answer_relevance(query, answer),
            evaluate_context_precision(query, chunks, answer),
            evaluate_context_recall(query, chunks, answer)
        )
        
        overall_score = 0.35 * faith + 0.30 * relevance + 0.20 * precision + 0.15 * recall
        
        logger.info(f"Evaluated run {run_id}. Overall: {overall_score:.2f}")
        
        # Mock database write to evaluations table
        # if overall_score > 0.8:
        #     logger.info(f"Marking run {run_id} as training pair")
        
        # Emits OpenTelemetry span ideally here
        
        return {
            "run_id": run_id,
            "overall_score": overall_score,
            "faithfulness": faith,
            "answer_relevance": relevance,
            "context_precision": precision,
            "context_recall": recall
        }
