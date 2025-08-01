import logging
from .tools import arxiv_tools
from langgraph.graph import StateGraph, END
from .schemas.arxivschema import ArxivState
from langchain_core.messages import  ToolMessage,SystemMessage
from langchain_core.runnables import RunnableConfig
from config.config import get_settings
from .prompts.arxiv_prompts import arxiv_prompts
class arxiv_agent:
    def __init__(self,llm,checkpointer=None, db_client=None):
        
        self.app_settings = get_settings()
        self.logger = logging.getLogger('uvicorn')        
        
        self.db_client = db_client
        self.llm = llm
        self.tools = {t.name: t for t in arxiv_tools}

        try:
            graph = StateGraph(ArxivState)
            graph.add_node("call_model", self.call_model)
            graph.add_node("action", self.take_action)
            
            graph.add_conditional_edges("call_model", self.exists_action, {True: "action", False: END})
            
            graph.add_edge("action", "call_model")
            graph.set_entry_point("call_model")
            
            self.graph = graph.compile(
                checkpointer=checkpointer,
                name="Arxiv Agent",
                debug=True
            )
            
        except Exception as e:
            self.logger.error(f'Error creating Arxiv Agent workflow: {e}')

    async def call_model(self, state: ArxivState, config:RunnableConfig): 
        try:                                                                                                                                                                                                                                                        
            system_prompt = SystemMessage(content=arxiv_prompts.ARXIV_SYSTEM_PROMPT.value)
            
            chat_messages = [system_prompt] + state['messages'] + state['arxiv_messages']
            response = await self.llm.generate_response(messages=chat_messages, tools=arxiv_tools)
        
            return {'arxiv_messages': response}
        
        except Exception as e:
            self.logger.error(f'Error calling model: {e}')
        
    async def exists_action(self, state: ArxivState, config:RunnableConfig):
        result = state['arxiv_messages'][-1]
        tool_calls = getattr(result, "tool_calls", None)
        return bool(tool_calls)
    
    async def take_action(self,state: ArxivState, config:RunnableConfig):
        try:
            tool_calls = state['arxiv_messages'][-1].tool_calls
            results = []
            for t in tool_calls:
                if t['name'] == "insert_raw_text":
                    args = {
                        **t['args'],
                        "db_client": self.db_client
                    }
                    result = await self.tools[t['name']].ainvoke(args, config=config)
                else:
                    result = await self.tools[t['name']].ainvoke(t['args'], config=config)
                results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=result))
                
            return {'arxiv_messages': results}
        
        except Exception as e:
            self.logger.error(f'Error taking action: {e}')