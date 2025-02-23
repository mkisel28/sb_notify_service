from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from application.api_key_service import ApiKeyService
from application.notification_service import NotificationService
from infra.database.models.api_key import APIKey

header_scheme = APIKeyHeader(name="x-api-key")


def get_api_key_service() -> ApiKeyService:
    return ApiKeyService()


def get_notification_service() -> NotificationService:
    return NotificationService()


async def verify_api_key(
    key: Annotated[str, Depends(header_scheme)],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
) -> APIKey:
    api_key = await api_key_service.get_api_key(key)

    if not api_key:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Not authenticated")

    return api_key
