from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from uuid import UUID
import re

@dataclass
class Citation:
    reference: str
    chunk_id: Optional[UUID]
    document_name: str
    page_number: Optional[int]
    content_preview: str
    invalid_citation: bool = False

class CitationParser:
    def parse_citations(self, response_text: str, context_sources: List[Dict[str, Any]]) -> List[Citation]:
        citations = []
        # Find all [Source N] patterns
        pattern = r'\[Source (\d+)\]'
        matches = re.finditer(pattern, response_text)
        
        seen_refs = set()
        
        for match in matches:
            ref_num = int(match.group(1))
            ref_str = f"Source {ref_num}"
            
            if ref_str in seen_refs:
                continue
            seen_refs.add(ref_str)
            
            if ref_num <= len(context_sources):
                source = context_sources[ref_num - 1]
                citations.append(Citation(
                    reference=ref_str,
                    chunk_id=source.get("chunk_id"),
                    document_name=source.get("document_name", "unknown"),
                    page_number=source.get("page_number"),
                    content_preview=source.get("content", "")[:100],
                    invalid_citation=False
                ))
            else:
                # Hallucinated citation
                citations.append(Citation(
                    reference=ref_str,
                    chunk_id=None,
                    document_name="unknown",
                    page_number=None,
                    content_preview="",
                    invalid_citation=True
                ))
                
        return citations
