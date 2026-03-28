from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app import utility
from app.schemas.query import AuthQueryParams, LoginQueryParams
from dependencies import get_auth_service
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_ORIGINS = {
    "web":      "http://localhost:5173/#/callback",
    "electron": "aiemailclient://callback",
}

@router.get("/login/{provider}")
async def login(
    provider: str,
    origin: str = "web",
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        res = auth_service.get_authorization_url(provider, origin)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
 
 
@router.get("/callback/{provider}/{origin}")
async def callback(
    provider: str,
    origin: str,
    params: AuthQueryParams = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        token = auth_service.handle_oauth_callback(provider, params.code, params.state, origin)
        print("Token:", token)
        return RedirectResponse(url=f"{FRONTEND_ORIGINS[origin]}?token={token}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))