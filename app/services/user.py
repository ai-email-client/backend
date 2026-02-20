from app.utility import hash_pin, verify_pin
from config import Config
from database import SupabaseDB
from fastapi import HTTPException

from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from app.schemas.request import UserRequest

class UserService:
    def __init__(self, config: Config, db: SupabaseDB):
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
            if creds is None:
                raise HTTPException(status_code=404, detail="Credentials not found for user")
            res = provider_service.get_user_info(creds)
            if res is None:
                raise HTTPException(status_code=404, detail="User not found")
            return res
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def setup_pin(self, req: UserRequest, pin: str, db: SupabaseDB):
        if self.config.SECRET_KEY is None:
            raise HTTPException(status_code=400, detail="Secret key not found")
        
        pin = hash_pin(pin, self.config.SECRET_KEY)
        try:
            db.upsert(
                table='users',
                data={
                    'pin': pin, 
                    'email_address': req.email_address
                },
                on_conflict='email_address'
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def verify_pin(self, req: UserRequest, pin: str, db: SupabaseDB):
        if self.config.SECRET_KEY is None:
            raise HTTPException(status_code=400, detail="Secret key not found")
        res = db.select(
            table='users',
            columns='pin',
            eq={'email_address': req.email_address}
        )
        if res is None:
            raise HTTPException(status_code=404, detail="User not found")
        if res[0]['pin']!= pin:
            raise HTTPException(status_code=401, detail="Invalid PIN")
        
        return  verify_pin(pin, res[0]['pin'], self.config.SECRET_KEY)
        