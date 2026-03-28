import datetime
from config import Config
from database import SupabaseDB
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from typing import Dict, Any
from fastapi import HTTPException
from app.utility import jwt_encode, jwt_decode
from app.schemas.response import LoginResponse


class AuthService:
    def __init__(self, config: Config, db: SupabaseDB):
        self.config = config
        self.db = db

    def get_authorization_url(self, provider: str, origin: str = "web"):
        if provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_authorization_url(origin, provider)

        return LoginResponse(url=res[0], state=res[1])

    def handle_oauth_callback(self, provider: str, code: str, state: str, origin: str = "web"):
        if provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        creds = provider_service.get_credentials(code, state, provider, origin, self.db)
        if creds is None:
            raise HTTPException(status_code=404, detail="Credentials not found")
        user_info = provider_service.get_user_info(creds)
        if user_info is None:
            raise HTTPException(status_code=404, detail="User not found")
        payload = {
            "email_address": user_info.get("emailAddress"),
            "provider": provider,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        }

        if self.config.SECRET_KEY is None:
            raise HTTPException(status_code=404, detail="Secret not found")

        token = jwt_encode(payload, self.config.SECRET_KEY)

        return token

    def get_user_info(self, provider: str, creds: Dict[str, Any]):
        if provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        res = provider_service.get_user_info(creds)

        return res
