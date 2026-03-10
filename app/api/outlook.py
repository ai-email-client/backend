from typing import List, Dict, Any
from imap_tools import MailBox
from app.schemas.email import Format, MessageGmail
from app.schemas.request import (
    EmailFetchRequest,
    MessageIdRequest,
    MessageBatchDeleteRequest,
    CreateLabelRequest,
    MessageModifyLabelRequest,
    MessageBatchModifyLabelRequest,
    GetLabelRequest,
    SyncLabelsRequest,
    UserRequest,
    CreateDraftRequest,
)
from database import SupabaseDB
from config import Config
from app.schemas.query import DraftsQueryParams, MessageParam, MessagesParam


class OutlookAPI:
    def __init__(self, config: Config):
        self.config = config

    def initialize_labels(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def fetch_emails(
        self, param: MessagesParam, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def get_message_batch(
        self,
        msgs: List[MessageGmail],
        param: MessageParam,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        pass

    def get_authorization_url(self):
        return ""

    def get_credentials(self, authorization_code: str, state: str, db: SupabaseDB):
        pass

    def get_stored_credentials(self, email_address: str, db: SupabaseDB):
        pass

    def get_user_info(self, creds):
        pass

    def get_message_by_id(
        self,
        msg_id: str,
        param: MessageParam,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        pass

    def get_labels(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_user_profile(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_attachment(
        self, msg_id: str, attachment_id: str, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def create_label(
        self, req: CreateLabelRequest, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def sync_labels(self, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_label_by_id(self, label_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_label_by_name(
        self, label_name: str, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def message_modify_label(
        self, req: MessageModifyLabelRequest, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def message_batch_modify_label(
        self,
        req: MessageBatchModifyLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        pass

    def message_delete(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_batch_delete(
        self, req: MessageBatchDeleteRequest, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def message_trash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def message_untrash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def create_draft(
        self, req: CreateDraftRequest, current_user: UserRequest, db: SupabaseDB
    ):
        pass

    def delete_draft(self, draft_id: str, current_user: UserRequest, db: SupabaseDB):
        pass

    def get_draft(
        self, draft_id: str, current_user: UserRequest, db: SupabaseDB, format: str
    ):
        pass

    def get_drafts(
        self, params: DraftsQueryParams, current_user: UserRequest, db: SupabaseDB
    ):
        pass
    
    def get_draft_batch(self, drafts: list, current_user: UserRequest, db: SupabaseDB, params: DraftsQueryParams):
        pass

    def update_draft(
        self,
        draft_id: str,
        req: CreateDraftRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        pass

    def upload_draft(
        self,
        draft_id: str,
        req: CreateDraftRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        pass

    def send_draft(self, draft_id: str, current_user: UserRequest, db: SupabaseDB):
        pass
