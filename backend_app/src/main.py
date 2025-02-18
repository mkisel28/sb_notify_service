from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Request,
)
from fastapi.responses import StreamingResponse

from core.config import settings
from infra.redis_client import RedisClient

router = APIRouter(prefix="/api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = RedisClient(settings.redis_dsn)
    await redis_client.connect()
    app.state.redis_client = redis_client
    yield
    await redis_client.disconnect()


app = FastAPI(
    routes=router.routes,
    root_path="/notifications_service",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


def get_redis_client(request: Request) -> RedisClient:
    return request.app.state.redis_client


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/get")
async def get_value(
    key: str,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> str | None:
    return await redis_client.get_value(key)


@app.post("/set")
async def set_value(
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
    key: str,
    value: str,
    expire: int | None = None,
) -> None:
    await redis_client.set_value(key, value, expire)


@app.post("/add-to-list")
async def add_to_list(
    key: str,
    values: list[str],
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> None:
    await redis_client.add_to_list(key, *values)


@app.get("/get-list")
async def get_list(
    key: str,
    from_index: int,
    to_index: int,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> list[str]:
    return await redis_client.get_list_range(key, from_index, to_index)


@app.post("/publish-message")
async def publish_message(
    channel: str,
    message: str,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> None:
    await redis_client.publish_to_channel(channel, message)


@app.get("/subscribe/{channel}")
async def subscribe_to_channel(
    channel: str,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)],
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        async for message in redis_client.listen_to_channel(channel):
            yield f"data: {message}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
