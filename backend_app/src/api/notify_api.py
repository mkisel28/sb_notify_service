from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_notification_service, verify_api_key
from application.notification_service import NotificationService
from infra.database.models.api_key import APIKey
from schemas.notify_schema import NotifyIn

router = APIRouter(prefix="/notify")


@router.post("")
async def notify(
    notify_data: NotifyIn,
    api_key: Annotated[APIKey, Depends(verify_api_key)],
    notification_service: Annotated[
        NotificationService,
        Depends(get_notification_service),
    ],
):
    result = await notification_service.send(
        notify_data.target_id,
        notify_data.message,
        api_key.bot.token,
        notify_data.format,
    )

    return "OK"
