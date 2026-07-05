import os
import uuid
import hashlib
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional
from db.pool import get_db
import asyncpg
from arq import create_pool
from arq.connections import RedisSettings

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024 # 100MB

# Helper to get ARQ pool
async def get_arq_pool(request: Request):
    if not hasattr(request.app.state, 'arq_pool'):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        # simple parsing of redis_url to settings
        host = redis_url.split("://")[1].split(":")[0]
        port = int(redis_url.split(":")[2].split("/")[0]) if len(redis_url.split(":")) > 2 else 6379
        request.app.state.arq_pool = await create_pool(RedisSettings(host=host, port=port))
    return request.app.state.arq_pool

class URLIngestRequest(BaseModel):
    url: str

def get_source_type(filename: str, content_type: str) -> str:
    ext = filename.split('.')[-1].lower() if '.' in filename else ""
    if ext == 'pdf' or 'pdf' in content_type:
        return 'pdf'
    if ext in ['docx', 'doc'] or 'word' in content_type:
        return 'docx'
    if ext in ['jpg', 'jpeg', 'png', 'webp'] or 'image' in content_type:
        return 'image'
    if ext == 'csv' or 'csv' in content_type:
        return 'csv'
    if ext == 'pptx' or 'presentation' in content_type:
        return 'pptx'
    return 'text'

@router.post("/ingest")
async def ingest_document(
    request: Request,
    file: Optional[UploadFile] = File(None),
    url_req: Optional[URLIngestRequest] = None, # Wait, FastAPI doesn't easily mix File and JSON body in same route cleanly unless using Form or Depends. We will handle url via Form or just check request body.
    url: Optional[str] = Form(None)
):
    if not file and not url:
        raise HTTPException(status_code=400, detail="Must provide either a file or a url")

    file_bytes = b""
    filename = ""
    source_type = ""
    file_path_or_url = ""

    if file:
        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")
        filename = file.filename
        source_type = get_source_type(filename, file.content_type)
        
        # Save to shared volume
        upload_dir = "/app/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        file_path_or_url = file_path
    elif url:
        # url ingest
        filename = url
        source_type = 'url'
        file_path_or_url = url
        file_bytes = url.encode('utf-8')

    # Hash for deduplication
    content_hash = hashlib.sha256(file_bytes).hexdigest()

    pool = request.app.state.pool
    arq_pool = await get_arq_pool(request)

    async with pool.acquire() as conn:
        # Check deduplication
        existing_doc = await conn.fetchrow(
            "SELECT id, status FROM documents WHERE content_hash = $1", 
            content_hash
        )
        if existing_doc:
            return {
                "document_id": existing_doc["id"],
                "status": existing_doc["status"],
                "duplicate": True
            }

        # Insert new doc
        doc_id = uuid.uuid4()
        await conn.execute(
            """
            INSERT INTO documents (id, filename, source_type, content_hash, status, metadata)
            VALUES ($1, $2, $3, $4, 'queued', $5)
            """,
            doc_id, filename, source_type, content_hash, json.dumps({})
        )

        # Enqueue job
        await arq_pool.enqueue_job(
            'process_document',
            str(doc_id),
            file_path_or_url,
            source_type
        )

        return {
            "document_id": str(doc_id),
            "status": "queued",
            "duplicate": False
        }

@router.get("/documents/{document_id}")
async def get_document(request: Request, document_id: str):
    pool = request.app.state.pool
    async with pool.acquire() as conn:
        doc = await conn.fetchrow(
            "SELECT id, filename, status, chunk_count, metadata, created_at FROM documents WHERE id = $1",
            document_id
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        return dict(doc)
