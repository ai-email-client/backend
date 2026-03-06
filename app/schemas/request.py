from typing import List, Optional
from pydantic import BaseModel
from app.schemas.category import Category
from app.schemas.email import Attachment, Sender
from app.schemas.response import OverviewResponse


class UserRequest(BaseModel):
    email_address: str
    provider: str


class DifySummaryBatchRequest(BaseModel):
    ids: List[str]


class DifySummaryRequest(BaseModel):
    sender: str
    msg_id: str
    plain_text: str
    email_tags: List[str]


class DataInsertSummaryRequest(BaseModel):
    id: str
    sender: str
    msg_id: str
    plain_text: str
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
    to: Optional[str] = ""
    subject: Optional[str] = ""
    message: Optional[str] = ""
    attachments: Optional[List[Attachment]] = []
