from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None
    
class EmailAccountCreate(BaseModel):
    email: str
    provider: str
    access_token: str
    refresh_token: Optional[str] = None

class EmailAccountResponse(BaseModel):
    email: str
    provider: str
    
    class Config:
        from_attributes = True

class EmailFetchRequest(BaseModel):
    provider: str
    token_data: Dict[str, Any]
    limit: Optional[int] = 50

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
    extraction_status: str
    confidence: float
    
class EmailMessageRequest(BaseModel):
    provider: str
    token_data: Dict[str, Any]
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
    body: str
    time: str
    tag: List[str]
    attachments: List[Attachment]
    plain_text: Optional[str] = None
