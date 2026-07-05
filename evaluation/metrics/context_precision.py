async def evaluate_context_precision(query: str, chunks: list[str], answer: str) -> float:
    """
    For each retrieved chunk, ask LLM: Was this passage useful in generating the answer? yes/no
    Compute: proportion of useful chunks among retrieved chunks, weighted by rank.
    """
    if not chunks:
        return 0.0
    # Mocking execution
    return 0.75
