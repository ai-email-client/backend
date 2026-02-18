from config import Config
from database import SupabaseDB
from fastapi import HTTPException

from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from app.schemas.request import UserRequest

class UserService:
    def __init__(self, config: Config, db: SupabaseDB = None):
        self.config = config
        self.db = db

    def get_user_profile(self, req: UserRequest):
        try:
            if req.provider == "gmail":
                provider_service = GmailAPI(self.config)
            elif req.provider == "outlook":
                provider_service = OutlookAPI(self.config)
            else:
                raise HTTPException(status_code=400, detail="Invalid provider")
            creds = provider_service.get_stored_credentials(req.email_address, self.db)
            res = provider_service.get_user_info(creds)

            return res
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def setup_pin(self, req: UserRequest, pin: str):
        try:
            res = self.db.update(
                table='google_accounts',
                data={'pin': pin},
                filters={'email_address': req.email_address}
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return res

    def verify_pin(self, req: UserRequest, pin: str):
        try:
            res = self.db.get(
                table='google_accounts',
                filters={'email_address': req.email_address}
            )
            if not res or 'data' not in res or len(res['data']) == 0:
                raise HTTPException(status_code=404, detail="User not found")
            stored_pin = res['data'][0].get('pin')
            if stored_pin is None:
                raise HTTPException(status_code=400, detail="PIN not set for user")
            return stored_pin == pin
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        

