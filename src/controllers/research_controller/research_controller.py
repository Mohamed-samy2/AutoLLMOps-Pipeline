import logging
from typing import Literal
from config.config import get_settings
from .agents.schemas.orchescratorschema import OrchestratorState
from .agents.arxiv_agent import arxiv_agent
from .agents.googlesearch_agent import google_agent
from .agents.websearch_agent import websearch_agent
from .agents.wikipedia_agent import wikipedia_agent
from langgraph.types import Command
from langgraph.graph import StateGraph,END
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
import uuid
class research_controller:
    def __init__(self,llm,
                checkpointer,
                db_client):
    
        self.llm = llm
        self.db_client = db_client
        self.checkpointer = checkpointer
        self.logger = logging.getLogger(__name__)   
        
        self.arxiv_agent = arxiv_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.google_agent = google_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.websearch_agent = websearch_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        self.wikipedia_agent = wikipedia_agent(llm=self.llm, db_client=self.db_client, checkpointer=self.checkpointer)
        
        try:
            self.workflow = StateGraph(OrchestratorState)
            self.workflow.add_node("ArxivAgent",self.arxiv_agent.graph)
            self.workflow.add_node("GoogleAgent",self.google_agent.graph)
            self.workflow.add_node("WebSearchAgent",self.websearch_agent.graph)
            self.workflow.add_node("WikipediaAgent",self.wikipedia_agent.graph)
            
            self.workflow.add_edge('ArxivAgent',END)
            self.workflow.add_edge('GoogleAgent',END)
            self.workflow.add_edge('WebSearchAgent',END)
            self.workflow.add_edge('WikipediaAgent',END)

            self.graph = self.workflow.compile(checkpointer=self.checkpointer,debug=False)
            
            image_data = self.graph.get_graph(xray=0).draw_mermaid_png()
            with open("graph.png", "wb") as f:
                    f.write(image_data)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize the Orchestrator Agent. Error: {e}")
    
    async def run(self, message):
        config = {'configurable': {
            'thread_id': str(uuid.uuid4()),
        }}

        input = {
            "messages": [HumanMessage(content=message)],
        }
        
        try:
            result = await self.graph.ainvoke(input, config=config)
            return True
        
        except Exception as e:
            self.logger.error(f"Error running the research controller: {e}")
            return False