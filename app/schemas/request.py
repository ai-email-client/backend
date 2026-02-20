from typing import List,Optional
from pydantic import BaseModel
from app.schemas.category import Category
from app.schemas.email import Message, Sender

class UserRequest(BaseModel):
    email_address: str
    provider: str

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

class AttachmentRequest(BaseModel):
    msg_id: str
    attachment_id: str

class EmailFetchRequest(BaseModel):
    label: List[Optional[str]] = ["INBOX"]
    limit: Optional[int] = 5    
    query: Optional[str] = ''
    page_token: Optional[str] = None

class EmailMessageRequest(BaseModel):
    msg_id: str

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

class DraftCreateRequest(BaseModel):
    id: str
    message: Message

class OverviewRequest(BaseModel):
    sender: Sender
    email_category: str
    summary: str
    limit: Optional[int] = 50