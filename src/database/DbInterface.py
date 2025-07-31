from abc import ABC, abstractmethod
from typing import List
from .db_schemas.postgres import QAPair
class DbInterface(ABC):

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def is_table_existed(self, table_name: str) -> bool:
        pass

    @abstractmethod
    async def create_raw_table(self):
        pass
    @abstractmethod
    async def create_qa_table(self):
        pass
    @abstractmethod
    async def insert_raw_text(self, text:str,metadata:dict):
        pass

    @abstractmethod
    async def insert_qa(self, data: List[QAPair], type: str):
        pass

    @abstractmethod
    async def get_raw_text(self):
        pass
    
    @abstractmethod
    async def get_qa_pairs(self, type: str):
        pass