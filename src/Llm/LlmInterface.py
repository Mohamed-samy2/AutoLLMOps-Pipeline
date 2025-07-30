from abc import ABC, abstractmethod
from pydantic import BaseModel

class LlmInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    async def generate_response(self, messages: list=[], response_schema:BaseModel=None, tools = None, temperature=None):
        pass
    