import re
from enum import Enum
from html import parser
from datetime import timezone
from dateutil import parser
from dateutil.tz import gettz
from pydantic import BaseModel, field_validator
from typing import List, Optional
from app.schemas.email import Sender

TZ_INFOS = {
    "EST": gettz("America/New_York"),
    "EDT": gettz("America/New_York"),
    "CST": gettz("America/Chicago"),
    "CDT": gettz("America/Chicago"),
    "PST": gettz("America/Los_Angeles"),
    "PDT": gettz("America/Los_Angeles"),
    "UTC": timezone.utc,
    "GMT": timezone.utc,
    "THAI_TZ": gettz("Asia/Bangkok"),
}

class Status(str, Enum):
    new = "new"
    processing = "processing"
    done = "done"
    error = "error"


class Importance(BaseModel):
    level: Optional[str] = None
    reason: Optional[str] = None


class DifySummary(BaseModel):
    sender: Optional[Sender] = None
    email_category: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    instructions: Optional[List[str]] = None
    required_items: Optional[List[str]] = None
    summary: Optional[str] = None
    importance: Optional[Importance] | str = None
    is_spam: Optional[bool] = None
    is_threat: Optional[bool] = None
    spam_type: Optional[str] = None
    spam_confidence: Optional[float] = None
    security_type: Optional[str] = None
    security_confidence: Optional[float] = None
    extraction_status: Optional[str] = None
    confidence: Optional[float] = None

    @field_validator("summary", "importance", mode="before")
    @classmethod
    def fix_duplicated_ai_fields(cls, data, info):

        if not isinstance(data, str):
            return data

        has_summary_block    = re.search(r'(?:\*{0,2})Summary:(?:\*{0,2})', data, re.IGNORECASE)
        has_importance_block = re.search(r'(?:\*{0,2})Importance:(?:\*{0,2})', data, re.IGNORECASE)

        if not has_summary_block and not has_importance_block:
            return data

        field_name = info.field_name

        if field_name == "summary":
            match = re.search(
                r'(?:\*{0,2})Summary:(?:\*{0,2})\s*(.*?)(?=\n{1,2}\s*(?:\*{0,2})Importance:|$)',
                data, re.DOTALL | re.IGNORECASE
            )
            return match.group(1).strip() if match else data

        if field_name == "importance":
            imp_dict = {}

            match_level = re.search(
                r'(?:\*{0,2})Importance:(?:\*{0,2})\s*([A-Za-z]+)',
                data, re.IGNORECASE
            )
            match_reason = re.search(
                r'(?:\*{0,2})Reason:(?:\*{0,2})\s*(.*?)(?=\n\s*\n|$)',
                data, re.DOTALL | re.IGNORECASE
            )

            if match_level:
                imp_dict['level'] = match_level.group(1).strip().capitalize()
            if match_reason:
                imp_dict['reason'] = match_reason.group(1).strip()

            return imp_dict if imp_dict else None

        return data

    @field_validator("date", mode="before")
    @classmethod
    def supabase_date_format(cls, v):
        if not v or str(v).lower() in ("null", "none", "", "n/a"):
            return None

        try:
            dt = parser.parse(str(v), fuzzy=True, dayfirst=True, tzinfos=TZ_INFOS)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc).astimezone(TZ_INFOS["THAI_TZ"])
            else:
                dt = dt.astimezone(TZ_INFOS["THAI_TZ"])

            return dt.strftime("%Y-%m-%d")

        except Exception:
            return None

    @field_validator("time", mode="before")
    @classmethod
    def normalize_time(cls, v):
        if not v or str(v).lower() in ("null", "none", "", "n/a"):
            return None

        try:
            dt = parser.parse(str(v), fuzzy=True, tzinfos=TZ_INFOS)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc).astimezone(TZ_INFOS["THAI_TZ"])
            else:
                dt = dt.astimezone(TZ_INFOS["THAI_TZ"])

            return dt.strftime("%H:%M:%S")

        except Exception:
            return None

class DifyDraft(BaseModel):
    tone_used: Optional[str] = None
    draft: Optional[str] = None
    confidence: Optional[float] = None