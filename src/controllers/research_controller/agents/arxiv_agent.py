import logging
from .tools import arxiv_tools
from langgraph.graph import StateGraph, END
from .schemas import OrderState
from .AgentPrompts.PromptEnums import OrderAgentPromptsEnum
from langchain_core.messages import  ToolMessage,RemoveMessage
from langchain_core.runnables import RunnableConfig
from config.configs import get_settings

class arxiv_agent():
    def __init__(self,llm,checkpointer=None,store=None):
        
        self.app_settings = get_settings()
        self.logger = logging.getLogger("uvicorn")        
        
        self.llm = llm
        self.tools = {t.name: t for t in arxiv_tools}

        
        try:
            graph = StateGraph(OrderState)
            graph.add_node("call_model", self.call_model)
            graph.add_node("action", self.take_action)
            graph.add_node("update_messages", self.update_messages)
            
            graph.add_conditional_edges("call_model", self.exists_action, {True: "action", False: END})
            
            graph.add_edge("action", "call_model")
            graph.set_entry_point("call_model")
            
            self.graph = graph.compile(
                checkpointer=checkpointer,
                name="Order Agent",
                debug=self.app_settings.DEBUG_MODE
            )
            
        except Exception as e:
            self.logger.error(f'Error creating Order Agent workflow: {e}')

    async def call_model(self, state: OrderState, config:RunnableConfig): 
        chat_history = '\n'.join([
                f"user: {m.content}" if m.type =='human' else f"ai: {m.content}"
                for m in state['messages'][:-1]
            ])

        try:
            system_prompt = self.langfuse.get_prompt(f"{OrderAgentPromptsEnum.FOLDER_NAME.value}/{OrderAgentPromptsEnum.ORDER_AGENT_SYSTEM.value}", 
                                                     label="production").compile(language=state['language'])                                                                                                                                                                                                                                                                                       
            
            user_prompt = self.langfuse.get_prompt(f"{OrderAgentPromptsEnum.FOLDER_NAME.value}/{OrderAgentPromptsEnum.ORDER_AGENT_HUMAN.value}", 
                                                   label="production").compile(usermessage=state['messages'][-1].content,
                                                                           chat_history=chat_history)
                                                                                                                                                   
            system_prompt = await self.llm.construct_prompt(prompt=system_prompt,
                                                            role=self.llm.enums.SYSTEM.value)
                        
            chat_messages = [system_prompt] 
            chat_messages.append(await self.llm.construct_prompt(prompt=user_prompt,
                                                                 role=self.llm.enums.USER.value))
            chat_messages += state['order_messages']
            
            response = await self.llm.generate_response(messages=chat_messages, tools=order_tools)
        
            return {'order_messages': response}
        
        except Exception as e:
            self.logger.error(f'Error calling model: {e}')
        
    async def exists_action(self, state: OrderState, config:RunnableConfig):
        result = state['order_messages'][-1]
        return len(result.tool_calls) > 0
    
    async def take_action(self,state: OrderState, config:RunnableConfig):
        try:
            tool_calls = state['order_messages'][-1].tool_calls
            results = []
            for t in tool_calls:
                result = self.tools[t['name']].ainvoke(t['args'],config=config) # must pass the settings by default
                results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=result))
                
            return {'order_messages': results}
        
        except Exception as e:
            self.logger.error(f'Error taking action: {e}')
        
    async def update_messages(self, state: OrderState,config:RunnableConfig):
        final_message = state['order_messages'][-1]
        delete_messages = [RemoveMessage(id=m.id) for m in state["order_messages"]]

        return {'messages': final_message,
                'order_messages': delete_messages }