import tiktoken
from typing import List, Dict, Any
from . import RetrievalResult

class ContextAssembler:
    def __init__(self, model_name="gpt-4"):
        self.encoding = tiktoken.encoding_for_model(model_name)
        
    def assemble(self, chunks: List[RetrievalResult], max_tokens: int = 4000) -> Dict[str, Any]:
        context_parts = []
        chunks_used = []
        sources = set()
        total_tokens = 0
        
        for chunk in chunks:
            # Format: [Source N - document_name.pdf, page X]
            doc_name = chunk.metadata.get("document_name", "unknown")
            page = chunk.metadata.get("page", "unknown")
            source_label = f"[{doc_name}, page {page}]"
            
            chunk_text = f"{source_label}\n{chunk.content}\n\n"
            tokens = len(self.encoding.encode(chunk_text))
            
            if total_tokens + tokens <= max_tokens:
                context_parts.append(chunk_text)
                chunks_used.append(chunk.chunk_id)
                sources.add(doc_name)
                total_tokens += tokens
            else:
                break
                
        return {
            "context": "".join(context_parts),
            "chunks_used": chunks_used,
            "total_tokens": total_tokens,
            "sources": list(sources)
        }
