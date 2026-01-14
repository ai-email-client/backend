
from fastapi import HTTPException
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from config import Config
from typing import Dict, Any

from app.schemas.email import EmailFetchRequest, EmailMessageRequest, EmailSummaryRequest

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
        print(res)
        return res
    
    def get_message_by_id(self, req: EmailMessageRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        return provider_service.get_message_by_id(req)
    
    def get_inbox(self, req: EmailFetchRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
    
    def get_summary(self, req: EmailMessageRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        return provider_service.get_summary(req)