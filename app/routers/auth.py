from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.services.auth import AuthService
from database import SupabaseDB
from config import Config

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

config = Config()
auth_service = AuthService(config)

@router.get("/login/{provider}")
async def login(provider: str):
    
    res = auth_service.get_authorization_url(provider)

    url = res[0]
    state = res[1]
    
    return {"url": url, "state": state}

@router.get("/callback/{provider}")
async def callback(
    provider: str,
    state: str,
    code: str
):
    try:
        url = auth_service.handle_oauth_callback(provider, code, state)
        return RedirectResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))