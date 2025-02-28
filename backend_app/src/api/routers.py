from fastapi import APIRouter

from api.notify_api import router as notify_router

router = APIRouter()

router.include_router(notify_router)
