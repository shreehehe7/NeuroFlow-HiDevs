import json
import re
from typing import List, Dict, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class TrainingDataExtractor:
    def __init__(self, db_pool):
        self.db = db_pool

    def contains_pii(self, text: str) -> bool:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(email_pattern, text) or re.search(phone_pattern, text):
            return True
        return False

    async def extract_training_pairs(self, job_id: UUID) -> List[Dict[str, Any]]:
        # Mock database fetch of training pairs where quality_score >= 0.82
        # and not included_in_job, user_rating >= 4 or null
        mock_pairs = [
            {
                "query": "What is the liability clause?",
                "context": "Liability is limited to $100.",
                "answer": "Based on [Source 1], the liability is limited to $100.",
                "faithfulness": 0.9
            }
        ]
        
        valid_pairs = []
        for pair in mock_pairs:
            # Validate
            if self.contains_pii(pair["query"]):
                continue
            
            tokens = len(pair["answer"].split())
            if tokens < 10 or tokens > 2000: # approximation
                continue
                
            if "[Source " not in pair["answer"]:
                continue
                
            if pair["faithfulness"] <= 0.8:
                continue
                
            # Format as OpenAI JSONL
            msg = {
                "messages": [
                    {"role": "system", "content": "You are a precise research assistant..."},
                    {"role": "user", "content": f"[Context]\n{pair['context']}\n[Question]\n{pair['query']}"},
                    {"role": "assistant", "content": pair["answer"]}
                ]
            }
            valid_pairs.append(msg)
            
        # Write to JSONL
        with open(f"backend/training_data/{job_id}.jsonl", "w") as f:
            for vp in valid_pairs:
                f.write(json.dumps(vp) + "\n")
                
        return valid_pairs
