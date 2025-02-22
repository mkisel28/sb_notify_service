from infra.database.models.api_key import APIKey


class ApiKeyService:
    async def get_api_key(self, api_key: str) -> APIKey | None:
        return await APIKey.get_or_none(
            key=api_key,
            is_active=True,
        ).select_related("bot")
