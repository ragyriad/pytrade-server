from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings(BaseSettings):
    DATABASE_URL: str
    WSIMPLE_EMAIL: str


settings = Settings()
