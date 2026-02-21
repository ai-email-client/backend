from typing import List, Dict, Any
from imap_tools import MailBox
from app.schemas.request import (
    EmailFetchRequest, 
    MessageIdRequest, MessageBatchDeleteRequest,
    CreateLabelRequest, MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    GetLabelRequest, SyncLabelsRequest,UserRequest,DraftCreateRequest
)
from database import SupabaseDB
from config import Config

class OutlookAPI:
    def __init__(self, config: Config):
        self.config = config

    def initialize_labels(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def fetch_emails(self, req: EmailFetchRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_stored_credentials(self, email_address: str, db: SupabaseDB):
        pass

    def get_user_info(self, creds):
        pass
    
    def get_message_by_id(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_labels(self, current_user: UserRequest , db: SupabaseDB):
        pass

    def get_user_profile(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_attachments(self, msg_id: str, attachment_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def create_label(self, req: CreateLabelRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def sync_labels(self, req: SyncLabelsRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_label_by_id(self, label_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_label_by_name(self, label_name: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_modify_label(self, req: MessageModifyLabelRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_batch_modify_label(self, req: MessageBatchModifyLabelRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_delete(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_batch_delete(self, req: MessageBatchDeleteRequest, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_trash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_untrash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def create_draft(self, req: DraftCreateRequest, current_user: UserRequest, db: SupabaseDB):
        pass
    
