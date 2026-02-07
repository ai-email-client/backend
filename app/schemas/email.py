from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class Attachment(BaseModel):
    filename: str
    mimeType: str
    size: int
    attachmentId: Optional[str] = None

class ClassificationLabelFieldValue(BaseModel):
    fieldId: str
    selection: str

class ClassificationLabelValue(BaseModel):
    labelId: str
    fields: List[ClassificationLabelFieldValue]

class Header(BaseModel):
    name: str
    value: str

class MessagePartBody(BaseModel):
    attachmentId: str
    size: int
    data: str

class MessagePart(BaseModel):
    partId: str
    mimeType: str
    filename: str
    headers: List[Header]
    body: MessagePartBody
    parts: List[MessagePart]

class Message(BaseModel):
    id: str
    threadId: str
    labelIds: List[str]
    snippet: str
    historyId: str
    internalDate: str
    payload: MessagePart
    sizeEstimate: int
    raw: str
    classificationLabelValues: List[ClassificationLabelValue]

class Sender(BaseModel):
    name: str
    type: str

