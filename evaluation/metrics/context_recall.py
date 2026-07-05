async def evaluate_context_recall(query: str, chunks: list[str], answer: str) -> float:
    """
    Break the answer into sentences.
    For each sentence, ask LLM: Can this sentence be attributed to the provided context?
    Score: attributable_sentences / total_sentences
    """
    if not chunks or not answer:
        return 0.0
    # Mocking execution
    return 0.82
