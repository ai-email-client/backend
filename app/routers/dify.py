from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from app.schemas.dify import Status
from app.services.dify import DifyService
from app.services.database import DatabaseService
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest,
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
                current_user=current_user
                )
            
            if summary_record:
                if status == Status.done.value:
                    print(f"Summary for msg_id {source_email.id} already exists. Returning existing summary.", flush=True)
                    labels = email_service.get_labels(current_user)
                    if labels is None:
                        raise HTTPException(status_code=400, detail="Labels not found")
                    
                    target_label_id = next((label.id for label in labels.categories if label.name == summary_record.email_category), None)
                    if target_label_id not in req.email_tags and target_label_id is not None:
                        print(f"Summary for msg_id {source_email.id} is done. Updating labels.", flush=True)
                        background_tasks.add_task(
                            email_service.update_message_labels, 
                            msg_id=source_email.msg_id, 
                            label_id=target_label_id, 
                            current_user=current_user
                        )             
                    return summary_record
                elif status == Status.processing.value:
                    print(f"Summary for msg_id {req.msg_id} is still processing.", flush=True)
                    return {"message": "Summary request is being processed in the background."}
                else:
                    print(f"Previous Dify API request for msg_id {req.msg_id} resulted in an error. Retrying...", flush=True)
                    background_tasks.add_task(dify_service.send_to_dify, dify_req)
                    return {"message": "Previous summary request resulted in an error. Retrying in the background."}
            else:
                print(f"No existing summary record for msg_id {req.msg_id}. Sending to Dify for processing.", flush=True)
                background_tasks.add_task(dify_service.send_to_dify, dify_req)
                return {"message": "Summary request submitted for processing."}
        else:
            inserted = database_service.upsert_email_source(req=req, user_email=current_user.email_address)
            if inserted is None:
                raise HTTPException(status_code=400, detail="Failed to insert email source") 
            print(f"No existing summary request for msg_id {inserted.id}. Creating new request.", flush=True)
            dify_req = DataInsertSummaryRequest(**inserted.model_dump(), current_user=current_user)
            database_service.upsert_status(source_email_id=inserted.id, status=Status.processing.value)            
            background_tasks.add_task(dify_service.send_to_dify, dify_req)
        
        return {"message": "Summary request submitted for processing."}
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail=str(e))

