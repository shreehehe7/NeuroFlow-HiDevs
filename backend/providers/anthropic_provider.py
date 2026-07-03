import time
from typing import AsyncGenerator
from anthropic import AsyncAnthropic, RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .base import BaseLLMProvider, ChatMessage, GenerationResult
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620"):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model_name = model_name
        self.prices = {
            "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00, "context": 200000},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25, "context": 200000}
        }
        
    @property
    def cost_per_input_token(self) -> float:
        price_info = self.prices.get(self.model_name, self.prices["claude-3-haiku-20240307"])
        return price_info["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        price_info = self.prices.get(self.model_name, self.prices["claude-3-haiku-20240307"])
        return price_info["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        price_info = self.prices.get(self.model_name, self.prices["claude-3-haiku-20240307"])
        return price_info["context"]

    def _format_messages(self, messages: list[ChatMessage]) -> tuple[list[dict], str]:
        formatted_messages = []
        system_prompt = ""
        for msg in messages:
            if msg.role == "system":
                system_prompt += (msg.content if isinstance(msg.content, str) else str(msg.content)) + "\n"
            else:
                formatted_messages.append({"role": msg.role, "content": msg.content})
        return formatted_messages, system_prompt.strip()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def complete(self, messages: list[ChatMessage], **kwargs) -> GenerationResult:
        start_time = time.time()
        formatted_msgs, system_prompt = self._format_messages(messages)
        
        request_params = {
            "model": self.model_name,
            "messages": formatted_msgs,
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        if system_prompt:
            request_params["system"] = system_prompt
            
        for k, v in kwargs.items():
            if k not in ["max_tokens", "system"]:
                request_params[k] = v
                
        response = await self.client.messages.create(**request_params)
        latency_ms = (time.time() - start_time) * 1000
        
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost_usd = (input_tokens * self.cost_per_input_token) + (output_tokens * self.cost_per_output_token)
        
        return GenerationResult(
            content=response.content[0].text if response.content else "",
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            finish_reason=response.stop_reason or "end_turn"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(RateLimitError)
    )
    async def stream(self, messages: list[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        formatted_msgs, system_prompt = self._format_messages(messages)
        
        request_params = {
            "model": self.model_name,
            "messages": formatted_msgs,
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        if system_prompt:
            request_params["system"] = system_prompt
            
        for k, v in kwargs.items():
            if k not in ["max_tokens", "system"]:
                request_params[k] = v

        async with self.client.messages.stream(**request_params) as stream:
            async for text in stream.text_stream:
                yield text

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic does not have a native text embeddings API
        raise NotImplementedError("Anthropic does not support text embeddings natively.")
