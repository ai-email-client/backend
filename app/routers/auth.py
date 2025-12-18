from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from config import Config
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

config = Config()

@router.get("/{provider}/login")
async def login(provider: str):
    if provider == "gmail":
        provider_service = GmailProvider(config)
    elif provider == "outlook":
        provider_service = OutlookProvider(config)
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    auth_url = provider_service.login()
    
    return RedirectResponse(url=auth_url)

@router.get("/{provider}/callback")
async def callback(
    provider: str,
    code: str
):
    try:
        if provider == "gmail":
            provider_service = GmailProvider(config)
        elif provider == "outlook":
            provider_service = OutlookProvider(config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
        
        token_data = provider_service.exchange_code_for_token(code)
        
        return {"provider": provider, "token_data": token_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))