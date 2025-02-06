from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    DATABASE_URL: str
    QUESTRADE_ACCESS_TOKEN: str
    QUESTRADE_SERVER: str
    QUESTRADE_REFRESH_TOKEN: str
    WSIMPLE_EMAIL: str
    WSIMPLE_PASSWORD: str
    WSIMPLE_REFRESH_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()
