from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class GoogleState(TypedDict):
    # Main States
    messages : Annotated[list, add_messages]
    
    google_messages : Annotated[list, add_messages]