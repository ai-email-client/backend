
from config import Config
from database import SupabaseDB
from fastapi import HTTPException
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI

from app.schemas.request import (
    EmailFetchRequest, EmailMessageRequest, 
    AttachmentRequest,
    MessageIdRequest, MessageBatchDeleteRequest,
    CreateLabelRequest, MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    GetLabelRequest, SyncLabelsRequest,UserRequest,DraftCreateRequest
)

class EmailService:
    def __init__(self, config: Config, db: SupabaseDB):
        self.config = config
        self.db = db

    def initialize_labels(self, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.initialize_labels(current_user, self.db)

        return res
    
    def fetch_emails(self, req: EmailFetchRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        res = provider_service.fetch_emails(req, current_user, self.db)
        return res
    
    def get_message_by_id(self, req: EmailMessageRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_message_by_id(req, current_user, self.db)

        return res

    def get_labels(self, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_labels(current_user, self.db)

        return res

    def get_attachments(self, req: AttachmentRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_attachments(req, current_user, self.db)

        return res
    
    def create_label(self, req: CreateLabelRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.create_label(req, current_user, self.db)

        return res
    
    def sync_labels(self, req: SyncLabelsRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.sync_labels(req, current_user, self.db)

        return res
    
    def get_label_by_id(self, label_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_label_by_id(label_id, current_user, self.db)

        return res
    
    def get_label_by_name(self, label_name: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_label_by_name(label_name, current_user, self.db)
        
        if res is None:
            res = provider_service.get_label_by_name("other", current_user, self.db)
            
        if res is None:
            raise Exception(f"Labels not found for name {label_name}")
        return res
    
    def message_modify_label(self, req: MessageModifyLabelRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_modify_label(req, current_user, self.db)

        return res

    def message_batch_modify_label(self, req: MessageBatchModifyLabelRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_batch_modify_label(req, current_user, self.db)

        return res

    def message_delete(self, req: MessageIdRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_delete(req, current_user, self.db)

        return res

    def message_batch_delete(self, req: MessageBatchDeleteRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_batch_delete(req, current_user, self.db)

        return res
    
    def message_trash(self, req: MessageIdRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_trash(req, current_user, self.db)

        return res

    def message_untrash(self, req: MessageIdRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.message_untrash(req, current_user, self.db)

        return res
    
    def update_message_labels(self, msg_id: str, label_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        req = MessageModifyLabelRequest(
            id=msg_id,
            addLabelIds=[label_id], 
            removeLabelIds=[]
            )
        provider_service.message_modify_label(req, current_user, self.db)

        return
    
    def draft_create(
        self,
        req: DraftCreateRequest,
        current_user: UserRequest
    ):
        pass
    
    def draft_delete():
        pass
    
    def draft_get():
        pass
    
    def draft_list():
        pass
    
    def draft_send():
        pass
    
    def draft_update():
        pass