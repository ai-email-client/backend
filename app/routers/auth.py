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

@router.get("/login/{provider}")
async def login(provider: str):
    if provider == "gmail":
        provider_service = GmailProvider(config)
    elif provider == "outlook":
        provider_service = OutlookProvider(config)
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    auth_url = provider_service.login()
    
    return RedirectResponse(url=auth_url)

@router.get("/callback/{provider}")
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

        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']

        url = f"http://localhost:5173/#/?provider={provider}&access_token={access_token}&refresh_token={refresh_token}"
        print(access_token)
        print(refresh_token)
        return RedirectResponse(url=url, status_code=302)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))