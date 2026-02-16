from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.services.database import DatabaseService
from app.utility import get_current_user
from config import Config
from app.services.dify import DifyService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest,
    UserRequest
)

router = APIRouter(
    prefix="/dify",
    tags=["dify"]
)

config = Config()
background_tasks = BackgroundTasks()

@router.post("/summary")
async def set_summary(
    req: DifySummaryRequest,
    current_user: UserRequest = Depends(get_current_user) 
):
    try:
        dify_service = DifyService(config)
        database_service = DatabaseService(config)
        
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

