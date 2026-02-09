from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.utility import get_current_user
from config import Config
from app.services.dify import DifyService
from app.schemas.request import (
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
async def get_summary(
    req: DifySummaryRequest,
):
    try:
        dify_service = DifyService(config)

        res = dify_service.get_summary(req, "mrowlvi@gmail.com")
        
        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/test-summary")
async def test_summary(
    req: DifySummaryRequest,
    current_user: UserRequest = Depends(get_current_user) 
):
    try:
        dify_service = DifyService(config)
        background_tasks.add_task(dify_service.get_summary, req, current_user.email_address)
        res = {"message": "Summary request is being processed in the background."}

        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))