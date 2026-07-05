import re
import os
import tiktoken
import numpy as np
from typing import List, Dict, Any, Optional
from google import genai
from sklearn.metrics.pairwise import cosine_similarity
from .extractors import ExtractedPage

class Chunker:
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        
    def chunk(self, pages: List[ExtractedPage], source_type: str) -> List[Dict[str, Any]]:
        if not pages:
            return []
            
        # Strategy selection
        has_headings = any(p.metadata.get("is_heading") for p in pages)
        is_large_pdf = source_type == "pdf" and len(pages) > 50
        
        chunks = []
        
        # Group pages by content type. Tables are always fixed_size (or just treated as single chunk if small)
        for page in pages:
            if page.content_type == "table":
                chunks.extend(self._fixed_size_chunk(page.content, page.page_number, page.metadata))
            else:
                # Apply strategy based on selection rules
                if has_headings and source_type == "docx":
                    # Hierarchical needs context across pages, but for simplicity we process per page or group
                    pass # We will handle hierarchical outside this loop
                elif is_large_pdf:
                    # Semantic chunking
                    chunks.extend(self._semantic_chunk(page.content, page.page_number, page.metadata))
                else:
                    chunks.extend(self._fixed_size_chunk(page.content, page.page_number, page.metadata))
                    
        # Handle hierarchical if selected
        if has_headings and source_type == "docx":
            chunks = self._hierarchical_chunk(pages)
            
        # Assign chunk_index
        for i, chunk in enumerate(chunks):
            chunk["chunk_index"] = i
            
        return chunks
        
    def _split_sentences(self, text: str) -> List[str]:
        # Basic sentence splitting (handles abbreviations poorly, but works for general text)
        sentences = re.split(r'(?<=[.!?]) +', text)
        return [s.strip() for s in sentences if s.strip()]

    def _fixed_size_chunk(self, text: str, page_number: int, metadata: Dict[str, Any], target_tokens: int = 512, overlap: int = 64) -> List[Dict[str, Any]]:
        chunks = []
        sentences = self._split_sentences(text)
        
        current_chunk_sentences = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoder.encode(sentence))
            
            if current_tokens + sentence_tokens > target_tokens and current_chunk_sentences:
                # Combine current chunk
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append({
                    "content": chunk_text,
                    "token_count": len(self.encoder.encode(chunk_text)),
                    "metadata": {**metadata, "page_number": page_number, "strategy": "fixed_size"}
                })
                
                # Overlap: keep the last few sentences that fit within the overlap limit
                overlap_tokens = 0
                overlap_sentences = []
                for s in reversed(current_chunk_sentences):
                    s_tokens = len(self.encoder.encode(s))
                    if overlap_tokens + s_tokens <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences
                current_tokens = overlap_tokens
                
            current_chunk_sentences.append(sentence)
            current_tokens += sentence_tokens
            
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "content": chunk_text,
                "token_count": len(self.encoder.encode(chunk_text)),
                "metadata": {**metadata, "page_number": page_number, "strategy": "fixed_size"}
            })
            
        return chunks

    def _semantic_chunk(self, text: str, page_number: int, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.client:
            return self._fixed_size_chunk(text, page_number, metadata)
            
        sentences = self._split_sentences(text)
        if len(sentences) <= 3:
            return self._fixed_size_chunk(text, page_number, metadata)
            
        # Get embeddings for all sentences
        try:
            response = self.client.models.embed_content(
                model='text-embedding-004',
                contents=sentences
            )
            embeddings = [e.values for e in response.embeddings]
        except Exception as e:
            print(f"Embedding failed: {e}, falling back to fixed size.")
            return self._fixed_size_chunk(text, page_number, metadata)
            
        chunks = []
        current_chunk_sentences = [sentences[0]]
        
        for i in range(1, len(sentences)):
            sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
            if sim < 0.7:
                # Topic shift, create chunk
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append({
                    "content": chunk_text,
                    "token_count": len(self.encoder.encode(chunk_text)),
                    "metadata": {**metadata, "page_number": page_number, "strategy": "semantic"}
                })
                current_chunk_sentences = [sentences[i]]
            else:
                current_chunk_sentences.append(sentences[i])
                
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                "content": chunk_text,
                "token_count": len(self.encoder.encode(chunk_text)),
                "metadata": {**metadata, "page_number": page_number, "strategy": "semantic"}
            })
            
        return chunks

    def _hierarchical_chunk(self, pages: List[ExtractedPage]) -> List[Dict[str, Any]]:
        chunks = []
        current_parent = None
        
        for page in pages:
            if page.content_type == "table":
                chunks.extend(self._fixed_size_chunk(page.content, page.page_number, page.metadata))
                continue
                
            is_heading = page.metadata.get("is_heading", False)
            level = page.metadata.get("level", "")
            
            if is_heading and level == "h1":
                current_parent = page.content
                # Store heading as its own chunk
                chunks.append({
                    "content": page.content,
                    "token_count": len(self.encoder.encode(page.content)),
                    "metadata": {**page.metadata, "page_number": page.page_number, "strategy": "hierarchical", "type": "parent"}
                })
            else:
                # Sub-section or content
                meta = {**page.metadata, "page_number": page.page_number, "strategy": "hierarchical"}
                if current_parent:
                    meta["parent_section"] = current_parent
                    
                # We can still apply fixed_size to the body under a heading if it's too long
                sub_chunks = self._fixed_size_chunk(page.content, page.page_number, meta)
                chunks.extend(sub_chunks)
                
        return chunks
