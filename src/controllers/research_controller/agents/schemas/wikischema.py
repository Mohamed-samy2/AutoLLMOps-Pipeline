from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class WikiState(TypedDict):
    # Main States
    messages : Annotated[list, add_messages]
    
    wiki_messages : Annotated[list, add_messages]