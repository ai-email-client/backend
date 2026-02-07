from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from app.schemas.email import (
    Sender
)
class Status(str, Enum):
    new = "new"
    processing = "processing"
    done = "done"
    error = "error"
    

class DifySummary(BaseModel):
    sender: Optional[Sender] = None
    email_category: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    instructions: Optional[List[str]] = None
    required_items: Optional[List[str]] = None
    summary: Optional[str] = None
    is_spam: Optional[bool] = None
    is_threat: Optional[bool] = None
    spam_type: Optional[str] = None
    spam_confidence: Optional[int] = None
    security_type: Optional[str] = None
    security_confidence: Optional[int] = None
    extraction_status: Optional[str] = None
    confidence: Optional[float] = None

