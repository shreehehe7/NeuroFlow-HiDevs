import time
from typing import AsyncGenerator
from openai import AsyncOpenAI, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import BaseLLMProvider, ChatMessage, GenerationResult
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model_name = model_name
        self.prices = {
            "gpt-4o": {"input": 2.50, "output": 10.00, "context": 128000},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60, "context": 128000}
        }
        
    @property
    def cost_per_input_token(self) -> float:
        price_info = self.prices.get(self.model_name, self.prices["gpt-4o-mini"])
        return price_info["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        price_info = self.prices.get(self.model_name, self.prices["gpt-4o-mini"])
        return price_info["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        price_info = self.prices.get(self.model_name, self.prices["gpt-4o-mini"])
        return price_info["context"]

    def _format_messages(self, messages: list[ChatMessage]) -> list[dict]:
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def complete(self, messages: list[ChatMessage], **kwargs) -> GenerationResult:
        start_time = time.time()
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self._format_messages(messages),
            **kwargs
        )
        latency_ms = (time.time() - start_time) * 1000
        
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        cost_usd = (input_tokens * self.cost_per_input_token) + (output_tokens * self.cost_per_output_token)
        
        return GenerationResult(
            content=response.choices[0].message.content or "",
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            finish_reason=response.choices[0].finish_reason or "stop"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def stream(self, messages: list[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        response_stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self._format_messages(messages),
            stream=True,
            **kwargs
        )
        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def embed(self, texts: list[str]) -> list[list[float]]:
        # text-embedding-3-small by default with batch size of 100
        all_embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(batch_embeddings)
        return all_embeddings
