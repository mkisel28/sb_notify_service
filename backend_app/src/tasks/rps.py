import logging
from contextlib import asynccontextmanager

from aioclock import AioClock, Depends, Every
from aioclock.group import Group
from faststream.rabbit import RabbitBroker
from core.config import settings
from infra.redis_client import RedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.rabbitmq_url)
tasks = Group()


class Dependencies:
    redis_client: RedisClient | None = None

    @classmethod
    async def get_redis(cls) -> RedisClient:
        """Возвращает инстанс Redis-клиента."""
        if cls.redis_client is None:
            raise RuntimeError("RedisClient не инициализирован")
        return cls.redis_client


@tasks.task(trigger=Every(seconds=5))
async def process_rps(redis: RedisClient = Depends(Dependencies.get_redis)):
    """Периодическая задача, публикующая сообщение в очередь и работающая с Redis."""
    logger.info("Processing scheduled task... Sending message to the queue.")

    keys = await redis.get_all_keys(match="notification:*", count=100)

    for key in keys:
        messages = await redis.pop_from_list(key=key, count=5, right=False)

        if not messages:
            continue

        if isinstance(messages, list):
            for m in messages:
                await broker.publish(message=m, queue="telegram:messages")
        else:
            await broker.publish(message=messages, queue="telegram:messages")

    logger.info("Message sent to queue.")


@asynccontextmanager
async def lifespan(aio_clock: AioClock):
    """Логика старта и остановки планировщика и брокера."""
    logger.info("Starting FastStream broker and AioClock scheduler...")

    Dependencies.redis_client = RedisClient(
        settings.redis_dsn,
    )
    await Dependencies.redis_client.connect()

    async with broker:
        yield aio_clock

    await Dependencies.redis_client.disconnect()
    Dependencies.redis_client = None
    logger.info("Stopping FastStream broker and AioClock scheduler...")


clock = AioClock(lifespan=lifespan)
clock.include_group(tasks)


async def main():
    await clock.serve()
