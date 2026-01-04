from fastapi import APIRouter, HTTPException, Body
from app.providers.gmail import GmailProvider
from config import Config
from typing import Dict, Any
from app.schemas.email import EmailFetchRequest, EmailMessageRequest

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
        if EmailFetchRequest.provider == "gmail":
            provider_service = GmailProvider(config)
        elif EmailFetchRequest.provider == "outlook":
            provider_service = OutlookProvider(config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        if EmailFetchRequest.limit is None:
            limit = 5
        else:
            limit = EmailFetchRequest.limit

        emails = provider_service.fetch_emails(EmailFetchRequest)
        
        return {"count": len(emails), "emails": emails}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def get_message_by_id(
    EmailMessageRequest: EmailMessageRequest
):
    try:
        if EmailMessageRequest.provider == "gmail":
            provider_service = GmailProvider(config)
        elif EmailMessageRequest.provider == "outlook":
            provider_service = OutlookProvider(config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        message = provider_service.get_message_by_id(EmailMessageRequest)
        
        return message
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inbox")
async def get_inbox(
    EmailFetchRequest: EmailFetchRequest
):
    try:
        if EmailFetchRequest.provider == "gmail":
            provider_service = GmailProvider(config)
        elif EmailFetchRequest.provider == "outlook":
            provider_service = OutlookProvider(config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        inbox = provider_service.get_inbox(EmailFetchRequest)
        
        return inbox
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))