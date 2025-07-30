from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class OrchestratorState(TypedDict):
    # Main States
    messages : Annotated[list, add_messages]
    