from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rabbit_url: str
    entry_queue: str
    retry_queue: str
    validation_queue: str
    dlq_queue: str

    class Config:
        env_file = ".env"


settings = Settings()
