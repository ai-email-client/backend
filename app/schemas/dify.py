from pydantic import BaseModel
from typing import List, Optional
from app.schemas.email import (
    Sender
)

class DifySummaryRequest(BaseModel):
    msg_id: str
    plain_text: str
    email_tags: List[str]

class DifySummary(BaseModel):
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

class DifySummaryResponse(BaseModel):
    clean_email: DifySummary