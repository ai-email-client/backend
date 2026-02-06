from fastapi import APIRouter, HTTPException
from config import Config
from app.services.dify import DifyService
from app.schemas.dify import DifySummaryRequest

router = APIRouter(
    prefix="/dify",
    tags=["dify"]
)

config = Config()

@router.post("/summary")
async def get_summary(
    req: DifySummaryRequest
):
    try:
        dify_service = DifyService(config)

        res = dify_service.get_summary(req)

        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/test-summary")
async def test_summary(
    req: DifySummaryRequest
):
    try:
        dify_service = DifyService(config)

        res = dify_service.get_summary(req)

        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))