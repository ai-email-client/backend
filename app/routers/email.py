from fastapi import APIRouter, HTTPException, Body, Depends
from config import Config
from typing import Dict, Any

from app.schemas.user import UserRequest

from app.schemas.email import (
    EmailFetchRequest, EmailMessageRequest, AttachmentRequest,
    MessageIdRequest, MessageBatchDeleteRequest
)

from app.schemas.category import (
    CreateLabelRequest, MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    GetLabelRequest
)

from app.services.email import EmailService

from app.utility import get_current_user

router = APIRouter(
    prefix="/email",
    tags=["email"]
)

config = Config()

@router.post("/initialize/labels")
async def initialize_labels(
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.initialize_labels(current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/messages")
async def fetch_emails(
    req: EmailFetchRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        return email_service.fetch_emails(req, current_user)
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/list/plain-text")
async def get_plain_text(
    req: EmailFetchRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.get_plain_text(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/get")
async def get_message_by_id(
    req: EmailMessageRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:

        email_service = EmailService(config)

        res = email_service.get_message_by_id(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/labels")
async def get_labels(
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.get_labels(current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))
        
@router.post("/message/attachment")
async def get_attachments(
    req: AttachmentRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.get_attachments(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/label/create")
async def create_label(
    req: CreateLabelRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.create_label(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/label/get")
async def get_label_by_id(
    req: GetLabelRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.get_label_by_id(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/modify")
async def modify_label(
    req: MessageModifyLabelRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_modify_label(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/batch-modify")
async def batch_modify_label(
    req: MessageBatchModifyLabelRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_batch_modify_label(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/delete")
async def delete_message(
    req: MessageIdRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_delete(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/batch-delete")
async def batch_delete_message(
    req: MessageBatchDeleteRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_batch_delete(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/trash")
async def trash_message(
    req: MessageIdRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_trash(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.post("/message/untrash")
async def untrash_message(
    req: MessageIdRequest,
    current_user: UserRequest = Depends(get_current_user)
):
    try:
        email_service = EmailService(config)

        res = email_service.message_untrash(req, current_user)

        return res
        
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))
