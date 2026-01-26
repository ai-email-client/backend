from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

from app.schemas.user import TokenData

class Category(Enum):
    APPOINTMENT = "Appointment"
    MEETING = "Meeting"
    INVITATION = "Invitation"
    INVOICE = "Invoice"
    MARKETING = "Marketing"
    NOTIFICATION = "Notification"
    ANNOUNCEMENT = "Announcement"

class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None
    
class EmailAccountCreate(BaseModel):
    email: str
    provider: str
    token_data: TokenData

class EmailAccountResponse(BaseModel):
    email: str
    provider: str
    
    class Config:
        from_attributes = True

class GetRequest(BaseModel):
    provider: str
    token_data: TokenData

class AttachmentRequest(BaseModel):
    provider: str
    token_data: TokenData
    msg_id: str
    attachment_id: str

class EmailFetchRequest(BaseModel):
    provider: str
    token_data: TokenData
    label: List[Optional[str]] = ["INBOX"]
    limit: Optional[int] = 5    
    page_token: Optional[str] = None

class EmailSummaryRequest(BaseModel):
    email_text: str

class DifySummaryRequest(BaseModel):
    inputs: EmailSummaryRequest
    user: str="frontend-test"
    response_mode: str

class Sender(BaseModel):
    name: str
    type: str

class EmailSummaryResponse(BaseModel):
    sender: Sender
    email_category: str
    date: str
    time: str
    location: str
    instructions: Optional[List[str]] = None
    required_items: Optional[List[str]] = None
    summary: str
    is_spam: bool
    is_threat: bool
    spam_type: Optional[str] = None
    spam_confidence: int
    security_type: str
    security_confidence: int
    extraction_status: str
    confidence: float
    
class EmailMessageRequest(BaseModel):
    provider: str
    token_data: TokenData
    message_id: str

class EmailShortResponse(BaseModel):
    msg_id: str
    subject: str
    sender: str
    snippet: str
    time: str
    tag: List[str]
    attachments: List[Attachment]

class EmailFetchResponse(BaseModel):
    count: int
    emails: List[EmailShortResponse]

class EmailDetailResponse(BaseModel):
    msg_id: str
    subject: str
    sender: str
    snippet: str
    html: Optional[str] = None
    plain_text: Optional[str] = None
    time: str
    tag: List[str]
    attachments: List[Attachment]

class EmailPlainResponse(BaseModel):
    msg_id: str
    plain_text: Optional[str] = None
    tag: List[str]

class EmailFetchPlainResponse(BaseModel):
    emails: List[EmailPlainResponse]
    page_token: Optional[str] = None

class MessageDeleteRequest(BaseModel):
    provider: str
    token_data: TokenData
    id: str

class MessageBatchDeleteRequest(BaseModel):
    provider: str
    token_data: TokenData
    ids: List[str]