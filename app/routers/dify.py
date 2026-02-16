from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from config import Config
from app.services.dify import DifyService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest,
    UserRequest
)
from dependencies import get_current_user, get_dify_service, get_database_service

router = APIRouter(
    prefix="/dify",
    tags=["dify"]
)

background_tasks = BackgroundTasks()

@router.post("/summary")
async def set_summary(
    req: DifySummaryRequest,
    current_user: UserRequest = Depends(get_current_user),
    dify_service: DifyService = Depends(get_dify_service),
    database_service = Depends(get_database_service)
):
    try:    
           
        is_summary = database_service.get_summary(req.msg_id, current_user.email_address)
        if  is_summary is not None:
            return is_summary
        else:
            is_inserted = database_service.get_email_source(req=req, user_email=current_user.email_address)
            if not is_inserted:
                is_inserted = database_service.insert_source_email(req=req, user_email=current_user.email_address)
            req = DataInsertSummaryRequest(**is_inserted[0])
            background_tasks.add_task(dify_service.send_to_dify, req)

        res = {"message": "Summary request is being processed in the background."}
        
        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

