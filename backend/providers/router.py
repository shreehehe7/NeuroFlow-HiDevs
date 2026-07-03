import json
from dataclasses import dataclass
from typing import Optional
from redis.asyncio import Redis

@dataclass
class RoutingCriteria:
    task_type: str          # "rag_generation" | "evaluation" | "embedding" | "classification"
    max_cost_per_call: Optional[float] = None
    require_vision: bool = False
    require_long_context: bool = False  # > 32k tokens
    latency_budget_ms: Optional[int] = None
    prefer_fine_tuned: bool = False

class ModelRouter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_models = [
            {
                "id": "gpt-4o",
                "provider": "openai",
                "vision": True,
                "context_window": 128000,
                "fine_tuned": False,
                "cost_input": 2.50,
                "cost_output": 10.00
            },
            {
                "id": "gpt-4o-mini",
                "provider": "openai",
                "vision": True,
                "context_window": 128000,
                "fine_tuned": False,
                "cost_input": 0.15,
                "cost_output": 0.60
            },
            {
                "id": "claude-3-5-sonnet-20240620",
                "provider": "anthropic",
                "vision": True,
                "context_window": 200000,
                "fine_tuned": False,
                "cost_input": 3.00,
                "cost_output": 15.00
            },
            {
                "id": "claude-3-haiku-20240307",
                "provider": "anthropic",
                "vision": True,
                "context_window": 200000,
                "fine_tuned": False,
                "cost_input": 0.25,
                "cost_output": 1.25
            },
            {
                "id": "gemini-1.5-flash",
                "provider": "gemini",
                "vision": True,
                "context_window": 1048576,
                "fine_tuned": False,
                "cost_input": 0.075,
                "cost_output": 0.30
            }
        ]

    async def _get_registered_models(self) -> list[dict]:
        models_json = await self.redis.get("router:models")
        if models_json:
            return json.loads(models_json)
        return self.default_models

    async def select_model(self, criteria: RoutingCriteria, estimated_input_tokens: int = 1000, estimated_output_tokens: int = 500) -> dict:
        models = await self._get_registered_models()
        valid_models = []
        
        for m in models:
            # Hard constraints
            if criteria.require_vision and not m.get("vision", False):
                continue
            
            # Rule: If require_long_context=True -> route to a model with >100k context
            if criteria.require_long_context and m.get("context_window", 0) <= 100000:
                continue
                    
            # Rule: If task_type="evaluation" -> always use a capable judge model, never a fine-tuned one
            if criteria.task_type == "evaluation" and m.get("fine_tuned", False):
                continue
                
            # Rule: If max_cost_per_call is set -> filter out models that would exceed it
            if criteria.max_cost_per_call is not None:
                cost_input = m.get("cost_input", 10.0) / 1_000_000
                cost_output = m.get("cost_output", 30.0) / 1_000_000
                est_cost = (estimated_input_tokens * cost_input) + (estimated_output_tokens * cost_output)
                if est_cost > criteria.max_cost_per_call:
                    continue
                    
            valid_models.append(m)

        if not valid_models:
            raise ValueError("No models available that satisfy the routing criteria")

        # Rule: If prefer_fine_tuned=True AND a fine-tuned model is registered for this task_type -> route to it
        if criteria.prefer_fine_tuned and criteria.task_type != "evaluation":
            fine_tuned_models = [m for m in valid_models if m.get("fine_tuned", False)]
            if fine_tuned_models:
                # Return the cheapest fine-tuned model
                return min(fine_tuned_models, key=lambda x: x.get("cost_input", float('inf')))

        # Default: route to the cheapest model that satisfies all hard constraints
        return min(valid_models, key=lambda x: x.get("cost_input", float('inf')))
