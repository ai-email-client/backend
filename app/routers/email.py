from fastapi import APIRouter, HTTPException, Body
from app.providers.gmail import GmailProvider
from config import Config
from typing import Dict, Any

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

config = Config()

@router.post("/{provider}/fetch")
async def fetch_emails(
    token_data: Dict[str, Any]
):
    try:
        if token_data.get("provider") == "gmail":
            provider_service = GmailProvider(config)
        elif token_data.get("provider") == "outlook":
            provider_service = OutlookProvider(config)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        if token_data.get("limit") is None:
            limit = 5
        else:
            limit = token_data.get("limit")

        emails = provider_service.fetch_emails(token_data.get("token_data"), limit)
        
        return {"count": len(emails), "emails": emails}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))