# ADR 003: Evaluation Framework

## Context
To ensure the RAG pipeline provides high-quality responses, we need to evaluate metrics like faithfulness, answer relevance, context precision, and context recall. Relying purely on human annotation is unscalable, slow, and expensive given the volume of generations.

## Decision
We will use **Automated LLM-as-a-Judge Evaluation** (using a highly capable model like GPT-4o) to asynchronously score every generation, supplemented by periodic human audits (e.g., 1-5% of logs).

## Consequences
- **Positive:** Enables 100% coverage of generation evaluation automatically and in near real-time.
- **Positive:** Allows programmatic extraction of high-quality data (Faithfulness > 0.8) for fine-tuning.
- **Negative:** LLM judges can suffer from biases (e.g., position bias, verbosity bias) and may occasionally hallucinate scores.
- **Mitigation:** We will detect failure modes by comparing LLM-judge scores with human annotations on a small sample set. If divergence exceeds an acceptable threshold, we will refine the judge's prompt or swap the judge model.
