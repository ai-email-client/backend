from fastapi import APIRouter, HTTPException, Depends
from config import Config
from app.services.database import DatabaseService
from app.schemas.request import (
    UserRequest
)
from dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/database",
    tags=["database"]
)

@router.get("/get-summary/{msg_id}")
async def get_summary(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_db)
):
    try:
        res = service.get_summary(msg_id, current_user.email_address)

        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-user-pin")
async def get_user_pin(
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_db)
):
    try:
        res = service.get_user_pin(current_user.email_address)
        if res is None:
            raise HTTPException(status_code=404, detail="PIN not found for user")

        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e)
)