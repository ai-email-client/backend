from enum import Enum
from pydantic import BaseModel
from typing import List

from app.schemas.color import Color

class Category(Enum):
    APPOINTMENT = "Appointment"
    MEETING = "Meeting"
    INVITATION = "Invitation"
    INVOICE = "Invoice"
    MARKETING = "Marketing"
    NOTIFICATION = "Notification"
    ANNOUNCEMENT = "Announcement"

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
    body: Category

class GetLabelRequest(BaseModel):
    id: str

class SyncLabelsRequest(BaseModel):
    names: List[str]

class MessageBatchModifyLabelRequest(BaseModel):
    ids: List[str]
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []

class MessageModifyLabelRequest(BaseModel):
    id: str
    addLabelIds: List[str] = []
    removeLabelIds: List[str] = []


INITIAL_LABELS = {
    "appointment": {
        "name": "appointment",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.BLUE_DARK,
            "backgroundColor": Color.BLUE_COBALT
        }
    },
    "meeting": {
        "name": "meeting",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.WHITE,
            "backgroundColor": Color.BLACK
        }
    },
    "invitation": {
        "name": "invitation",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.BLUE_ROYAL,
            "backgroundColor": Color.BLUE_PALE
        }
    },
    "invoice": {
        "name": "invoice",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.RED_BRICK,
            "backgroundColor": Color.RED_SALMON
        }
    },
    "marketing": {
        "name": "marketing",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.BROWN_GOLDEN,
            "backgroundColor": Color.APRICOT
        }
    },
    "notification": {
        "name": "notification",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.DARK_GRAY_1,
            "backgroundColor": Color.OFF_WHITE_1
        }
    },
    "announcement": {
        "name": "announcement",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.RED_DEEP,
            "backgroundColor": Color.PEACH
        }
    },
    "other": {
        "name": "other",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {
            "textColor": Color.DARK_GRAY_2,
            "backgroundColor": Color.OFF_WHITE_2
        }
    }
}