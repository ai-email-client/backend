from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.schemas.dify import Status
from app.schemas.email import Sender
from app.services.dify import DifyService
from app.services.database import DatabaseService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest,
    OverviewRequest,
    UserRequest
)
from app.services.email import EmailService
from dependencies import (   
    get_current_user, 
    get_dify_service, 
    get_database_service,
    get_email_service
)

router = APIRouter(
    prefix="/dify",
    tags=["dify"]
)


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
        source_email = database_service.get_source_email(
            req.msg_id, 
            current_user.email_address
        )
        if source_email:

            summary_record = database_service.get_summary(source_email.id)
            status = source_email.status
            
            temp = source_email.model_dump()
            dify_req = DataInsertSummaryRequest(
                **temp, 
                current_user=current_user, 
                sender=req.sender
                )
            
            if summary_record:
                if status == Status.done.value:
                    print(f"Summary for msg_id {source_email.id} already exists. Returning existing summary.", flush=True)
                    
                    if summary_record.email_category:
                        label = email_service.get_label_by_name(summary_record.email_category, current_user)
                        if label.id not in req.email_tags and label.id:
                            print(f"Summary for msg_id {source_email.id} is done. Updating labels.", flush=True)
                            background_tasks.add_task(
                                email_service.update_message_labels, 
                                msg_id=source_email.msg_id, 
                                label_id=label.id, 
                                current_user=current_user
                            )
                    if summary_record.sender is not None:
                        sender = Sender(
                            name=req.sender,
                            type=summary_record.sender.type
                        )
                        background_tasks.add_task(
                            database_service.upsert_sender, 
                            source_email_id=source_email.id,
                            sender=sender
                        )             
                    return summary_record
                elif status == Status.processing.value:
                    print(f"Summary for msg_id {req.msg_id} is still processing.", flush=True)
                    return 
                else:
                    print(f"Previous Dify API request for msg_id {req.msg_id} resulted in an error. Retrying...", flush=True)
                    background_tasks.add_task(dify_service.send_to_summary, dify_req)
                    return 
            else:
                print(f"No existing summary record for msg_id {req.msg_id}. Sending to Dify for processing.", flush=True)
                background_tasks.add_task(dify_service.send_to_summary, dify_req)
                return 
        else:
            inserted = database_service.upsert_email_source(req=req, user_email=current_user.email_address)
            if inserted is None:
                raise HTTPException(status_code=400, detail="Failed to insert email source") 
            print(f"No existing summary request for msg_id {inserted.id}. Creating new request.", flush=True)
            dify_req = DataInsertSummaryRequest(**inserted.model_dump(), sender=req.sender, current_user=current_user)
            database_service.upsert_status(source_email_id=inserted.id, status=Status.processing.value)            
            background_tasks.add_task(dify_service.send_to_summary, dify_req)
        
        return 
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_overview(
    current_user: UserRequest = Depends(get_current_user),
    database_service: DatabaseService = Depends(get_database_service),
    dify_service: DifyService = Depends(get_dify_service)
):
    try:
        res = None

        data = database_service.get_overview(current_user.email_address)
        if data is None:
            raise HTTPException(status_code=404, detail="No overview data found")
        
        res = dify_service.send_to_overview(data)
        if res is None:
            raise HTTPException(status_code=404, detail="Overview request failed")
        return res
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))
