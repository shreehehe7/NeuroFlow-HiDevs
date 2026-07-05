import asyncio
from neuroflow import NeuroFlowClient

async def run_quickstart():
    print("Mocking quickstart...")
    client = NeuroFlowClient(base_url="http://localhost:8000", api_key="mock-key")
    doc = await client.ingest_file("mock.pdf")
    print(f"Document ingested: {doc.id}")
    
    print("Streaming response:")
    async for token in await client.query("What is mock?", "default", stream=True):
        print(token, end="", flush=True)
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(run_quickstart())
