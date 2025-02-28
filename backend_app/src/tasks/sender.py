import logging

from faststream import FastStream
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitQueue,
)
from pydantic import Json

from application.notification_service import (
    NotificationService,
)
from core.config import settings
from schemas.notify_schema import NotifyRedisDto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.rabbitmq_url)

app = FastStream(broker)

exch = RabbitExchange("exchange", auto_delete=True, type=ExchangeType.TOPIC)
queue_1 = RabbitQueue("telegram:messages", auto_delete=True)


@broker.subscriber(queue_1, exch)
async def base_handler1(msg: Json[NotifyRedisDto]) -> None:
    await NotificationService().send(
        chat_id=msg.target_id,
        bot_token=msg.bot_token,
        message=msg.message,
        parse_mode=msg.format,
    )


async def main() -> None:
    await app.run()
