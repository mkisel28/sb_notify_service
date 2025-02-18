from fastapi import APIRouter

from infra.database.models.user import User

router = APIRouter(prefix="/users")

@router.get("")
async def get_users(): 
  users_result = await User.all()

  if users_result is None:
      return "qwe: qwe"
  
  return users_result