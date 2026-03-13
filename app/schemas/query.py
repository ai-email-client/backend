from typing import List
from fastapi import Query

from app.schemas.email import Format


class DraftsQueryParams:
    def __init__(
        self,
        maxResults: int = Query(default=5, ge=1, le=500),
        pageToken: str | None = Query(default=None),
        q: str | None = Query(default=None),
        includeSpamTrash: bool = Query(default=False),
        format: str = Query(default=Format.FULL.value),
        metadataHeaders: List[str] = Query(default=None),
    ):
        self.maxResults = maxResults
        self.pageToken = pageToken
        self.q = q
        self.includeSpamTrash = includeSpamTrash
        self.format = format
        self.metadataHeaders = metadataHeaders



class DraftQueryParam:
    def __init__(
        self,
        format: str = Query(default=Format.FULL.value),
    ):
        self.format = format


class MessagesParam:
    def __init__(
        self,
        maxResults: int = Query(default=5, ge=1, le=500),
        pageToken: str | None = Query(default=None),
        q: str | None = Query(default=None),
        labelIds: List[str] = Query(default=["INBOX"]),
        includeSpamTrash: bool = Query(default=True),
        format: str = Query(default=Format.FULL.value),
        metadataHeaders: List[str] = Query(default=None),
    ):
        self.maxResults = maxResults
        self.pageToken = pageToken
        self.q = q
        self.labelIds = labelIds
        self.includeSpamTrash = includeSpamTrash
        self.format = format
        self.metadataHeaders = metadataHeaders


class MessageParam:
    def __init__(
        self,
        format: str = Query(default=Format.FULL.value),
        metadataHeaders: List[str] = Query(default=None),
    ):
        self.format = format
        self.metadataHeaders = metadataHeaders


class AuthQueryParams:
    def __init__(
        self,
        state: str = Query(default=None),
        code: str = Query(default=None),
    ):
        self.state = state
        self.code = code
