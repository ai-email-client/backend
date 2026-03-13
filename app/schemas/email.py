from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum


class Format(str, Enum):
    FULL = "full"
    MINIMAL = "minimal"
    RAW = "raw"
    METADATA = "metadata"


class Header(BaseModel):
    name: str
    value: str

class Sender(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    threadId: str


class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None
    headers: Optional[List[Header]] = []
    data: Optional[str] = None


class AttachmentData(BaseModel):
    size: int
    data: str


class ClassificationLabelFieldValue(BaseModel):
    fieldId: str
    selection: str


class ClassificationLabelValue(BaseModel):
    labelId: str
    fields: List[ClassificationLabelFieldValue]


class MessagePartBody(BaseModel):
    attachmentId: Optional[str] = None
    size: Optional[int] = 0
    data: Optional[str] = None


class MessagePart(BaseModel):
    partId: Optional[str] = None
    mimeType: Optional[str] = None
    filename: Optional[str] = None
    headers: Optional[List[Header]] = []
    body: Optional["MessagePartBody"] = None
    parts: Optional[List["MessagePart"]] = []


class MessageGmail(BaseModel):
    id: str
    threadId: str
    labelIds: List[str]
    snippet: Optional[str] = None
    historyId: Optional[str] = None
    internalDate: Optional[str] = None
    payload: Optional["MessagePart"] = None
    attachments: Optional[List["Attachment"]] = None
    text_plain: Optional[str] = None
    text_html: Optional[str] = None
    sizeEstimate: Optional[int] = None
    raw: Optional[str] = None
    classificationLabelValues: Optional[List[ClassificationLabelValue]] = None

class Message(BaseModel):
    id: str                                   
    threadId: str                             
    message_id: Optional[str] = None         
    historyId: Optional[str] = None          

    sender: Optional[Sender] = None             
    to: Optional[List[Sender]] = None
    cc: Optional[List[Sender]] = None
    bcc: Optional[List[Sender]] = None                

    subject: Optional[str] = None
    snippet: Optional[str] = None            
    text_plain: Optional[str] = None
    text_html: Optional[str] = None

    attachments: Optional[List[Attachment]] = None

    in_reply_to: Optional[str] = None        
    references: Optional[str] = None         

    labelIds: Optional[List[str]] = None     
    date: Optional[str] = None              
    internalDate: Optional[str] = None      
    sizeEstimate: Optional[int] = None


class Draft(BaseModel):
    id: str
    message: Message
