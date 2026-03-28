from fastapi import APIRouter, HTTPException, Depends
from app.schemas.dify import Status
from app.services.database import DatabaseService
from app.schemas.request import (
    UserRequest
)
from dependencies import get_database_service, get_current_user

router = APIRouter(
    prefix="/database",
    tags=["database"]
)

@router.get("/get_summary/{msg_id}")
async def get_summary(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_database_service)
):
    try:
        source_email = service.get_source_email(msg_id, current_user.email_address)
        if source_email is None:
            return None
        res = service.get_summary(source_email.id)
        if res is None:
            return None

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))
    
@router.get("/get_source_email/{msg_id}")
async def get_source_email(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_database_service)
):
    try:
        res = service.get_source_email(msg_id, current_user.email_address)
        if res is None:
            raise HTTPException(status_code=404, detail="Source email not found for the given msg_id and user")

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-user-pin")
async def get_user_pin(
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_database_service)
):
    try:
        res = service.get_user_pin(current_user.email_address)
        if res is None:
            raise HTTPException(status_code=404, detail="PIN not found for user")

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e)
)
        
@router.post("/upsert_email_tags/{msg_id}")
async def upsert_email_tags(
    msg_id: str,
    email_tags: str,
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_database_service)
):
    try:
        source_email = service.get_source_email(msg_id, current_user.email_address)
        if source_email is None:
            raise HTTPException(status_code=404, detail="Source email not found for the given msg_id and user")
        
        res = service.upsert_email_tags(source_email.id, email_tags)

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))

@router.get("/check_summary/{msg_id}")
async def check_summary(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    service: DatabaseService = Depends(get_database_service)
):
    try:
        source_email = service.get_source_email(msg_id, current_user.email_address)
        if source_email is None or source_email.status != Status.done.value:
            return False

        return True
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_overview(
    current_user: UserRequest = Depends(get_current_user), 
    service: DatabaseService = Depends(get_database_service)
):
    try:
        res = service.get_overview(current_user.email_address)
        if res is None:
            raise HTTPException(status_code=404, detail="Overview not found for user")

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))

@router.get("/spam")
async def get_spam(
    current_user: UserRequest = Depends(get_current_user), 
    service: DatabaseService = Depends(get_database_service)
):
    try:
        res = service.get_spam(current_user.email_address)
        if res is None:
            raise HTTPException(status_code=404, detail="Spam not found for user")

        return res
    except Exception as e:
        
        return HTTPException(status_code=500, detail=str(e))