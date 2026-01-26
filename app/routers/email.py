from fastapi import APIRouter, HTTPException, Body
from config import Config
from typing import Dict, Any

from app.schemas.email import (
    EmailFetchRequest, EmailMessageRequest, EmailSummaryRequest, 
    DifySummaryRequest,AttachmentRequest,GetRequest,
    MessageDeleteRequest, MessageBatchDeleteRequest
)

from app.schemas.category import (
    CreateLabelRequest, MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    GetLabelRequest
)

from app.services.email import EmailService

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

config = Config()

@router.post("/fetch")
async def fetch_emails(
    req: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        return email_service.fetch_emails(req)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/list/plain-text")
async def get_plain_text(
    req: EmailFetchRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_plain_text(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/get")
async def get_message_by_id(
    req: EmailMessageRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_message_by_id(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/summary")
async def get_summary(
    req: EmailSummaryRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_summary(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/labels")
async def get_labels(
    req: GetRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_labels(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/user")
async def get_user_profile(
    req: GetRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_user_profile(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/attachment")
async def get_attachments(
    req: AttachmentRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_attachments(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/label/create")
async def create_label(
    req: CreateLabelRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.create_label(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/label/get")
async def get_label_by_id(
    req: GetLabelRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.get_label_by_id(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/modify")
async def modify_label(
    req: MessageModifyLabelRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.message_modify_label(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/batch-modify")
async def batch_modify_label(
    req: MessageBatchModifyLabelRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.message_batch_modify_label(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/delete")
async def delete_message(
    req: MessageDeleteRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.message_delete(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/batch-delete")
async def batch_delete_message(
    req: MessageBatchDeleteRequest
):
    try:
        email_service = EmailService(config)

        res = email_service.message_batch_delete(req)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

