from fastapi import APIRouter, HTTPException, status
from app.services.user_service import UserService
from app.schemas.user_schema import UserLoginRequest, UserResponse
from typing import Dict, Any

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

user_service = UserService()

@router.get("/profile", response_model=UserResponse)
async def profile(
    provider: str,
    token_data: Dict[str, Any]
):
    try:
        return user_service.profile(provider, token_data)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))




