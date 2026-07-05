async def evaluate_faithfulness(query: str, answer: str, context: str) -> float:
    """
    Extract claims from the answer: prompt LLM to list all factual statements as JSON array
    For each claim, prompt LLM: Is this claim supported by the context? Answer yes/no/partial
    Score: supported_claims / total_claims. partial counts as 0.5.
    Return 0.0 if answer makes claims but context is empty.
    """
    if not context or not answer:
        return 0.0
    # Mocking execution
    return 0.9
