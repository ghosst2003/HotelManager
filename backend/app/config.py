from pathlib import Path
from pydantic_settings import BaseSettings

_env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    class Config:
        env_file = str(_env_path)


settings = Settings()
