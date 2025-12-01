from fastapi import APIRouter, HTTPException, status
from app.services.user_service import UserService
from app.schemas.user_schema import UserLoginRequest

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_service = UserService()

@router.post("/login")
async def login(login_data: UserLoginRequest):
    try:
        result = user_service.login_email(login_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


