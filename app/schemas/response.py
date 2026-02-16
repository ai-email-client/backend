from typing import List,Optional
from pydantic import BaseModel
from app.schemas.dify import DifySummary
from app.schemas.email import Attachment
from app.schemas.category import Category

class SourceEmailResponse(BaseModel):
    id: str
    msg_id: str
    plain_text: str
    email_tags: List[str]
    status: str
    user_email_address: str

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