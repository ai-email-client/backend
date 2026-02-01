from enum import Enum
from pydantic import BaseModel
from typing import List

from app.schemas.user import TokenData

INITIAL_LABELS = [
    {
        "name": "appointment",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShowIfUnread",
        "type": "user",
        "color": 
            {
                "textColor": "#0d3472", 
                "backgroundColor": "#b3d4ff"
            }
    },
    {
        "name": "meeting",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShowIfUnread",
        "type": "user",
        "color": 
            {
                "textColor": "#FFFFFF", 
                "backgroundColor": "#000000"
            }
    },
    {
        "name": "invitation",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShowIfUnread",
        "type": "user",
        "color": 
            {
                "textColor": "#1f74ad", 
                "backgroundColor": "#bce3ff"
            }
    },
    {
        "name": "invoice",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShow",
        "type": "user",
        "color": 
            {
                "textColor": "#a32018", 
                "backgroundColor": "#fad1cd"
            }
    },
    {
        "name": "marketing",
        "messageListVisibility": "show",
        "labelListVisibility": "labelHide",
        "type": "user",
        "color": 
            {
                "textColor": "#895000", 
                "backgroundColor": "#ffdea2"
            }
    },
    {
        "name": "notification",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShowIfUnread",
        "type": "user",
        "color": 
            {
                "textColor": "#434343", 
                "backgroundColor": "#eeeeee"
            }
    },
    {
        "name": "announcement",
        "messageListVisibility": "show",
        "labelListVisibility": "labelShow",
        "type": "user",
        "color": 
            {
                "textColor": "#822600", 
                "backgroundColor": "#ffb47b"
            }
    },
    {
        "name": "other",
        "messageListVisibility": "show",
        "labelListVisibility": "labelHide",
        "type": "user",
        "color": 
            {
                "textColor": "#444444", 
                "backgroundColor": "#dddddd"
            }
    }
]

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
    id: str | None = None
    name: str | None = None
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

class GetLabelRequest(BaseModel):
    provider: str
    token_data: TokenData
    id: str

class MessageBatchModifyLabelRequest(BaseModel):
    provider: str
    token_data: TokenData
    ids: List[str]
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []

class MessageModifyLabelRequest(BaseModel):
    provider: str
    token_data: TokenData
    id: str
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []