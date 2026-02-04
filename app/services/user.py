from typing import List, Dict, Any
from config import Config
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from app.schemas.user import UserRequest
from fastapi import HTTPException

from database import SupabaseDB


class UserService:
    def __init__(self, config: Config):
        self.config = config
        self.supabase = SupabaseDB(config)

    def get_user_profile(self, req: UserRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        creds = provider_service.get_stored_credentials(req.email_address, self.supabase)
        res = provider_service.get_user_info(creds)

        return res
        


        

