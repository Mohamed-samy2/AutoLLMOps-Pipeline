from enum import Enum

class PostgresRawTableEnum(Enum):
    TABLE_NAME = "raw_texts"
    RAW_TEXT = "raw_text"
    METADATA = "metadata"
    
class PostgresQATableEnum(Enum):
    TABLE_NAME = "qa_texts"
    QUESTION = "question"
    ANSWER = "answer"
    TYPE = "type"

class PostgresDbEnums(Enum):
    POSTGRES = "postgres"