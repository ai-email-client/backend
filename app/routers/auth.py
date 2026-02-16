from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from dependencies import get_auth_service
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.get("/login/{provider}")
async def login(
    provider: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    
    res = auth_service.get_authorization_url(provider)

    url = res[0]
    state = res[1]
    
    return {"url": url, "state": state}

@router.get("/callback/{provider}")
async def callback(
    provider: str,
    state: str,
    code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        url = auth_service.handle_oauth_callback(provider, code, state)
        return RedirectResponse(url=url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))