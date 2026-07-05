# NeuroFlow SDK

## Quickstart
```python
import asyncio
from neuroflow import NeuroFlowClient

async def main():
    client = NeuroFlowClient(base_url="http://localhost:8000", api_key="test-key")
    doc = await client.ingest_file("test.pdf", pipeline_id="default")
    print(f"Ingested doc: {doc.id}")
    
    async for token in await client.query("What is this?", "default", stream=True):
        print(token, end="", flush=True)

asyncio.run(main())
```
