from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from typing import Any, Optional

class insertschema(BaseModel):
    raw_text:str = Field(..., description="The raw input text to be processed or stored. This could be a prompt, user input, or unprocessed data entry.")
    metadata: Optional[str]=Field(
        None, 
        description="Optional metadata as a dictionary"
    )
    db_client:Optional[Any] = None