from contextlib import asynccontextmanager

from fastapi import (
    APIRouter,
    FastAPI,
)
from tortoise.contrib.fastapi import register_tortoise

from api.routers import router as main_router
from core.config import settings
from infra.redis_client import RedisClient

router = APIRouter(prefix="/api")

router.include_router(main_router)


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


register_tortoise(
    app=app,
    config=settings.tortoise_config,
    modules={"models": ["infra.database.models"]},
    add_exception_handlers=True,
)
