from typing import List
from app.schemas.category import Category
from app.schemas.email import AttachmentData, Draft, Format, MessageGmail, Message
from app.schemas.response import CategoryListResponse, MessagesResponse
from config import Config
from database import SupabaseDB
from fastapi import HTTPException
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI

from app.email_parser import (
    parse_message_by_payload
)
from app.schemas.request import (
    MessageBatchDeleteRequest,
    CreateLabelRequest,
    MessageModifyLabelRequest,
    MessageBatchModifyLabelRequest,
    UserRequest,
    CreateDraftRequest,
)
from app.schemas.response import DraftsResposnse
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

    def get_messages(self, param: MessagesParam, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        res = provider_service.get_messages(param, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=404, detail="Fetch messages failed")
        messages: List[Message] = []
        nextPageToken = res.get("nextPageToken", None)
        resultSizeEstimate = res.get("resultSizeEstimate", 0)
        for msg in res["messages"]:
            if param.format == Format.FULL:
                msg = parse_message_by_payload(msg)
            elif param.format == Format.RAW:
                pass
            elif param.format == Format.METADATA:
                pass
            elif param.format == Format.MINIMAL:
                pass
            messages.append(msg)
        return MessagesResponse(
            messages=messages,
            nextPageToken=nextPageToken,
            resultSizeEstimate=resultSizeEstimate,
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
        if param.format == Format.FULL:
            res = parse_message_by_payload(res)
        elif param.format == Format.RAW:
            pass
        elif param.format == Format.METADATA:
            pass
        elif param.format == Format.MINIMAL:
            pass
        
        return res

    def get_labels(
        self, current_user: UserRequest
    ):
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

    def get_attachment(
        self, msg_id: str, attachment_id: str, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_attachment(
            msg_id, attachment_id, current_user, self.db
        )
        if res is None:
            raise HTTPException(status_code=404, detail="Attachment not found")

        return AttachmentData(**res)

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
        return Category(**res)

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
        if res is None:
            raise HTTPException(status_code=404, detail="Message not found")

        return res

    def message_delete(
        self, msg_id: str, current_user: UserRequest
    ):
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

    def message_trash(
        self, msg_id: str, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_trash(msg_id, current_user, self.db)

        return res

    def message_untrash(
        self, msg_id: str, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.message_untrash(msg_id, current_user, self.db)

        return res

    def update_message_labels(
        self,
        msg_id: str,
        current_user: UserRequest,
        addLabelIds: List[str] = [],
        removeLabelIds: List[str] = [],
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        req = MessageModifyLabelRequest(
            id=msg_id, addLabelIds=addLabelIds, removeLabelIds=removeLabelIds
        )
        provider_service.message_modify_label(req, current_user, self.db)

        return

    def create_draft(
        self, req: CreateDraftRequest, current_user: UserRequest
    ):
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

    def delete_draft(
        self, draft_id: str, current_user: UserRequest
    ):
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
        draft_id = res.get("id", "")

        if res is None:
            raise HTTPException(status_code=404, detail=f"Error getting draft :{res}")
        
        if format == Format.FULL.value:
            msg = parse_message_by_payload(res["message"])
        elif format == Format.RAW.value:
            pass
        elif format == Format.METADATA.value:
            pass
        elif format == Format.MINIMAL.value:
            pass

        return Draft(id=draft_id, message=msg)

    def get_drafts(
        self, params: DraftsQueryParams, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_drafts(params, current_user, self.db)
        if res is None:
            raise HTTPException(status_code=400, detail=f"Error getting drafts :{res}")

        drafts: List[Draft] = []
        nextPageToken = res.get("nextPageToken", None)
        resultSizeEstimate = res.get("resultSizeEstimate", 0)
        
        for draft in res["drafts"]:
            if params.format == Format.FULL:
                draft = Draft(
                    id=draft.get("id", ""), 
                    message=parse_message_by_payload(draft.get("message", {}))
                )
            elif params.format == Format.RAW:
                pass
            elif params.format == Format.METADATA:
                pass
            elif params.format == Format.MINIMAL:
                pass
            drafts.append(draft)
        return DraftsResposnse(
            drafts=drafts,
            nextPageToken=nextPageToken,
            resultSizeEstimate=resultSizeEstimate
        )

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

        print(res)

        return Draft(**res)

    def upload_draft(
        self, draft_id: str, req: CreateDraftRequest, current_user: UserRequest
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.upload_draft(draft_id, req, current_user, self.db)
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

        return MessageGmail(**res)
    