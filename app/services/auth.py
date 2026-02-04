import datetime
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from config import Config
from typing import Dict, Any
from fastapi import HTTPException
from app.utility import jwt_encode
from database import SupabaseDB

class AuthService:
    def __init__(self, config: Config):
        self.config = config
        self.db = SupabaseDB(config)

    def get_authorization_url(self, provider: str):
        if provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_authorization_url()

        return res

    def handle_oauth_callback(self, provider: str, code: str, state: str):
        if provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        creds = provider_service.get_credentials(code, state, self.db)
        user_info = provider_service.get_user_info(creds)
        payload = {
            "email_address": user_info.get('emailAddress'),
            "provider": provider,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }

        token = jwt_encode(payload, self.config.SECRET_KEY)

        url = f"{self.config.FRONTEND_API_URL}/#/?token={token}"

        return url

    def get_user_info(self, provider: str, creds: Dict[str, Any]):
        if provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        res = provider_service.get_user_info(creds)

        return res