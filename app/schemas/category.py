from enum import Enum
from pydantic import BaseModel
from typing import List

from app.schemas.user import TokenData

class MessageListVisibility(str, Enum):
    HIDE = "hide"
    SHOW = "show"

class LabelListVisibility(str, Enum):
    SHOW = "labelShow"
    HIDE = "labelHide"
    SHOW_IF_UNREAD = "labelShowIfUnread"

class CategoryType(str, Enum):
    USER = "user"
    SYSTEM = "system"

class CategoryColor(BaseModel):
    textColor: str
    backgroundColor: str

class Category(BaseModel):
    id: str
    name: str
    messageListVisibility: MessageListVisibility | None = None
    labelListVisibility: LabelListVisibility | None = None
    type: CategoryType | None = None
    messagesTotal: int | None = None
    messagesUnread: int | None = None
    threadsTotal: int | None = None
    threadsUnread: int | None = None
    color: CategoryColor | None = None

class CategoryListResponse(BaseModel):
    categories: List[Category]

class CreateLabelRequest(BaseModel):
    provider: str
    token_data: TokenData
    body: Category
