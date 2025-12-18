from fastapi import APIRouter, HTTPException, status
from app.services.user_service import UserService
from app.schemas.user_schema import UserLoginRequest

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_service = UserService()



