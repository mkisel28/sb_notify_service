from __future__ import annotations

from collections.abc import AsyncGenerator

import redis.asyncio as redis

from infra.decorators import retry_on_failure


class RedisClient:
    """Асинхронный клиент Redis с поддержкой DSN и расширенными параметрами."""

    def __init__(self, dsn: str, *, decode_responses: bool = True) -> None:
        """Инициализирует клиент Redis.

        :param dsn: DSN строка подключения (например, "redis://localhost:6379/0")
        :param decode_responses: Флаг декодирования ответов Redis в строки \
            (по умолчанию True)
        """
        self._dsn = dsn
        self._decode_responses = decode_responses
        self._redis: redis.Redis | None = None

    @retry_on_failure
    async def connect(self):
        """Устанавливает подключение к Redis."""
        if not self._redis:
            self._redis = redis.from_url(
                self._dsn,
                decode_responses=self._decode_responses,
            )

    async def disconnect(self):
        """Закрывает подключение к Redis."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def set_value(
        self,
        key: str,
        value: str,
        expire: int | None = None,
        **kwargs,  # noqa: ANN003
    ) -> None:
        """Устанавливает ключ-значение в Redis.

        :param key: Ключ
        :param value: Значение
        :param expire: Время жизни ключа в секундах (если не указано, \
            ключ бессрочный).
        :param kwargs: Дополнительные параметры (например, nx=True, px=1000)
        """
        redis_con = await self._get_redis_connection()
        await redis_con.set(key, value, ex=expire, **kwargs)

    async def get_value(self, key: str) -> str | None:
        """Возвращает значение ключа из Redis.

        :param key: Ключ.
        :return: Значение или None, если ключ не существует.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.get(key)

    async def delete_key(self, key: str):
        """Удаляет ключ из Redis.

        :param key: Ключ для удаления.
        """
        redis_con = await self._get_redis_connection()
        await redis_con.delete(key)

    async def is_key_exists(self, key: str) -> bool:
        """Проверяет, существует ли ключ в Redis.

        :param key: Ключ
        :return: True, если ключ существует, иначе False.
        """
        redis_con = await self._get_redis_connection()
        return bool(await redis_con.exists(key))

    async def flush(self, **kwargs) -> None:  # noqa: ANN003
        """Удаляет все ключи в текущей базе данных Redis.

        :param kwargs: Дополнительные параметры (например, `asynchronous=True`)
        """
        redis_con = await self._get_redis_connection()
        await redis_con.flushdb(**kwargs)

    async def incr_key(
        self,
        key: str,
        amount: int = 1,
        ttl: int | None = None,
    ) -> int:
        """Увеличивает значение ключа на указанное число.

        :param key: Ключ.
        :param amount: Число, на которое увеличивается значение (по умолчанию 1).
        :param ttl: Время жизни ключа в секундах (если установлено).
        :return: Новое значение после инкремента.
        """
        redis_con = await self._get_redis_connection()
        value = await redis_con.incr(key, amount)

        if ttl and (await redis_con.ttl(key)) == -1:
            await redis_con.expire(key, ttl)

        return value

    async def decr_key(
        self,
        key: str,
        amount: int = 1,
        ttl: int | None = None,
    ) -> int:
        """Уменьшает значение ключа на указанное число.

        :param key: Ключ.
        :param amount: Число, на которое уменьшается значение (по умолчанию 1).
        :param ttl: Время жизни ключа в секундах (если установлено).
        :return: Новое значение после декремента.
        """
        redis_con = await self._get_redis_connection()
        value = await redis_con.decr(key, amount)

        if ttl and (await redis_con.ttl(key)) == -1:
            await redis_con.expire(key, ttl)

        return value

    async def set_ttl(self, key: str, seconds: int, **kwargs) -> bool:  # noqa: ANN003
        """Устанавливает срок жизни ключа.

        :param key: Ключ.
        :param seconds: Время жизни ключа в секундах.
        :param kwargs: Дополнительные параметры.
        :return: True, если срок жизни был установлен, иначе False.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.expire(key, seconds, **kwargs)

    async def get_ttl(self, key: str) -> int:
        """Возвращает оставшееся время жизни ключа.

        :param key: Ключ.
        :return: Время жизни в секундах или -1, если ключ бессрочный.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.ttl(key)

    async def find_keys(self, pattern: str) -> list[str]:
        """Возвращает список ключей, соответствующих шаблону.

        :param pattern: Шаблон поиска (например, `"user:*"`).
        :return: Список ключей.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.keys(pattern)

    async def add_to_set(
        self,
        key: str,
        *values: str,
        ttl: int | None = None,
    ) -> None:
        """Добавляет один или несколько элементов в множество (set) в Redis.

        :param key: Ключ множества.
        :param values: Один или несколько элементов для добавления.
        :param ttl: Время жизни множества в секундах (если указано).
        """
        redis_con = await self._get_redis_connection()
        await redis_con.sadd(key, *values)  # type: ignore [await]
        if ttl:
            await redis_con.expire(key, ttl)

    async def remove_from_set(self, key: str, *values: str) -> None:
        """Удаляет элементы из множества.

        :param key: Ключ множества.
        :param values: Один или несколько элементов для удаления.
        """
        redis_con = await self._get_redis_connection()
        await redis_con.srem(key, *values)  # type: ignore [await]

    async def is_member_of_set(self, key: str, value: str) -> bool:
        """Проверяет, является ли элемент членом множества.

        :param key: Ключ множества.
        :param value: Элемент для проверки.
        :return: True, если элемент присутствует в множестве, иначе False.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.sismember(key, value)  # type: ignore [await]

    async def get_set_members(self, key: str) -> set[str]:
        """Возвращает все элементы множества.

        :param key: Ключ множества.
        :return: Множество элементов.
        """
        redis_con = await self._get_redis_connection()
        return await redis_con.smembers(key)  # type: ignore [await]

    async def add_to_list(
        self,
        key: str,
        *values: str,
        right: bool = True,
        ttl: int | None = None,
    ) -> None:
        """Добавляет один или несколько элементов в список (list).

        :param key: Ключ списка.
        :param values: Один или несколько элементов для добавления.
        :param right: Если True, добавляет элементы в конец списка (RPUSH),\
            иначе в начало (LPUSH).
        :param ttl: Время жизни списка в секундах (если указано).
        """
        redis_con = await self._get_redis_connection()

        if right:
            await redis_con.rpush(key, *values)  # type: ignore [await]
        else:
            await redis_con.lpush(key, *values)  # type: ignore [await]

        if ttl:
            await redis_con.expire(key, ttl)

    async def pop_from_list(
        self,
        key: str,
        count: int | None = None,
        *,
        right: bool = True,
        ttl: int | None = None,
    ) -> str | list[str] | None:
        """Извлекает элемент(ы) из списка.

        :param key: Ключ списка в Redis
        :param right: True - извлекает с конца (rpop), False - с начала (lpop)
        :param count: Количество элементов для извлечения (если None, то один)
        :param ttl: Время жизни ключа после удаления (если список пуст)
        :return: Один элемент или список элементов (если count > 1)
        """
        redis_con = await self._get_redis_connection()

        if right:
            result = await redis_con.rpop(key, count)  # type: ignore [await]
        else:
            result = await redis_con.lpop(key, count)  # type: ignore [await]

        if ttl and not await redis_con.exists(key):
            await redis_con.expire(key, ttl)

        return result

    async def get_list_range(
        self,
        key: str,
        start: int = 0,
        end: int = -1,
    ) -> list[str]:
        """Возвращает диапазон элементов списка.

        :param key: Ключ списка.
        :param start: Начальный индекс (по умолчанию 0).
        :param end: Конечный индекс (по умолчанию -1, что означает\
            последний элемент).
        :return: Список элементов в заданном диапазоне.
        """
        redis_client = await self._get_redis_connection()
        return await redis_client.lrange(key, start, end)  # type: ignore [await]

    async def publish_to_channel(self, channel: str, message: str) -> None:
        """Публикует сообщение в канал.

        :param channel: Название канала.
        :param message: Сообщение для публикации.
        """
        redis_client = await self._get_redis_connection()
        await redis_client.publish(channel, message)

    async def listen_to_channel(
        self,
        channel: str,
    ) -> AsyncGenerator[str]:
        """Подписывается на канал и слушает сообщения.

        :param channel: Название канала.
        :return: Генератор сообщений из канала.
        """
        redis_con = await self._get_redis_connection()
        async with redis_con.pubsub() as pubsub:
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield message["data"]

    async def get_client(self) -> redis.Redis:
        """Возвращает объект клиента Redis.

        :return: Объект `redis.Redis`, представляющий соединение.
        """
        return await self._get_redis_connection()

    async def _get_redis_connection(self) -> redis.Redis:
        """Возвращает текущее соединение с Redis, выполняя подключение при необходимости.

        :return: Объект `redis.Redis`.
        """
        while not self._redis:
            await self.connect()
        return self._redis
