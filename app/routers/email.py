from fastapi import APIRouter, HTTPException, Depends
from app.schemas.category import Category
from app.schemas.email import Format, Message
from app.schemas.response import CategoryListResponse, MessagesResponse
from config import Config

from app.schemas.request import (
    UserRequest,
    EmailFetchRequest,
    MessageBatchDeleteRequest,
    CreateLabelRequest,
    MessageModifyLabelRequest,
    MessageBatchModifyLabelRequest,
    SyncLabelsRequest,
    CreateDraftRequest,
)
from app.schemas.query import (
    DraftQueryParam,
    DraftsQueryParams,
    MessageParam,
    MessagesParam,
)

from dependencies import get_current_user, get_email_service
from app.services.email import EmailService

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/initialize/labels")
async def initialize_labels(
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.initialize_labels(current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/messages")
async def fetch_emails(
    param: MessagesParam = Depends(),
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        msgs = email_service.fetch_emails(param, current_user)

        res = email_service.get_message_batch(msgs=msgs, current_user=current_user)

        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/message/{msg_id}")
async def get_message_by_id(
    msg_id: str,
    param: MessageParam = Depends(),
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_message_by_id(msg_id, param, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/labels")
async def get_labels(
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_labels(current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/message/{msg_id}/attachments/{attachment_id}")
async def get_attachments(
    msg_id: str,
    attachment_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_attachments(msg_id, attachment_id, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/label/create")
async def create_label(
    req: CreateLabelRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.create_label(req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/labels/sync")
async def sync_labels(
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.sync_labels(current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/label/{label_id}")
async def get_label_by_id(
    label_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_label_by_id(label_id, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/message/modify")
async def modify_label(
    req: MessageModifyLabelRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.message_modify_label(req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/message/batch_modify")
async def batch_modify_label(
    req: MessageBatchModifyLabelRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.message_batch_modify_label(req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.delete("/message/{msg_id}")
async def delete_message(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.message_delete(msg_id, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/message/batch_delete")
async def batch_delete_message(
    req: MessageBatchDeleteRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.message_batch_delete(req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.put("/message/trash/{msg_id}")
async def trash_message(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        email_service.message_trash(msg_id, current_user)
        return HTTPException(status_code=200, detail="Message trashed successfully")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.put("/message/untrash/{msg_id}")
async def untrash_message(
    msg_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        email_service.message_untrash(msg_id, current_user)
        return HTTPException(status_code=200, detail="Message untrashed successfully")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/draft/create")
async def create_draft(
    req: CreateDraftRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.create_draft(req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.delete("/draft/{draft_id}")
async def delete_draft(
    draft_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        email_service.delete_draft(draft_id, current_user)
        return HTTPException(status_code=200, detail="Draft deleted successfully")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/draft/{draft_id}")
async def get_draft(
    draft_id: str,
    params: DraftQueryParam = Depends(),
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_draft(draft_id, current_user, params.format)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.get("/drafts")
async def get_drafts(
    params: DraftsQueryParams = Depends(),
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.get_drafts(params, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.put("/draft/{draft_id}")
async def update_draft(
    draft_id: str,
    req: CreateDraftRequest,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.update_draft(draft_id, req, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@router.post("/draft/{draft_id}/send")
async def send_draft(
    draft_id: str,
    current_user: UserRequest = Depends(get_current_user),
    email_service: EmailService = Depends(get_email_service),
):
    try:
        res = email_service.send_draft(draft_id, current_user)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
