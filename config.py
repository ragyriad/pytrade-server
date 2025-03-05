from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings(BaseSettings):
    DATABASE_URL: str
    QUESTRADE_ACCESS_TOKEN: str
    QUESTRADE_SERVER: str
    QUESTRADE_REFRESH_TOKEN: str
    WSIMPLE_EMAIL: str
    WSIMPLE_PASSWORD: str
    WSIMPLE_REFRESH_TOKEN: str


settings = Settings()
