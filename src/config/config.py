from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    TARGET_DOMAIN:str
    USE_CASE:str
    DATA_SOURCES_PATH:str
    BASE_LLM:str

    # ============================ Database connection ===========================
    DB_BACKEND:str
    POSTGRES_USERNAME:str
    POSTGRES_PASSWORD:str
    POSTGRES_HOST:str
    POSTGRES_PORT:int
    POSTGRES_DB:str

    # ============================ LLM Config ============================
    LLM_PROVIDER:str
    LLM_MODEL_ID:str
    API_KEY:str
    
    # ============================ Training Config ============================
    TRAINING_OUTPUT_DIR:str
    LOGGING_DIR:str
    NUM_EPOCHS:int
    BATCH_SIZE:int
    LEARNING_RATE:float
    # ============================ Other Services Config ============================
    SERPAPI_KEY:str
    WANDB_API_KEY:str
    TAVILY_API_KEY:str

    class Config:
        env_file = ".env"
        
def get_settings():
    return Settings()