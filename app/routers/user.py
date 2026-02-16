from fastapi import APIRouter, HTTPException
from app.services.user import UserService
from config import Config
from fastapi import Depends

from app.schemas.request import UserRequest

from dependencies import get_current_user,get_user_service

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/profile")
async def profile(
    req: UserRequest = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        res = user_service.get_user_profile(req)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@router.put("/setup-pin")
async def setup_pin(
    pin: str,
    req: UserRequest = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        res = user_service.setup_pin(req, pin)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

