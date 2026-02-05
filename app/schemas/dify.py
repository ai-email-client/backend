from pydantic import BaseModel
from typing import List, Optional
from app.schemas.email import (
    Sender
)

class EmailSummaryRequest(BaseModel):
    email_text: str

class DifySummaryRequest(BaseModel):
    inputs: EmailSummaryRequest
    user: str="frontend-test"
    response_mode: str

class DifySummaryBatchRequest(BaseModel):
    inputs: List[EmailSummaryRequest]
    user: str="frontend-test"
    response_mode: str

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