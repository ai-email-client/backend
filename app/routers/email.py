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
    EmailFetchRequest: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        return email_service.fetch_emails(EmailFetchRequest)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def get_message_by_id(
    EmailMessageRequest: EmailMessageRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_message_by_id(EmailMessageRequest)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.get("/inbox")
async def get_inbox(
    EmailFetchRequest: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_inbox(EmailFetchRequest)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/summary")
async def get_summary(
    EmailSummaryRequest: EmailSummaryRequest
):
    try:
        email_service = EmailService(config)

        return email_service.get_summary(EmailSummaryRequest)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))