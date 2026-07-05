import os
import asyncio
import logging
from arq import Worker
from arq.connections import RedisSettings
from db.pool import init_db_pool, close_db_pool
from opentelemetry import trace
import json
import time

# Extractors and Chunker
from pipelines.ingestion.extractors.pdf_extractor import extract_pdf
from pipelines.ingestion.extractors.docx_extractor import extract_docx
from pipelines.ingestion.extractors.image_extractor import extract_image
from pipelines.ingestion.extractors.csv_extractor import extract_csv
from pipelines.ingestion.extractors.url_extractor import extract_url
from pipelines.ingestion.extractors.pptx_extractor import extract_pptx
from pipelines.ingestion.chunker import Chunker
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

async def startup(ctx):
    logger.info("Starting NeuroFlow Worker...")
    ctx['pool'] = await init_db_pool()
    ctx['chunker'] = Chunker()
    api_key = os.getenv("GEMINI_API_KEY")
    ctx['genai_client'] = genai.Client(api_key=api_key) if api_key else None

async def shutdown(ctx):
    logger.info("Worker shutting down...")
    await close_db_pool()

async def process_document(ctx, document_id: str, file_path_or_url: str, source_type: str):
    start_time = time.time()
    logger.info(f"Processing document {document_id} of type {source_type}")
    
    pool = ctx['pool']
    chunker = ctx['chunker']
    genai_client = ctx['genai_client']
    
    # Update status to processing
    async with pool.acquire() as conn:
        await conn.execute("UPDATE documents SET status = 'processing' WHERE id = $1", document_id)
        
    with tracer.start_as_current_span("ingestion.process") as span:
        span.set_attribute("document_id", str(document_id))
        span.set_attribute("source_type", source_type)
        
        try:
            # 1. Extraction
            pages = []
            if source_type == "pdf":
                pages = extract_pdf(file_path_or_url)
            elif source_type == "docx":
                pages = extract_docx(file_path_or_url)
            elif source_type == "image":
                pages = extract_image(file_path_or_url)
            elif source_type == "csv":
                pages = extract_csv(file_path_or_url)
            elif source_type == "url":
                pages = await extract_url(file_path_or_url)
            elif source_type == "pptx":
                pages = extract_pptx(file_path_or_url)
            elif source_type == "text":
                with open(file_path_or_url, "r", encoding="utf-8") as f:
                    from pipelines.ingestion.extractors import ExtractedPage
                    pages = [ExtractedPage(page_number=1, content=f.read(), content_type="text")]
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
                
            page_count = len(pages)
            span.set_attribute("page_count", page_count)
            
            # 2. Chunking
            chunks = chunker.chunk(pages, source_type)
            chunk_count = len(chunks)
            span.set_attribute("chunk_count", chunk_count)
            
            # 3. Embedding and DB Insertion
            total_tokens = 0
            embedding_calls = 0
            
            async with pool.acquire() as conn:
                for chunk in chunks:
                    content = chunk["content"]
                    token_count = chunk["token_count"]
                    metadata = chunk["metadata"]
                    chunk_index = chunk["chunk_index"]
                    
                    total_tokens += token_count
                    
                    # Compute embedding
                    embedding = None
                    if genai_client:
                        try:
                            response = genai_client.models.embed_content(
                                model='text-embedding-004',
                                contents=content
                            )
                            embedding = response.embeddings[0].values
                            embedding_calls += 1
                        except Exception as e:
                            logger.error(f"Failed to compute embedding for chunk {chunk_index}: {e}")
                    
                    # Convert embedding list to pgvector string format '[v1,v2,...]'
                    embedding_str = f"[{','.join(map(str, embedding))}]" if embedding else None
                    
                    await conn.execute(
                        """
                        INSERT INTO chunks (document_id, content, embedding, chunk_index, token_count, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        document_id, content, embedding_str, chunk_index, token_count, json.dumps(metadata)
                    )
            
            # Update document status to complete
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE documents SET status = 'complete', chunk_count = $1 WHERE id = $2",
                    chunk_count, document_id
                )
                
            span.set_attribute("embedding_calls", embedding_calls)
            
            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(json.dumps({
                "event": "ingestion_complete",
                "document_id": str(document_id),
                "duration_ms": duration_ms,
                "chunks": chunk_count,
                "tokens": total_tokens
            }))
            
        except Exception as e:
            logger.exception(f"Error processing document {document_id}")
            async with pool.acquire() as conn:
                await conn.execute("UPDATE documents SET status = 'error' WHERE id = $1", document_id)
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise e

class WorkerSettings:
    functions = [process_document]
    redis_settings = RedisSettings(host="redis", port=6379)
    on_startup = startup
    on_shutdown = shutdown

if __name__ == "__main__":
    from arq.cli import cli
    import sys
    sys.argv = ['arq', 'worker.WorkerSettings']
    cli()
