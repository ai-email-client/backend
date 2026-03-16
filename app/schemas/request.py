from typing import List, Optional, Dict
from pydantic import BaseModel
from app.schemas.category import Category
from app.schemas.email import Attachment, Sender, MessageGmail

class TestSummaryRequest(BaseModel):
    email_text: str

class UserRequest(BaseModel):
    email_address: str
    provider: str


class DifySummaryRequest(BaseModel):
    sender: str
    msg_id: str
    text_plain: str
    email_tags: List[str]

class DifySummaryBatchRequest(BaseModel):
    emails: List[DifySummaryRequest]

class DataInsertSummaryRequest(BaseModel):
    id: str
    sender: str
    msg_id: str
    text_plain: Optional[str] = None
    text_html: Optional[str] = None
    email_tags: List[str]
    current_user: UserRequest


class EmailFetchRequest(BaseModel):
    label: List[Optional[str]] = ["INBOX"]
    limit: Optional[int] = 5
    query: Optional[str] = ""
    page_token: Optional[str] = None


class MessageIdRequest(BaseModel):
    id: str


class MessageBatchDeleteRequest(BaseModel):
    ids: List[str]


class CreateLabelRequest(BaseModel):
    body: Category


class GetLabelRequest(BaseModel):
    id: str


class SyncLabelsRequest(BaseModel):
    names: List[str]


class MessageBatchModifyLabelRequest(BaseModel):
    ids: List[str]
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []


class MessageModifyLabelRequest(BaseModel):
    id: str
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []


class OverviewItemRequest(BaseModel):
    sender: Sender
    email_category: str
    summary: str


class OverviewRequest(BaseModel):
    data: List[OverviewItemRequest]


class WritterRequest(BaseModel):
    email_text: Optional[str] = None
    ai_summary: Optional[str] = None
    user_draft: Optional[str] = None
    topic: Optional[str] = None
    target_person: Optional[str] = None


class CreateDraftRequest(BaseModel):
    to: str
    cc: Optional[str] = ""
    bcc: Optional[str] = ""
    subject: str
    content: Optional[Dict[str, str]] = None
    threadId: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: Optional[str] = None
    action: Optional[str] = "new"
    attachments: Optional[List[Attachment]] = []
