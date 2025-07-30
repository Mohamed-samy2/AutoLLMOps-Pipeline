from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class ArxivState(TypedDict):
    # Main States
    messages : Annotated[list, add_messages]
    
    arxiv_messages : Annotated[list, add_messages]