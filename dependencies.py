import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.schemas.request import UserRequest
from config import Config
from database import SupabaseDB
from app.services.database import DatabaseService
from app.services.dify import DifyService
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.email import EmailService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_config():
    return Config()

def get_db(config: Config = Depends(get_config)):
    return SupabaseDB(config)
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, get_config().SECRET_KEY, algorithms=[get_config().ALGORITHM])
        provider = payload.get("provider")
        email_address = payload.get("email_address")
        
        if provider is None:
            raise HTTPException(status_code=401, detail="Invalid Token: Missing provider")

        if email_address is None:
            raise HTTPException(status_code=401, detail="Invalid Token: Missing email")
            
        return UserRequest(provider=provider, email_address=email_address)
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
def get_dify_service(
    config: Config = Depends(get_config),
    db: SupabaseDB = Depends(get_db)
):
    return DifyService(config, db)

def get_database_service(
    config: Config = Depends(get_config),
    db: SupabaseDB = Depends(get_db)
):
    return DatabaseService(config, db)

def get_auth_service(
    config: Config = Depends(get_config),
    db: SupabaseDB = Depends(get_db)
):
    return AuthService(config, db)
def get_user_service(
    config: Config = Depends(get_config),
    db: SupabaseDB = Depends(get_db)
):
    return UserService(config, db)
def get_email_service(
    config: Config = Depends(get_config),
    db: SupabaseDB = Depends(get_db)
):
    return EmailService(config, db)
