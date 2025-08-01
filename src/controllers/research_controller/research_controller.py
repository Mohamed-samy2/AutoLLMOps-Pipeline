import logging
from typing import Literal
from config.config import get_settings
from langchain_core.messages import HumanMessage
import uuid
from .agents.orchescrator import orchestrator_agent

class research_controller:
    def __init__(self,llm,
                checkpointer,
                db_client):
    
        self.llm = llm
        self.db_client = db_client
        self.checkpointer = checkpointer
        self.logger = logging.getLogger('uvicorn')
        
        self.orchestrator = orchestrator_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
    
    async def run(self, message):
        
        for i in range(2):
            config = {'configurable': {
                'thread_id': str(uuid.uuid4()),
            },
                "recursion_limit": 100
            }

            input = {
                "messages": [HumanMessage(content=message)],
            }
            
            try:
                result = await self.orchestrator.graph.ainvoke(input, config=config)
                return True
            
            except Exception as e:
                self.logger.error(f"Error running the research controller: {e}")
                return False