from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str
    cors_origins: str = "*"
    
    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"

settings = Settings()