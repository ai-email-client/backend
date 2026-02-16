import time
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.schemas.dify import Status
from app.services.dify import DifyService
from app.services.database import DatabaseService
from config import Config
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


@router.post("/summary")
async def set_summary(
    req: DifySummaryRequest,
    current_user: UserRequest = Depends(get_current_user),
    dify_service: DifyService = Depends(get_dify_service),
    database_service: DatabaseService = Depends(get_database_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:    
        is_summary = database_service.get_source_email(req.msg_id, current_user.email_address)
        if is_summary:
            if is_summary.status == Status.done.value:
                print(f"Summary already exists for msg_id {req.msg_id}, fetching from database.", flush=True)
                return database_service.get_summary(is_summary.id)
            elif (is_summary.status == Status.new.value or is_summary.status == Status.error.value) and is_summary:
                temp = is_summary.model_dump()
                req = DataInsertSummaryRequest(**temp)
                time.sleep(5)
                background_tasks.add_task(dify_service.send_to_dify, req)
                print(f"Summary request is being processed in the background.", flush=True)
        else:
            inserted = database_service.insert_source_email(req=req, user_email=current_user.email_address)
            req = DataInsertSummaryRequest(**inserted[0])
            time.sleep(5)
            background_tasks.add_task(dify_service.send_to_dify, req)
            print(f"Summary request is being processed in the background.", flush=True)


        res = {"message": "Summary request is being processed in the background."}
        
        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

