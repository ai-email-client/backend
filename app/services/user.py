from typing import List, Dict, Any
from config import Config
from fastapi import HTTPException

from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from app.schemas.request import UserRequest

from database import SupabaseDB


class UserService:
    def __init__(self, config: Config):
        self.config = config
        self.supabase = SupabaseDB(config)

    def get_user_profile(self, req: UserRequest):
        if req.provider == "gmail":
            provider_service = GmailAPI(self.config)
        elif req.provider == "outlook":
            provider_service = OutlookAPI(self.config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        creds = provider_service.get_stored_credentials(req.email_address, self.supabase)
        res = provider_service.get_user_info(creds)

        return res
    
    def setup_pin(self, req: UserRequest, pin: str):
        try:
            res = self.supabase.update(
                table='users',
                data={'pin': pin},
                filters={'email_address': req.email_address}
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return res


        

