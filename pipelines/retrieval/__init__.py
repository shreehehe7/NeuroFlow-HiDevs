from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class RetrievalResult:
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    rank: Optional[int] = None
