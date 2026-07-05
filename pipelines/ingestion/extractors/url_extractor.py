import httpx
import trafilatura
from urllib.parse import urlparse
import urllib.robotparser
from typing import List
from . import ExtractedPage
import asyncio

async def extract_url(url: str) -> List[ExtractedPage]:
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        can_fetch = rp.can_fetch("*", url)
    except Exception:
        # Default to fetch if robots.txt is unavailable or fails
        can_fetch = True
        
    if not can_fetch:
        return [ExtractedPage(page_number=1, content="Blocked by robots.txt", content_type="text")]
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            return [ExtractedPage(page_number=1, content=f"Failed to fetch URL: {str(e)}", content_type="text")]
            
    extracted_text = trafilatura.extract(
        html, 
        include_tables=True, 
        include_comments=False, 
        output_format="markdown"
    )
    
    metadata_dict = trafilatura.extract_metadata(html)
    
    metadata = {}
    if metadata_dict:
        metadata = {
            "title": metadata_dict.title,
            "author": metadata_dict.author,
            "url": metadata_dict.url or url,
            "date": metadata_dict.date
        }
        
    if not extracted_text:
        extracted_text = "No main content found."
        
    return [ExtractedPage(
        page_number=1,
        content=extracted_text,
        content_type="text",
        metadata=metadata
    )]
