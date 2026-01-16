
from fastapi import HTTPException
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from app.services.dify import DifyService
from config import Config
from typing import Dict, Any
from app.utility import clean_html

from app.schemas.email import (
    EmailFetchRequest, 
    EmailMessageRequest, 
    EmailSummaryRequest, 
    DifySummaryRequest
)

class EmailService:
    def __init__(self, config: Config):
        self.config = config
    
    def fetch_emails(self, req: EmailFetchRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        res = provider_service.fetch_emails(req)
        
        return res
    
    def get_message_by_id(self, req: EmailMessageRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_message_by_id(req)

        return res
    
    def get_summary(self, req: EmailSummaryRequest):

        dify_service = DifyService(self.config)
        req = DifySummaryRequest(
            inputs=EmailSummaryRequest(email_text=req.email_text),
            user="frontend-test",
            response_mode="blocking"
        )

        return dify_service.get_summary(req)

    def get_plain_text(self, req: EmailFetchRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_plain_text(req)

        return res