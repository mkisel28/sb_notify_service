from fastapi import APIRouter

from infra.database.models.user import User

router = APIRouter(prefix="/users")

@router.get("")
async def get_users():
  users_result = await User.all()

  if not users_result:
    return "Bla Bla"

  return users_result
