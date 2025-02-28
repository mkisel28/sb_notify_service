import logging

import httpx

from schemas.notify_schema import MessageParseMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    async def send(
        self,
        chat_id: int,
        message: str,
        bot_token: str,
        parse_mode: MessageParseMode | None,
    ) -> None:
        """Отправка сообщения в Telegram."""
        await self._send_telegram_message(
            chat_id,
            bot_token,
            message,
            parse_mode,
        )

    async def _send_telegram_message(
        self,
        chat_id: int,
        bot_token: str,
        message: str,
        parse_mode: MessageParseMode | None,
    ) -> None:
        """Отправка сообщения в Telegram."""
        payload = {
            "chat_id": chat_id,
            "text": message,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.post(api_url, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.info(
                    f"Ошибка при отправке сообщения: {e.response.status_code} {e.response.text}",
                )
            except httpx.RequestError as e:
                logger.info(f"Ошибка соединения с Telegram API: {e}")
