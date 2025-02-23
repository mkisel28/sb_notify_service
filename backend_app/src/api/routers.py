from fastapi import APIRouter

from api.notify_api import router as notify_router
from api.user_api import router as user_router

router = APIRouter()

router.include_router(user_router)
router.include_router(notify_router)
