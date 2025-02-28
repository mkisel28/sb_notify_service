from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_dsn: str = Field(
        "redis://redis:6379/0",
        validation_alias="REDIS_DSN",
    )
    rabbitmq_url: str = Field(
        "amqp://user:password@localhost:5672",
        validation_alias="RABBITMQ_URL",
    )
    DB_NAME: str = Field(
        "sb_news",
        validation_alias="DB_NAME",
    )
    DB_USER: str = Field(
        "sb_user_POI5ty",
        validation_alias="DB_USER",
    )
    DB_PASSWORD: str = Field(
        "Jfdiodsfju!g@ids9K-32d",
        validation_alias="DB_PASSWORD",
    )
    DB_HOST: str = Field(
        "db",
        validation_alias="DB_HOST",
    )
    DB_PORT: int = Field(
        5432,
        validation_alias="DB_PORT",
    )

    @property
    def tortoise_config(self) -> dict:
        """Конфиг для Tortoise ORM."""
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": self.DB_NAME,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                    },
                },
            },
            "apps": {
                "models": {
                    "models": ["infra.database.models"],
                    "default_connection": "default",
                },
            },
            "use_tz": False,
            "timezone": "UTC",
        }


settings = Settings()  # type: ignore [assignment]
