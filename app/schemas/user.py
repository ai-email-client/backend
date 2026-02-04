from pydantic import BaseModel

from typing import List, Optional


class UserRequest(BaseModel):
    email_address: str
    provider: str

class TokenData(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None