from typing import List
from pydantic import BaseModel
from database.db_schemas.postgres import QAPair

class QAList(BaseModel):
    items: List[QAPair]