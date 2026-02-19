from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.schemas.dify import Status
from app.services.dify import DifyService
from app.services.database import DatabaseService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest,
    UserRequest
)
from app.services.email import EmailService
from dependencies import get_current_user, get_dify_service, get_database_service, get_email_service

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
    email_service: EmailService = Depends(get_email_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:    
        is_summary = database_service.get_source_email(req.msg_id, current_user.email_address)
        if is_summary:
            temp = is_summary.model_dump()
            req = DataInsertSummaryRequest(**temp, current_user=current_user)
            is_have_summary = database_service.get_summary(is_summary.id)
            
            if is_summary.status == Status.done.value:
                print(f"Summary already exists for msg_id {req.msg_id}, fetching from database.", flush=True)
                email_service.update_message_labels(
                    msg_id=is_summary.msg_id, 
                    email_category=is_have_summary.email_category, 
                    current_user=current_user)
                
                return database_service.get_summary(is_summary.id)
            elif (is_summary.status == Status.new.value or is_summary.status == Status.error.value) and is_summary:
                
                background_tasks.add_task(dify_service.send_to_dify, req)
            else:
                print(f"Summary already being processed for {is_summary.id}, fetching from database.", flush=True)
                if is_have_summary is not None:
                    database_service.upsert_status(source_email_id=is_summary.id, status=Status.done.value)
                    return is_have_summary
        else:
            inserted = database_service.upsert_email_source(req=req, user_email=current_user.email_address)
            req = DataInsertSummaryRequest(**inserted[0], current_user=current_user)
            background_tasks.add_task(dify_service.send_to_dify, req)


        res = {"message": "Summary request is being processed in the background."}
        
        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

