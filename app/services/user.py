from typing import List, Dict, Any
from config import Config
from app.database.supabase import SupabaseDB
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from app.schemas.user import UserRequest
from fastapi import HTTPException


class UserService:
    def __init__(self, config: Config):
        self.config = config
        self.supabase = SupabaseDB(config)

    def get_user_profile(self, req: UserRequest):
        if req.provider == "gmail":
            provider_service = GmailProvider(self.config)
            creds = self.supabase.table("google_accounts").select(
                "credentials"
            ).eq(
                "email_address", req.email_address
            ).execute()
        elif req.provider == "outlook":
            provider_service = OutlookProvider(self.config)
            creds = self.supabase.table("outlook_accounts").select(
                "credentials"
            ).eq(
                "email_address", req.email_address
            ).execute()
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        res = provider_service.get_user_info(creds)
        print(res)
        return res
        


        

