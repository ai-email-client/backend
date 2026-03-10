from typing import List
from app import utility
from app.schemas.category import Category
from app.schemas.email import AttachmentData, Draft, Format, MessageGmail, Message
from app.schemas.response import CategoryListResponse, MessagesResponse
from config import Config
from database import SupabaseDB
from fastapi import HTTPException
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI

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
        return MessagesResponse(**res)

    def get_message_batch(
        self,
        msgs: MessagesResponse,
        current_user: UserRequest,
        format: str = Format.FULL.value,
        metadataHeaders: List[str] = None,
    ):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        param = MessageParam(
            format=format,
            metadataHeaders=metadataHeaders,
        )
        res = provider_service.get_message_batch(
            msgs.messages, param, current_user, self.db
        )
        if res is None:
            raise HTTPException(status_code=404, detail=f"Messages not found")
        
        for msg in res:
            if param.format != "raw":
                msg['message_id'] = utility.get_header_value(msg["payload"], "Message-ID")
                msg['in_reply_to'] = utility.get_header_value(msg["payload"], "In-Reply-To")
                msg['references'] = utility.get_header_value(msg["payload"], "References")

                msg["attachments"] = utility.get_attachments(msg["payload"])

                msg["to"] = utility.get_header_value(msg["payload"], "To")
                msg["sender"] = utility.get_header_value(msg["payload"], "From")
                msg["subject"] = utility.get_header_value(msg["payload"], "Subject")
                msg["date"] = utility.get_header_value(msg["payload"], "Date")

                body_html = utility.get_part_by_mimetype(msg["payload"], "text/html")
                body_plain = utility.get_part_by_mimetype(msg["payload"], "text/plain")

                if body_html is None:
                    text_html = ""
                else:
                    text_html = utility.decode_base64(body_html["body"]["data"])

                if body_plain is None:
                    body_plain = utility.get_part_by_mimetype(msg["payload"], "text/html")
                    if body_plain is not None:
                        text_plain = utility.clean_html(
                                utility.decode_base64(body_plain["body"]["data"])
                            )
                    else:
                        text_plain = ""
                else:
                    text_plain = utility.decode_base64(body_plain["body"]["data"])
                    text_plain = utility.clean_text(text_plain)

                msg["text_plain"] = text_plain
                msg["text_html"] = text_html

            else:
                message = utility.parse_raw_message_from_string(msg["raw"])
                msg['message_id'] = message.get("Message-ID")
                msg['in_reply_to'] = message.get("In-Reply-To")
                msg['references'] = message.get("References")


                msg["attachments"] = utility.get_attachments_from_iterator(message.iter_attachments())

                msg["to"] = message.get("To")
                msg["sender"] = message.get("From")
                msg["subject"] = message.get("Subject")
                msg["date"] = message.get("Date")

                body_html = message.get_body("html")
                body_plain = message.get_body("plain")

                if body_html is None or body_html.get_content() == "":
                    text_html = ""
                else:
                    text_html = body_html.get_content()

                if body_plain is None or body_plain.get_content() == "":
                    body_plain = body_html
                    if body_plain is not None:
                        text_plain = utility.clean_html(
                            body_plain.get_content()
                        )
                    else:
                        text_plain = ""
                else:
                    text_plain = body_plain.get_content()
                    text_plain = utility.clean_text(text_plain)

                msg["text_html"] = text_html
                msg["text_plain"] = text_plain
                
                msg['raw'] = ''
        
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
        
        if param.format != "raw":
            res['message_id'] = utility.get_header_value(res["payload"], "Message-ID")
            res['in_reply_to'] = utility.get_header_value(res["payload"], "In-Reply-To")
            res['references'] = utility.get_header_value(res["payload"], "References")

            res["attachments"] = utility.get_attachments(res["payload"])

            res["to"] = utility.get_header_value(res["payload"], "To")
            res["sender"] = utility.get_header_value(res["payload"], "From")
            res["subject"] = utility.get_header_value(res["payload"], "Subject")
            res["date"] = utility.get_header_value(res["payload"], "Date")

            body_html = utility.get_part_by_mimetype(res["payload"], "text/html")
            body_plain = utility.get_part_by_mimetype(res["payload"], "text/plain")

            if body_html is None:
                text_html = ""
            else:
                text_html = utility.decode_base64(body_html["body"]["data"])

            if body_plain is None:
                body_plain = utility.get_part_by_mimetype(res["payload"], "text/html")
                if body_plain is not None:
                    text_plain = utility.clean_html(
                        utility.decode_base64(body_plain["body"]["data"])
                    )
                else:
                    text_plain = ""
            else:
                text_plain = utility.decode_base64(body_plain["body"]["data"])
                text_plain = utility.clean_text(text_plain)

            res["text_plain"] = text_plain
            res["text_html"] = text_html
        else:
            message = utility.parse_raw_message_from_string(res["raw"])
            res["message_id"] = message.get("Message-ID")
            res["in_reply_to"] = message.get("In-Reply-To")
            res["references"] = message.get("References")

            res["to"] = message.get("To")
            res["sender"] = message.get("From")
            res["subject"] = message.get("Subject")
            res["date"] = message.get("Date")

            body_html = message.get_body("html")
            body_plain = message.get_body("plain")

            if body_html is None or body_html.get_content() == "":
                text_html = ""
            else:
                text_html = body_html.get_content()

            if body_plain is None or body_plain.get_content() == "":
                body_plain = body_html
                if body_plain is not None:
                    text_plain = utility.clean_html(
                        body_plain.get_content()
                    )
                else:
                    text_plain = ""
            else:
                text_plain = body_plain.get_content()
                text_plain = utility.clean_text(text_plain)

            res["text_html"] = text_html
            res["text_plain"] = text_plain
            
            res["attachments"] = utility.get_attachments_from_iterator(message.iter_attachments())

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

        if res is None:
            raise HTTPException(status_code=404, detail=f"Error getting draft :{res}")

        if format != "raw":
            res["message"]["message_id"] = utility.get_header_value(res["message"]["payload"], "Message-ID")
            res["message"]["in_reply_to"] = utility.get_header_value(res["message"]["payload"], "In-Reply-To")
            res["message"]["references"] = utility.get_header_value(res["message"]["payload"], "References")

            res["message"]["attachments"] = utility.get_attachments(res["message"]["payload"])
            
            res["message"]["to"] = utility.get_header_value(res["message"]["payload"], "To")
            res["message"]["sender"] = utility.get_header_value(res["message"]["payload"], "From")
            res["message"]["subject"] = utility.get_header_value(res["message"]["payload"], "Subject")
            res["message"]["date"] = utility.get_header_value(res["message"]["payload"], "Date")

            body_html = utility.get_part_by_mimetype(res["message"]["payload"], "text/html")
            body_plain = utility.get_part_by_mimetype(res["message"]["payload"], "text/plain")

            if body_html is None:
                text_html = ""
            else:
                text_html = utility.decode_base64(body_html["body"]["data"])

            if body_plain is None:
                body_plain = utility.get_part_by_mimetype(res["message"]["payload"], "text/html")
                if body_plain is not None:
                    text_plain = utility.clean_html(
                        utility.decode_base64(body_plain["body"]["data"])
                    )
                else:
                    text_plain = ""
            else:
                text_plain = utility.decode_base64(body_plain["body"]["data"])
                text_plain = utility.clean_text(text_plain)

            res["message"]["text_plain"] = text_plain
            res["message"]["text_html"] = text_html
        else:
            message = utility.parse_raw_message_from_string(res["message"]["raw"])
            res["message"]["message_id"] = message.get("Message-ID")
            res["message"]["in_reply_to"] = message.get("In-Reply-To")
            res["message"]["references"] = message.get("References")

            res["message"]["to"] = message.get("To")
            res["message"]["sender"] = message.get("From")
            res["message"]["subject"] = message.get("Subject")
            res["message"]["date"] = message.get("Date")

            body_html = message.get_body("html")
            body_plain = message.get_body("plain")

            if body_html is None or body_html.get_content() == "":
                text_html = ""
            else:
                text_html = body_html.get_content()

            if body_plain is None or body_plain.get_content() == "":
                body_plain = body_html
                if body_plain is not None:
                    text_plain = utility.clean_html(
                        body_plain.get_content()
                    )
                else:
                    text_plain = ""
            else:
                text_plain = body_plain.get_content()
                text_plain = utility.clean_text(text_plain)

            res["message"]["text_html"] = text_html
            res["message"]["text_plain"] = text_plain
            
            res["message"]["attachments"] = utility.get_attachments_from_iterator(message.iter_attachments())
            res["message"]["raw"] = ''


        return Draft(**res)

    def get_drafts(self, params: DraftsQueryParams, current_user: UserRequest):
        if current_user.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif current_user.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        msgs = provider_service.get_drafts(params, current_user, self.db)
        if msgs is None:
            raise HTTPException(status_code=400, detail=f"Error getting drafts :{msgs}")

        res = provider_service.get_draft_batch(msgs, current_user, self.db, params)
        if res is None:
            raise HTTPException(status_code=400, detail=f"Error getting draft batch :{res}")
        for draft in res:
            if params.format != "raw":
                draft["message"]["message_id"] = utility.get_header_value(draft["message"]["payload"], "Message-ID")
                draft["message"]["in_reply_to"] = utility.get_header_value(draft["message"]["payload"], "In-Reply-To")
                draft["message"]["references"] = utility.get_header_value(draft["message"]["payload"], "References")

                draft["message"]["attachments"] = utility.get_attachments(draft["message"]["payload"])
                
                draft["message"]["to"] = utility.get_header_value(draft["message"]["payload"], "To")
                draft["message"]["sender"] = utility.get_header_value(draft["message"]["payload"], "From")
                draft["message"]["subject"] = utility.get_header_value(draft["message"]["payload"], "Subject")
                draft["message"]["date"] = utility.get_header_value(draft["message"]["payload"], "Date")

                body_html = utility.get_part_by_mimetype(draft["message"]["payload"], "text/html")
                body_plain = utility.get_part_by_mimetype(draft["message"]["payload"], "text/plain")

                if body_html is None:
                    text_html = ""
                else:
                    text_html = utility.decode_base64(body_html["body"]["data"])

                if body_plain is None:
                    body_plain = utility.get_part_by_mimetype(res["message"]["payload"], "text/html")
                    if body_plain is not None:
                        text_plain = utility.clean_html(
                            utility.decode_base64(body_plain["body"]["data"])
                        )
                    else:
                        text_plain = ""
                else:
                    text_plain = utility.decode_base64(body_plain["body"]["data"])
                    text_plain = utility.clean_text(text_plain)

                draft["message"]["text_plain"] = text_plain
                draft["message"]["text_html"] = text_html
                
            else:
                message = utility.parse_raw_message_from_string(draft["message"]["raw"])
                draft["message"]["message_id"] = message.get("Message-ID")
                draft["message"]["in_reply_to"] = message.get("In-Reply-To")
                draft["message"]["references"] = message.get("References")

                draft["message"]["to"] = message.get("To")
                draft["message"]["sender"] = message.get("From")
                draft["message"]["subject"] = message.get("Subject")
                draft["message"]["date"] = message.get("Date")

                body_html = message.get_body("html")
                body_plain = message.get_body("plain")

                if body_html is None or body_html.get_content() == "":
                    text_html = ""
                else:
                    text_html = body_html.get_content()

                if body_plain is None or body_plain.get_content() == "":
                    body_plain = body_html
                    if body_plain is not None:
                        text_plain = utility.clean_html(
                            body_plain.get_content()
                        )
                    else:
                        text_plain = ""
                else:
                    text_plain = body_plain.get_content()
                    text_plain = utility.clean_text(text_plain)

                draft["message"]["text_html"] = text_html
                draft["message"]["text_plain"] = text_plain
                
                draft["message"]["attachments"] = utility.get_attachments_from_iterator(message.iter_attachments())
                draft["message"]["raw"] = ''

        return DraftsResposnse(
            drafts=res,
            nextPageToken=msgs.nextPageToken,
            resultSizeEstimate=msgs.resultSizeEstimate
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
    