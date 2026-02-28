from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

from app.schemas.color import Color

# class EnumCategory(Enum):
#     APPOINTMENT = "Appointment"
#     PROMOTION = "Promotion"
#     MEETING = "Meeting"
#     INVITATION = "Invitation"
#     INVOICE = "Invoice"
#     MARKETING = "Marketing"
#     NOTIFICATION = "Notification"
#     ANNOUNCEMENT = "Announcement"


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
    textColor: Optional[str] = None
    backgroundColor: Optional[str] = None


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
    color: Optional[CategoryColor] = None


INITIAL_LABELS = {
    "appointment": {
        "name": "appointment",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.BLUE_DARK, "backgroundColor": Color.BLUE_COBALT},
    },
    "meeting": {
        "name": "meeting",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.WHITE, "backgroundColor": Color.BLACK},
    },
    "invitation": {
        "name": "invitation",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.BLUE_ROYAL, "backgroundColor": Color.BLUE_PALE},
    },
    "invoice": {
        "name": "invoice",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.GREEN_DEEP, "backgroundColor": Color.GREEN_MINT},
    },
    "marketing": {
        "name": "marketing",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.BROWN_GOLDEN, "backgroundColor": Color.APRICOT},
    },
    "notification": {
        "name": "notification",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.RED_DEEP, "backgroundColor": Color.RED_SALMON},
    },
    "announcement": {
        "name": "announcement",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.BLUE_BABY, "backgroundColor": Color.BLUE_PALE},
    },
    "other": {
        "name": "other",
        "messageListVisibility": MessageListVisibility.SHOW,
        "labelListVisibility": LabelListVisibility.SHOW,
        "type": "user",
        "color": {"textColor": Color.BLACK, "backgroundColor": Color.WHITE},
    },
}
