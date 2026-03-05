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


class MessageResponse(BaseModel):
    id: str
    threadId: str


class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None
    headers: Optional[List[Header]] = None
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
    headers: Optional[List[Header]] = None
    body: Optional["MessagePartBody"] = None
    parts: Optional[List["MessagePart"]] = None


class Message(BaseModel):
    id: str
    threadId: str
    labelIds: Optional[List[str]] = None
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


class Sender(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class Draft(BaseModel):
    id: str
    message: Message
