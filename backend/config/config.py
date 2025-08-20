
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(env_file='.env' , env_file_encoding='utf-8')
    
    news_api_key : str
    redis_url : str
    app_env: str = "production"
    
settings = Settings()