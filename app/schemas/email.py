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

class EmailMessageRequest(BaseModel):
    provider: str
    token_data: Dict[str, Any]
    message_id: str

class EmailShortResponse(BaseModel):
    id: str
    subject: str
    sender: str
    snippet: str

class EmailFetchResponse(BaseModel):
    count: int
    emails: List[EmailShortResponse]

class EmailDetailResponse(BaseModel):
    id: str
    subject: str
    sender: str
    snippet: str
    body: str
    time: str
    tag: List[str]
    attachments: List[Attachment]
