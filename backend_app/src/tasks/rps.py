import asyncio
import functools
import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import BrokerWrapper, StreamScheduler

# Настроим логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Указываем настройки для RabbitMQ и Redis
RABBITMQ_URL = "amqp://user:password@rabbitmq:5672"
REDIS_URL = "redis://redis:6379"


def rate_limited_task(interval_seconds: int):
    """Декоратор для ограничения частоты выполнения цикла."""
    if interval_seconds <= 0:
        raise ValueError("times_per_minute должен быть больше 0")

    iteration = int(60 / interval_seconds)

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(iteration):
                await func(*args, **kwargs)
                await asyncio.sleep(interval_seconds)

        return wrapper

    return decorator


# Создаем брокер для RabbitMQ
broker = RabbitBroker(RABBITMQ_URL)

# Создаем приложение FastStream
app = FastStream(broker)

# Оборачиваем брокер в Taskiq для совместимости
taskiq_broker = BrokerWrapper(broker)


# Определим задачу для планирования
@rate_limited_task(30)
async def process_rps():
    logger.info(
        "Processing scheduled task... Sending message to the queue.",
    )
    # Публикуем сообщение в очередь
    await broker.publish(message="message piska", queue="pizda")
    logger.info("Message sent to queue.")


# Регистрация задачи для планирования с cron-выражением
taskiq_broker.task(
    message=process_rps,
    schedule=[
        {"cron": "* * * * *"},
    ],  # Задача будет запускаться каждую минуту
)


@broker.subscriber("pizda")
async def handle_message(message: str):
    logger.info(f"Received message from 'pizda' queue: {message}")
    # Здесь можно выполнить нужные действия с полученным сообщением
    logger.info(f"Message received: {message}")


# Создаем планировщик задач
scheduler = StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(taskiq_broker)],
)
