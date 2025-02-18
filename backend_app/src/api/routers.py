from fastapi import APIRouter

from api.user_api import router as user_router

router = APIRouter()

router.include_router(user_router)
