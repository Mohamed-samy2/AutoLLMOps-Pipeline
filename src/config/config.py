from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    target_domain:str
    use_case:str
    data_sources_path:str
    base_llm:str
    
    class Config:
        env_file = ".env"
        
def get_settings():
    return Settings()