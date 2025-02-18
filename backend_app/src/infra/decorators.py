from __future__ import annotations

from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar

from tenacity import retry, stop_after_attempt, wait_fixed

T = TypeVar("T")


def retry_on_failure(
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    @wraps(func)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_fixed(2),
    )
    async def wrapper(*args, **kwargs) -> T:
        return await func(*args, **kwargs)

    return wrapper
