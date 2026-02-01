
from fastapi import HTTPException
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from app.services.dify import DifyService
from config import Config
from typing import Dict, Any
from app.utility import clean_html
from database import Database

from app.schemas.email import (
    EmailFetchRequest, EmailMessageRequest, EmailSummaryRequest, 
    DifySummaryRequest,AttachmentRequest,GetRequest,
    MessageIdRequest, MessageBatchDeleteRequest
)

from app.schemas.category import (
    CreateLabelRequest, MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    GetLabelRequest
)

class EmailService:
    def __init__(self, config: Config):
        self.config = config

    def initialize_labels(self, req: GetRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.initialize_labels(req)

        return res
    
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

        db = Database(self.config)
        db.insert("emails", req.dict())

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

    def get_labels(self, req: GetRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_labels(req)

        return res
    
    def get_user_profile(self, req: GetRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_user_profile(req)

        return res
    
    def get_attachments(self, req: AttachmentRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_attachments(req)

        return res
    
    def create_label(self, req: CreateLabelRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.create_label(req)

        return res
    
    def get_label_by_id(self, req: GetLabelRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_label_by_id(req)

        return res
    
    def message_modify_label(self, req: MessageModifyLabelRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_modify_label(req)

        return res

    def message_batch_modify_label(self, req: MessageBatchModifyLabelRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_batch_modify_label(req)

        return res

    def message_delete(self, req: MessageIdRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_delete(req)

        return res

    def message_batch_delete(self, req: MessageBatchDeleteRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_batch_delete(req)

        return res
    
    def message_trash(self, req: MessageIdRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_trash(req)

        return res

    def message_untrash(self, req: MessageIdRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_untrash(req)

        return res