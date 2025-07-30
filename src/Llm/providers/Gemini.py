from ..LlmInterface import LlmInterface
import logging
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI



class Gemini(LlmInterface):
    def __init__(self,api_key, model_id: str, temperature: float = 0.2):
        self.logger = logging.getLogger(__name__)
        self.model_id = model_id
        self.temperature = temperature
        self.client = None
        self.api_key = api_key

    def set_generation_model(self, model_id: str):
        self.model_id = model_id
        self.client = ChatGoogleGenerativeAI(api_key=self.api_key, model=model_id, temperature=self.temperature)

    async def generate_response(self, messages: list, response_schema: BaseModel=None, tools=None):
        
        if tools:
            result = await self.client.bind_tools(tools, tool_choice='auto').ainvoke(messages)
            return result
        
        if response_schema:
                result =  await self.client.with_structured_output(schema=response_schema,strict=True).ainvoke(messages)
                return result

        
        result = await self.client.ainvoke(messages)
        return result
