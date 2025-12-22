from pydantic import BaseModel
from typing import Optional, List

class EmailAccountCreate(BaseModel):
    email: str
    provider: str
    access_token: str
    refresh_token: Optional[str] = None

class EmailAccountResponse(BaseModel):
    email: str
    provider: str
    
    class Config:
        from_attributes = True