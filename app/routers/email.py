from fastapi import APIRouter, HTTPException, Body
from config import Config
from typing import Dict, Any
from app.schemas.email import EmailFetchRequest, EmailMessageRequest, EmailSummaryRequest
from app.services.email import EmailService

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

config = Config()

@router.post("/fetch")
async def fetch_emails(
    req: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        return email_service.fetch_emails(req)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def get_message_by_id(
    req: EmailMessageRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_message_by_id(req)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.get("/inbox")
async def get_inbox(
    req: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_inbox(req)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/summary")
async def get_summary(
    req: EmailSummaryRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_summary(req)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))