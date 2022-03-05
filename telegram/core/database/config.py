from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Instance stores all app settings, mainly environment variables"""

    PROJECT_NAME: str = "Onlineedu"
    DB_PATH: Optional[str]

    class Config:
        # env_prefix = 'ONLINEEDU_'
        # uncomment when testing locally
        env_file = ".env"
        # env_file_encoding = 'utf-8'


settings = Settings()
