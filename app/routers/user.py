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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/has_pin")
async def has_pin(
    req: UserRequest = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        res = user_service.has_pin(req)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/setup_pin")
async def setup_pin(
    pin: str,
    req: UserRequest = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user_service.setup_pin(req, pin)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify_pin")
async def verify_pin(
    pin: str,
    req: UserRequest = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    try:
        res = user_service.verify_pin(req, pin)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))