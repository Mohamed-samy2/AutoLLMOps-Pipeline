from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class WebState(TypedDict):
    # Main States
    messages : Annotated[list, add_messages]
    
    web_messages : Annotated[list, add_messages]