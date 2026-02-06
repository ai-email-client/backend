from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None
 
class Sender(BaseModel):
    name: str
    type: str
   
class EmailAccountCreate(BaseModel):
    email: str

class EmailAccountResponse(BaseModel):
    email: str

    class Config:
        from_attributes = True
    

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

class EmailShortResponse(BaseModel):
    msg_id: str
    subject: str
    sender: str
    snippet: str
    time: str
    tag: List[str]
    attachments: List[Attachment]

class EmailFetchResponse(BaseModel):
    page_token: Optional[str] = None
    messages: List[EmailShortResponse]

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
    messages: List[EmailPlainResponse]
    page_token: Optional[str] = None

class MessageIdRequest(BaseModel):
    id: str

class MessageBatchDeleteRequest(BaseModel):
    ids: List[str]