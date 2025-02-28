from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class SourceType(StrEnum):
    TELEGRAM = "telegram"


class MessageParseMode(StrEnum):
    MARKDOWN = "Markdown"
    HTML = "HTML"


class NotifyIn(BaseModel):
    """Схема уведомления.

    :target_id: int
    :message: str
    :source: SourceType = Field(SourceType.TELEGRAM)
    """

    target_id: int
    message: str
    format: MessageParseMode | None = None
    source: SourceType = Field(SourceType.TELEGRAM)


class NotifyRedisDto(BaseModel):
    target_id: int
    message: str
    format: MessageParseMode | None = None
    bot_token: str
    timestamp: float
