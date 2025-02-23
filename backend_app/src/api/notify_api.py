import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import (
    get_redis_client,
    verify_api_key,
)
from infra.database.models.api_key import APIKey
from infra.redis_client import RedisClient
from schemas.notify_schema import NotifyIn, NotifyRedisDto

router = APIRouter(prefix="/notify")


@router.post("")
async def notify(
    notify_data: NotifyIn,
    api_key: Annotated[APIKey, Depends(verify_api_key)],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
):
    key = f"notification:{notify_data.target_id}:{api_key.bot.token}"

    notify_redis_dto = NotifyRedisDto(
        **notify_data.model_dump(),
        bot_token=api_key.bot.token,
        timestamp=datetime.now(UTC).timestamp(),
    )

    await redis_client.add_to_list(
        key,
        json.dumps(notify_redis_dto.model_dump()),
    )

    return "kek"
