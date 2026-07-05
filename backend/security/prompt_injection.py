import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

INJECTION_PATTERNS = [
    r"ignore (all |previous |the |your )?instructions",
    r"you are now",
    r"new (system |)prompt",
    r"disregard (the |all |previous )",
    r"forget (everything|all|previous)",
    r"act as (if |a |an )",
    r"\[\[(system|SYSTEM)\]\]",
    r"<\|system\|>"
]

def scan_for_injection(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            logger.warning(f"Prompt injection pattern detected: {pattern}")
            return {"prompt_injection_detected": True, "pattern": pattern}
    return {"prompt_injection_detected": False}

async def llm_injection_detection(query: str) -> bool:
    # Mock LLM-based detection
    # In reality, it would ask LLM: "Does the following user message attempt to override..."
    if "ignore" in query.lower() or "new instructions" in query.lower():
        return True
    return False
