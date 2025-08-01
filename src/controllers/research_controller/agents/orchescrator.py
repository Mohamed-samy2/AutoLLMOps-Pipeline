import logging
from typing import Literal
from config.config import get_settings
from .schemas.orchescratorschema import OrchestratorState
from .arxiv_agent import arxiv_agent
from .googlesearch_agent import google_agent
from .websearch_agent import websearch_agent
from .wikipedia_agent import wikipedia_agent
from langgraph.types import Command
from langgraph.graph import StateGraph,END
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.runnables import RunnableConfig
from .prompts.orchescrator_prompts import orchescrator_prompts
import time
class orchestrator_agent:
    def __init__(self,llm,
                checkpointer,
                db_client):
    
        self.llm = llm
        self.db_client = db_client
        self.checkpointer = checkpointer
        self.logger = logging.getLogger('uvicorn')   
        
        self.arxiv_agent = arxiv_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.google_agent = google_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.websearch_agent = websearch_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.wikipedia_agent = wikipedia_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        
        try:
            self.workflow = StateGraph(OrchestratorState)
            self.workflow.add_node("Planner",self.planner)
            self.workflow.add_node("ArxivAgent",self.arxiv_agent.graph)
            self.workflow.add_node("GoogleAgent",self.google_agent.graph)
            self.workflow.add_node("WebSearchAgent",self.websearch_agent.graph)
            self.workflow.add_node("WikipediaAgent",self.wikipedia_agent.graph)
            
            self.workflow.add_edge("Planner","ArxivAgent")
            self.workflow.add_edge("Planner","GoogleAgent")
            self.workflow.add_edge("Planner","WebSearchAgent")
            self.workflow.add_edge("Planner","WikipediaAgent")

            self.workflow.add_edge('ArxivAgent',END)
            self.workflow.add_edge('GoogleAgent',END)
            self.workflow.add_edge('WebSearchAgent',END)
            self.workflow.add_edge('WikipediaAgent',END)
            
            self.workflow.set_entry_point("Planner")

            self.graph = self.workflow.compile(checkpointer=self.checkpointer,debug=True,name="Orchestrator Agent")
            
            image_data = self.graph.get_graph(xray=1).draw_mermaid_png()
            with open("graph.png", "wb") as f:
                    f.write(image_data)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize the Orchestrator Agent. Error: {e}")
    
    async def planner(self,state: OrchestratorState):
        try:
            system_prompt = SystemMessage(content=orchescrator_prompts.PLANNER_SYSTEM_PROMPT.value)

            chat_messages = [system_prompt] + state['messages']
            time.sleep(10)
            response = await self.llm.generate_response(messages=chat_messages)

            return {'messages': response}
        
        except Exception as e:
            self.logger.error(f'Error calling model: {e}')
        
