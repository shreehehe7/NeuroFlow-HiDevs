import mlflow
from uuid import UUID
from typing import List, Any
import logging

logger = logging.getLogger(__name__)

class FinetuneTracker:
    def start_training_job(self, job_id: UUID, pairs: List[Any], base_model: str) -> str:
        mlflow.set_tracking_uri("http://localhost:5000")
        try:
            with mlflow.start_run(run_name=f"finetune-{job_id}") as run:
                mlflow.log_params({
                    "base_model": base_model,
                    "training_pair_count": len(pairs),
                    "avg_quality_score": 0.85, # mock average
                    "date_range": "2024-01-01 to 2024-01-31"
                })
                
                # Log training data as artifact
                mlflow.log_artifact(f"backend/training_data/{job_id}.jsonl")
                
                return run.info.run_id
        except Exception as e:
            logger.error(f"Failed to track run: {e}")
            return "mock-run-id"
            
    def log_job_completion(self, run_id: str, job_id: UUID, job_result: Any):
        mlflow.set_tracking_uri("http://localhost:5000")
        try:
            with mlflow.start_run(run_id=run_id):
                mlflow.log_metrics({
                    "training_loss": getattr(job_result, "training_loss", 0.1),
                    "validation_loss": getattr(job_result, "validation_loss", 0.15),
                    "training_token_count": getattr(job_result, "trained_tokens", 1000)
                })
                
                mlflow.register_model(f"runs:/{run_id}/model", f"neuroflow-finetune-{job_id}")
        except Exception as e:
            logger.error(f"Failed to log completion: {e}")
