import bleach
import re
from fastapi import HTTPException
import ipaddress
from urllib.parse import urlparse

def sanitize_text(text: str) -> str:
    return bleach.clean(text, tags=[], strip=True)

def validate_query(query: str):
    if len(query) > 5000:
        raise HTTPException(status_code=400, detail="Query too long")

def validate_pipeline_name(name: str):
    if len(name) > 100:
        raise HTTPException(status_code=400, detail="Pipeline name too long")

def validate_url(url: str):
    if not re.match(r"^https?://", url):
        raise HTTPException(status_code=400, detail="Invalid URL protocol")
        
    parsed = urlparse(url)
    hostname = parsed.hostname
    if hostname:
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback:
                raise HTTPException(status_code=400, detail="SSRF prevented: Private IP not allowed")
        except ValueError:
            # Not an IP, could resolve hostname here in a real scenario to prevent DNS rebinding
            pass
