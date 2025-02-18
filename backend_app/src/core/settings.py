from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_dsn: str = Field(
        "redis://localhost:6379/0",
        validation_alias="REDIS_DSN",
    )
