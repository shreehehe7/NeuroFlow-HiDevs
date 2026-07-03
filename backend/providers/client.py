import sys
import os
from typing import AsyncGenerator
from redis.asyncio import Redis
from opentelemetry import trace
from tenacity import RetryError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from providers.base import ChatMessage, GenerationResult, BaseLLMProvider
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.router import ModelRouter, RoutingCriteria

tracer = trace.get_tracer(__name__)

class NeuroFlowClient:
    _instance = None

    def __new__(cls, redis_client: Redis = None):
        if cls._instance is None:
            cls._instance = super(NeuroFlowClient, cls).__new__(cls)
            cls._instance.redis = redis_client
            cls._instance.router = ModelRouter(redis_client)
            cls._instance.providers = {}
        return cls._instance

    def _get_provider(self, model_info: dict) -> BaseLLMProvider:
        provider_type = model_info.get("provider")
        model_name = model_info.get("id")
        
        if provider_type == "openai":
            if model_name not in self.providers:
                self.providers[model_name] = OpenAIProvider(model_name=model_name)
            return self.providers[model_name]
        elif provider_type == "anthropic":
            if model_name not in self.providers:
                self.providers[model_name] = AnthropicProvider(model_name=model_name)
            return self.providers[model_name]
        elif provider_type == "gemini":
            if model_name not in self.providers:
                self.providers[model_name] = GeminiProvider(model_name=model_name)
            return self.providers[model_name]
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    async def _record_metrics(self, result: GenerationResult):
        if self.redis:
            await self.redis.incr(f"metrics:model:{result.model}:calls")
            await self.redis.incrbyfloat(f"metrics:model:{result.model}:cost_usd", result.cost_usd)

    async def chat(self, messages: list[ChatMessage], routing_criteria: RoutingCriteria, **kwargs) -> GenerationResult:
        # FallbackChain implementation
        try:
            model_info = await self.router.select_model(routing_criteria)
        except ValueError as e:
            raise e

        # Prepare fallback order based on capabilities and cost
        fallback_models = []
        if model_info["id"] == "gpt-4o-mini":
            fallback_models = ["claude-3-haiku-20240307", "gpt-4o"]
        elif model_info["id"] == "claude-3-haiku-20240307":
            fallback_models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
        elif model_info["id"] == "gpt-4o":
            fallback_models = ["claude-3-5-sonnet-20240620"]
        
        models_to_try = [model_info["id"]] + fallback_models
        
        last_error = None
        for attempt_model_id in models_to_try:
            # Reconstruct model info from default if not passing full dict
            attempt_info = next((m for m in self.router.default_models if m["id"] == attempt_model_id), model_info)
            provider = self._get_provider(attempt_info)
            
            with tracer.start_as_current_span("provider_call") as span:
                span.set_attribute("model", attempt_model_id)
                try:
                    result = await provider.complete(messages, **kwargs)
                    
                    span.set_attribute("input_tokens", result.input_tokens)
                    span.set_attribute("output_tokens", result.output_tokens)
                    span.set_attribute("cost_usd", result.cost_usd)
                    span.set_attribute("latency_ms", result.latency_ms)
                    span.set_status(trace.status.Status(trace.status.StatusCode.OK))
                    
                    await self._record_metrics(result)
                    return result
                    
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, str(e)))
                    last_error = e
                    continue # Fallback to next model
                    
        raise RuntimeError(f"All providers in FallbackChain failed. Last error: {last_error}")

    async def stream(self, messages: list[ChatMessage], routing_criteria: RoutingCriteria, **kwargs) -> AsyncGenerator[str, None]:
        model_info = await self.router.select_model(routing_criteria)
        provider = self._get_provider(model_info)
        
        async for chunk in provider.stream(messages, **kwargs):
            yield chunk

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Hardcode OpenAI for embeddings as Anthropic doesn't support it natively yet.
        provider = self._get_provider({"id": "text-embedding-3-small", "provider": "openai"})
        with tracer.start_as_current_span("provider_embed") as span:
            span.set_attribute("model", "text-embedding-3-small")
            try:
                result = await provider.embed(texts)
                span.set_status(trace.status.Status(trace.status.StatusCode.OK))
                return result
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.status.Status(trace.status.StatusCode.ERROR, str(e)))
                raise
