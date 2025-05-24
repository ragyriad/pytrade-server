from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    WSIMPLE_EMAIL: str
    DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
