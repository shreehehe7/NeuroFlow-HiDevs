from fastapi import APIRouter
import uuid
import sys
import os

# Adjusting path to import from pipelines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from pipelines.finetuning.extractor import TrainingDataExtractor
from pipelines.finetuning.tracker import FinetuneTracker
from pipelines.finetuning.job_manager import FinetuneJobManager

router = APIRouter()
jobs_db = {}

@router.post("/finetune/jobs")
async def trigger_finetune_job():
    job_id = uuid.uuid4()
    
    # Extract data
    extractor = TrainingDataExtractor(db_pool=None)
    pairs = await extractor.extract_training_pairs(job_id)
    
    if not pairs:
        return {"error": "No valid training pairs found."}
        
    # Start tracking
    tracker = FinetuneTracker()
    run_id = tracker.start_training_job(job_id, pairs, "gpt-4o-mini")
    
    # Submit job
    manager = FinetuneJobManager()
    provider_job_id = await manager.submit_finetune_job(f"backend/training_data/{job_id}.jsonl", "gpt-4o-mini")
    
    jobs_db[str(job_id)] = {
        "job_id": str(job_id),
        "status": "submitted",
        "provider_job_id": provider_job_id,
        "mlflow_run_id": run_id
    }
    return {"job_id": str(job_id), "status": "submitted"}

@router.get("/finetune/jobs")
async def list_jobs():
    return list(jobs_db.values())

@router.get("/finetune/jobs/{id}")
async def get_job(id: str):
    return jobs_db.get(id, {"error": "not found"})

@router.get("/finetune/training-data/preview")
async def preview_training_data():
    extractor = TrainingDataExtractor(db_pool=None)
    pairs = await extractor.extract_training_pairs(uuid.uuid4())
    return {"preview": pairs[:5]}
