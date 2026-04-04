import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from app.core.queue import enqueue_summary, is_queued
from app.schemas.dify import Status
from app.schemas.email import Sender
from app.schemas.query import MessageParam
from app.services.dify import DifyService
from app.services.database import DatabaseService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryBatchRequest,
    DifySummaryRequest,
    WritterRequest,
    UserRequest,
    TestSummaryRequest
)
from app.services.email import EmailService
from app.utility import clean_content
from dependencies import (
    get_current_user,
    get_dify_service,
    get_database_service,
    get_email_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dify", tags=["dify"])

@router.post("/summary")
async def set_summary(
    req: DifySummaryRequest,
    current_user: UserRequest = Depends(get_current_user),
    dify_service: DifyService = Depends(get_dify_service),
    database_service: DatabaseService = Depends(get_database_service),
    email_service: EmailService = Depends(get_email_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        source_email, summary_record = database_service.get_source_email_with_summary(
            req.msg_id, current_user.email_address
        )

        if source_email is not None:
            dify_req = DataInsertSummaryRequest(
                **source_email.model_dump(), current_user=current_user, sender=req.sender
            )
            status = source_email.status

            if summary_record:
                if status == Status.done.value:
                    if summary_record.email_category:
                        label = email_service.get_label_by_name(
                            summary_record.email_category, current_user
                        )
                        if label and label.id and label.id not in req.email_tags:
                            background_tasks.add_task(
                                email_service.update_message_labels,
                                msg_id=source_email.msg_id,
                                addLabelIds=[label.id],
                                current_user=current_user,
                            )
                    if summary_record.is_spam:
                        background_tasks.add_task(
                            email_service.update_message_labels,
                            msg_id=source_email.msg_id,
                            addLabelIds=["SPAM"],
                            current_user=current_user,
                        )
                    if summary_record.sender is not None:
                        background_tasks.add_task(
                            database_service.upsert_sender,
                            source_email_id=source_email.id,
                            sender=Sender(name=req.sender, type=summary_record.sender.type),
                        )
                    return {"status": "done", "msg_id": req.msg_id, **summary_record.model_dump()}

                elif status == Status.processing.value:
                    if not is_queued(str(source_email.id)):
                        logger.warning(f"msg_id={req.msg_id} processing but not queued. Re-queuing.")
                        await enqueue_summary(dify_service.send_to_summary, dify_req)
                    return {"status": "processing", "msg_id": req.msg_id}

                else:
                    database_service.upsert_status(
                        source_email_id=source_email.id,
                        status=Status.processing.value
                    )
                    await enqueue_summary(dify_service.send_to_summary, dify_req)
                    return {"status": "queued", "msg_id": req.msg_id}

            else:
                labelId = [item for item in req.email_tags if item.startswith("Label_")]
                if labelId:
                    background_tasks.add_task(
                        email_service.update_message_labels,
                        msg_id=source_email.msg_id,
                        removeLabelIds=labelId,
                        current_user=current_user,
                    )
                is_spam = "SPAM" in req.email_tags
                print(f"is_spam: {is_spam}")
                if is_spam:
                    background_tasks.add_task(
                        email_service.update_message_labels,
                        msg_id=source_email.msg_id,
                        removeLabelIds=["SPAM"],
                        current_user=current_user,
                    )
                await enqueue_summary(dify_service.send_to_summary, dify_req)
                return {"status": "queued", "msg_id": req.msg_id}

        else:
            inserted = database_service.upsert_email_source(
                req=req, user_email=current_user.email_address
            )
            if inserted is None:
                raise HTTPException(status_code=400, detail="Failed to insert email source")

            dify_req = DataInsertSummaryRequest(
                **inserted.model_dump(), sender=req.sender, current_user=current_user
            )
            database_service.upsert_status(
                source_email_id=inserted.id, status=Status.processing.value
            )
            await enqueue_summary(dify_service.send_to_summary, dify_req)
            return {"status": "queued", "msg_id": req.msg_id}
    except Exception as e:
        logger.error(f"Error in set_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summary/batch")
async def set_summary_batch(
    req: DifySummaryBatchRequest,
    current_user: UserRequest = Depends(get_current_user),
    dify_service: DifyService = Depends(get_dify_service),
    database_service: DatabaseService = Depends(get_database_service),
    email_service: EmailService = Depends(get_email_service),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    try:
        msg_ids = [e.msg_id for e in req.emails]

        source_map = database_service.get_source_emails_with_summary_batch(
            msg_ids, current_user.email_address
        )

        res = []
        for email_req in req.emails:
            source_email, summary_record = source_map.get(email_req.msg_id, (None, None))

            if source_email is not None:
                dify_req = DataInsertSummaryRequest(
                    **source_email.model_dump(), current_user=current_user, sender=email_req.sender
                )
                status = source_email.status

                if summary_record:
                    if status == Status.done.value:
                        if summary_record.email_category or summary_record.is_spam:
                            label_ids = []

                            if summary_record.email_category:
                                label = email_service.get_label_by_name(
                                    summary_record.email_category, current_user
                                )
                                if label and label.id and label.id not in email_req.email_tags:
                                    label_ids.append(label.id)

                            if summary_record.is_spam:
                                label_ids.append("SPAM")

                            if label_ids:
                                background_tasks.add_task(
                                    email_service.update_message_labels,
                                    msg_id=source_email.msg_id,
                                    addLabelIds=label_ids,
                                    current_user=current_user,
                                )
                        if summary_record.sender is not None:
                            background_tasks.add_task(
                                database_service.upsert_sender,
                                source_email_id=source_email.id,
                                sender=Sender(name=email_req.sender, type=summary_record.sender.type),
                            )
                        res.append({"msg_id": email_req.msg_id, "status": "done", **summary_record.model_dump()})
                        continue

                    elif status == Status.processing.value:
                        if not is_queued(str(source_email.id)):
                            await enqueue_summary(dify_service.send_to_summary, dify_req)
                        res.append({"msg_id": email_req.msg_id, "status": "processing"})
                        continue

                    else:
                        database_service.upsert_status(
                            source_email_id=source_email.id,
                            status=Status.processing.value
                        )
                        await enqueue_summary(dify_service.send_to_summary, dify_req)
                        res.append({"msg_id": email_req.msg_id, "status": "queued"})
                        continue

                else:
                    await enqueue_summary(dify_service.send_to_summary, dify_req)
                    res.append({"msg_id": email_req.msg_id, "status": "queued"})
                    continue

            else:
                inserted = database_service.upsert_email_source(
                    req=email_req, user_email=current_user.email_address
                )
                if inserted is None:
                    res.append({"msg_id": email_req.msg_id, "status": "error"})
                    continue

                dify_req = DataInsertSummaryRequest(
                    **inserted.model_dump(), sender=email_req.sender, current_user=current_user
                )
                database_service.upsert_status(
                    source_email_id=inserted.id, status=Status.processing.value
                )
                await enqueue_summary(dify_service.send_to_summary, dify_req)
                res.append({"msg_id": email_req.msg_id, "status": "queued"})

        return res
    except Exception as e:
        logger.error(f"Error in set_summary_batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_overview(
    current_user: UserRequest = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service),
):
    try:
        res = database_service.get_overview(current_user.email_address)
        if res is None:
            return HTTPException(status_code=404, detail="No overview data found")

        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@router.post("/writter")
async def writter(
    req: WritterRequest,
    dify_service: DifyService = Depends(get_dify_service),
):
    try:
        res = dify_service.send_to_writter(req)
        if res is None:
            return HTTPException(status_code=404, detail="Writter request failed")
        print(res, flush=True)
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@router.post("/summary_test")
async def summary(
    req: TestSummaryRequest,
    dify_service: DifyService = Depends(get_dify_service),
):
    try:
        res = await dify_service.test_summary(plain_text=req.email_text)
        if res is None:
            return HTTPException(status_code=404, detail="Summary request failed")
        return res
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))