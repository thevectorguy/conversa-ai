from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = ConfigDict(extra='ignore', env_file='.env')
    
    # API Settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Data Settings
    DATA_PATH: str = "data/BiztelAI_DS_Dataset_V1.json"
    
    # LLM Settings
    MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    
    # Performance Settings
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 32
    
    # Development Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

settings = Settings()
