# ADR 004: Model Routing Strategy

## Context
Different queries require different levels of reasoning. Sending every query to the most capable (and expensive) model is not cost-effective, while sending complex queries to a fast/cheap model results in poor quality.

## Decision
We will implement a **dynamic model routing matrix** in the Generation Subsystem. Queries will be classified (via a fast LLM or heuristic classifier) before generation:
- **Tier 1 (Fast & Cheap):** Simple summarization, direct fact retrieval -> e.g., Llama 3 8B or GPT-4o-mini.
- **Tier 2 (Balanced):** Moderate reasoning, standard RAG queries -> e.g., fine-tuned models from our pipeline.
- **Tier 3 (Heavy Reasoning):** Complex synthesis, coding, or ambiguous queries -> e.g., GPT-4o or Claude 3.5 Sonnet.

## Consequences
- **Positive:** Optimizes for cost and latency without significantly degrading perceived quality.
- **Positive:** Creates a clear path to integrate our own fine-tuned models into the Tier 2 bucket.
- **Negative:** Adds slight latency upfront to classify the query.
- **Negative:** Misclassification can lead to poor answers (if routed too low) or wasted money (if routed too high).
