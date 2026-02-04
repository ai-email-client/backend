from fastapi import APIRouter, HTTPException, status
from app.services.user import UserService
from app.schemas.user import UserRequest
from typing import Dict, Any
from config import Config

from app.utility import get_current_user
from fastapi import Depends

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

config = Config()
user_service = UserService(config)

@router.get("/profile")
async def profile(
    req: UserRequest = Depends(get_current_user)
):
    try:
        res = user_service.get_user_profile(req)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))



