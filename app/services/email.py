from typing import List
from app import utility
from app.schemas.category import Category
from app.schemas.email import Draft, Format, Message
from app.schemas.response import CategoryListResponse, MessagesResponse
from config import Config
from database import SupabaseDB
from fastapi import HTTPException
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI

from app.schemas.request import (
    EmailFetchRequest,
    MessageIdRequest,
    MessageBatchDeleteRequest,
    CreateLabelRequest,
    MessageModifyLabelRequest,
    MessageBatchModifyLabelRequest,
    SyncLabelsRequest,
    UserRequest,
    CreateDraftRequest,
)
from app.schemas.query import DraftsQueryParams, MessageParam, MessagesParam


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

    def fetch_emails(self, param: MessagesParam, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        res = provider_service.fetch_emails(param, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=404, detail="Fetch MessageIDs not found")
        return res

    def get_message_batch(
        self,
        msgs: MessagesResponse,
        current_user: UserRequest,
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        param = MessageParam(
            format="metadata", metadataHeaders=["Date", "From", "Subject", "To"]
        )
        res = provider_service.get_message_batch(
            msgs.messages, param, current_user, self.db
        )
        if res is None:
            raise HTTPException(status_code=404, detail=f"Messages not found")

        return MessagesResponse(
            messages=res,
            nextPageToken=msgs.nextPageToken,
            resultSizeEstimate=msgs.resultSizeEstimate,
        )

    def get_message_by_id(
        self, msg_id: str, param: MessageParam, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_message_by_id(msg_id, param, current_user, self.db)
        if res is None:
            raise HTTPException(
                status_code=404, detail=f"Message with id {msg_id} not found"
            )
        body_html = utility.get_part_by_mimetype(res["payload"], "text/html")
        body_plain = utility.get_part_by_mimetype(res["payload"], "text/plain")

        if body_html is None:
            text_html = ""
        else:
            text_html = utility.decode_base64(body_html["body"]["data"])

        if body_plain is None:
            body_plain = utility.get_part_by_mimetype(res["payload"], "text/html")
            if body_plain is None:
                raise HTTPException(
                    status_code=404, detail="Message text or html body not found"
                )
            text_plain = utility.clean_html(
                utility.decode_base64(body_plain["body"]["data"])
            )
        else:
            text_plain = utility.decode_base64(body_plain["body"]["data"])
            text_plain = utility.clean_text(text_plain)

        res["text_plain"] = text_plain
        res["text_html"] = text_html

        return Message(**res)

    def get_labels(self, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_labels(current_user, self.db)
        if res is None:
            raise HTTPException(status_code=404, detail="Labels not found")

        return CategoryListResponse(**res)

    def get_attachments(
        self, msg_id: str, attachment_id: str, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_attachments(
            msg_id, attachment_id, current_user, self.db
        )

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

    def sync_labels(self, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.sync_labels(current_user, self.db)
        if res is None:
            raise HTTPException(status_code=404, detail="Labels sync failed")
        return CategoryListResponse(**res)

    def get_label_by_id(self, label_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_label_by_id(label_id, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=404, detail="Label not found")

        return Category(**res)

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

    def message_modify_label(
        self, req: MessageModifyLabelRequest, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_modify_label(req, current_user, self.db)

        return res

    def message_batch_modify_label(
        self, req: MessageBatchModifyLabelRequest, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_batch_modify_label(req, current_user, self.db)

        return res

    def message_delete(self, msg_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_delete(msg_id, current_user, self.db)

        return res

    def message_batch_delete(
        self, req: MessageBatchDeleteRequest, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_batch_delete(req, current_user, self.db)

        return res

    def message_trash(self, msg_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_trash(msg_id, current_user, self.db)

        return res

    def message_untrash(self, msg_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_untrash(msg_id, current_user, self.db)

        return res

    def update_message_labels(
        self, msg_id: str, label_id: str, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        req = MessageModifyLabelRequest(
            id=msg_id, addLabelIds=[label_id], removeLabelIds=[]
        )
        provider_service.message_modify_label(req, current_user, self.db)

        return

    def create_draft(self, req: CreateDraftRequest, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.create_draft(req, current_user, self.db)

        if res is None:
            raise HTTPException(status_code=400, detail=f"Error creating draft :{res}")

        return Draft(**res)

    def delete_draft(self, draft_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.delete_draft(draft_id, current_user, self.db)

        return res

    def get_draft(
        self, draft_id: str, current_user: UserRequest, format: str = Format.FULL.value
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_draft(draft_id, current_user, self.db, format)

        return res

    def get_drafts(self, params: DraftsQueryParams, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_drafts(params, current_user, self.db)

        return res

    def draft_send(self):
        pass

    def update_draft(
        self, draft_id: str, req: CreateDraftRequest, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.update_draft(draft_id, req, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=400, detail=f"Error updating draft :{res}")

        return Draft(**res)

    def send_draft(self, draft_id: str, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.send_draft(draft_id, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=400, detail=f"Error sending draft :{res}")

        return Message(**res)
