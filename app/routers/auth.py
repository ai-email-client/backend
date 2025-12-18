from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from config import Config

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

config = Config()
