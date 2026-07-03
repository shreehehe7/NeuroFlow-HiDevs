from openai import AsyncOpenAI
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from providers.openai_provider import OpenAIProvider

class GeminiProvider(OpenAIProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        # Google's Gemini API has an official OpenAI-compatible endpoint!
        self.client = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model_name = model_name
        
        # Gemini Pricing (free tier effectively 0.0)
        # Using typical paid tier prices just for metrics tracking
        self.prices = {
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30, "context": 1048576},
            "gemini-1.5-pro": {"input": 3.50, "output": 10.50, "context": 2097152}
        }
