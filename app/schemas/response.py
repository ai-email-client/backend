from typing import List,Optional
from pydantic import BaseModel
from app.schemas.dify import DifySummary
from app.schemas.email import Attachment
from app.schemas.category import Category



class DifySummaryResponse(BaseModel):
    clean_email: DifySummary
    
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


class CategoryListResponse(BaseModel):
    categories: List[Category]