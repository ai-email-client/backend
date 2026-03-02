from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.dify import DifySummary
from app.schemas.email import Attachment, Sender, Message
from app.schemas.category import Category


class MessagesResponse(BaseModel):
    messages: List[Message] = []
    nextPageToken: Optional[str] = None
    resultSizeEstimate: Optional[int] = None


class SourceEmailResponse(BaseModel):
    id: str
    msg_id: str
    plain_text: str
    email_tags: List[str]
    status: str
    user_email_address: str


class EmailAIAnalysisResponse(BaseModel):
    source_email_id: str
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
    spam_confidence: Optional[float] = None
    security_type: Optional[str] = None
    security_confidence: Optional[float] = None
    extraction_status: Optional[str] = None
    confidence: Optional[float] = None


class OverviewResponse(BaseModel):
    source_email_id: str
    sender: Sender
    email_category: str
    summary: str


class CredentialResponse(BaseModel):
    access_token: str
    refresh_token: str
    scopes: list[str]
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int


class DifyOutputs(BaseModel):
    clean_email: Optional[DifySummary] = None


class DifyDataResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    outputs: Optional[DifyOutputs] = None
    error: Optional[str] = None
    elapsed_time: float
    total_tokens: int
    total_steps: int
    created_at: int
    finished_at: int


class DifyResponse(BaseModel):
    task_id: str
    workflow_run_id: str
    data: DifyDataResponse | None


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
    messages: List[Dict[str, Any]]


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
    labels: List[Category]


class WritterResponse(BaseModel):
    tone_used: Optional[str] = None
    draft: Optional[str] = None
    confidence: Optional[float] = None
