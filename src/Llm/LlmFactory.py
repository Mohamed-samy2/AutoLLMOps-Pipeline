from .LlmEnums import LlmProviders
from .providers.Gemini import Gemini 

class LlmFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LlmProviders.GEMINI.value:
            return Gemini(
                api_key=self.config.API_KEY,
                model_id=self.config.LLM_MODEL_ID,
                temperature=self.config.TEMPERATURE,
            )