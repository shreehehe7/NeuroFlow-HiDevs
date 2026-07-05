from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ExtractedPage:
    page_number: int
    content: str
    content_type: str  # "text" | "table" | "image_description"
    metadata: Dict[str, Any] = field(default_factory=dict)
