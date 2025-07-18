from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rabbit_url: str
    entry_queue: str
    retry_queue: str
    validation_queue: str
    dlq_queue: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
