from ..DbInterface import DbInterface
from ..DbEnums import (PostgresRawTableEnum,PostgresQATableEnum)
import logging
from typing import List
from sqlalchemy.sql import text as sql_query
import json
from ..db_schemas.postgres import QAPair

class postgres(DbInterface):
    def __init__(self,db_client):
        self.db_client = db_client
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        try:
            async with self.db_client() as session:
                async with session.begin():
                    result = await session.execute(sql_query("SELECT 1"))
            if result.scalar() == 1:
                self.logger.info("Connected to PostgreSQL database successfully.")
                return True
            else:
                self.logger.error("Failed to connect to PostgreSQL database.")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to PostgreSQL database: {e}")
            return False
    async def disconnect(self):
        pass
    
    async def is_table_existed(self, table_name: str) -> bool:
        
        is_existed = None
        async with self.db_client() as session:
            async with session.begin():
                list_table = sql_query(f"SELECT * FROM pg_tables WHERE tablename = :table_name")
                results = await session.execute(list_table,{"table_name": table_name})
                is_existed = results.scalar_one_or_none()

        return is_existed is not None
    
    async def create_raw_table(self):
        
        if await self.is_table_existed(PostgresRawTableEnum.TABLE_NAME.value):
            self.logger.info("Raw table already exists.")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                create_table_query = sql_query(f"""
                    CREATE TABLE IF NOT EXISTS {PostgresRawTableEnum.TABLE_NAME.value} (
                        id SERIAL PRIMARY KEY,
                        {PostgresRawTableEnum.RAW_TEXT.value} TEXT NOT NULL,
                        {PostgresRawTableEnum.METADATA.value} JSONB 
                    );
                """)
                await session.execute(create_table_query)
                await session.commit()
        return True
    
    async def create_qa_table(self):
        
        if await self.is_table_existed(PostgresQATableEnum.TABLE_NAME.value):
            self.logger.info("QA table already exists.")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                create_table_query = sql_query(f"""
                    CREATE TABLE IF NOT EXISTS {PostgresQATableEnum.TABLE_NAME.value} (
                        id SERIAL PRIMARY KEY,
                        {PostgresQATableEnum.QUESTION.value} TEXT NOT NULL,
                        {PostgresQATableEnum.ANSWER.value} TEXT NOT NULL,
                        {PostgresQATableEnum.TYPE.value} VARCHAR(50) NOT NULL
                    );
                """)
                await session.execute(create_table_query)
                await session.commit()
                
        return True
    
    async def insert_raw_text(self, text:str, metadata:dict):
        
        if not await self.is_table_existed(PostgresRawTableEnum.TABLE_NAME.value):
            await self.create_raw_table()
        
        metadata_json = json.dumps(metadata,ensure_ascii=False) if metadata is not None else "{}"
        
        async with self.db_client() as session:
            async with session.begin():
                insert_query = sql_query(f"""
                    INSERT INTO {PostgresRawTableEnum.TABLE_NAME.value} 
                    ({PostgresRawTableEnum.RAW_TEXT.value}, {PostgresRawTableEnum.METADATA.value}) 
                    VALUES (:text, :metadata);
                """)
                await session.execute(insert_query, {"text": text, "metadata": metadata_json})
                await session.commit()
        return True

    async def insert_qa(self, data: List[QAPair],type:str):
        
        if not await self.is_table_existed(PostgresQATableEnum.TABLE_NAME.value):
            await self.create_qa_table()
        
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(data), 50):
                    batch = [{"question": item.question, "answer": item.answer , "type": type} for item in data[i:i + 50]]
                    insert_query = sql_query(f"""
                        INSERT INTO {PostgresQATableEnum.TABLE_NAME.value} 
                        ({PostgresQATableEnum.QUESTION.value}, {PostgresQATableEnum.ANSWER.value}, {PostgresQATableEnum.TYPE.value}) 
                        VALUES (:question, :answer, :type);
                    """)
                    await session.execute(insert_query, batch)
                    await session.commit()
        return True
    
    async def get_raw_text(self):
        
        if not await self.is_table_existed(PostgresRawTableEnum.TABLE_NAME.value):
            self.logger.warning("Raw Text table does not exist.")
            return 
        
        async with self.db_client() as session:
            async with session.begin():
                select_query = sql_query(f"""
                                        SELECT * FROM {PostgresRawTableEnum.TABLE_NAME.value};
                                        """)
                result = await session.stream(select_query)
                async for row in result:
                    yield row

    async def get_qa_pairs(self, type: str):
        if not await self.is_table_existed(PostgresQATableEnum.TABLE_NAME.value):
            self.logger.warning("QA table does not exist.")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                select_query = sql_query(f"""
                                        SELECT * FROM {PostgresQATableEnum.TABLE_NAME.value} 
                                        WHERE {PostgresQATableEnum.TYPE.value} = :type;
                                        """)
                results = await session.execute(select_query, {"type": type})
                records = results.fetchall()

        return [QAPair(**row._mapping) for row in records]
