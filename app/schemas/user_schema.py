from pydantic import BaseModel, EmailStr

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    imap_server: str = "imap.gmail.com"

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
