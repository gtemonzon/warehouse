from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "warehouse"
    mysql_user: str = "warehouse_user"
    mysql_password: str = "12345678"
    database_url: str | None = None
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"

    @property
    def url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

settings = Settings()
