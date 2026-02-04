from pydantic import BaseModel

class CredentialResponse(BaseModel):
    access_token: str
    refresh_token: str
    scopes: list[str]
    id_token: str
    token_type: str
    expires_in: int
    expires_at: int