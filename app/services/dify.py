from typing import List
import time
from app.api.dify import DifyAPI
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from config import Config
from database import SupabaseDB

from app.schemas.dify import (
    Status
)
from app.schemas.request import (
    DataInsertSummaryRequest,
    MessageModifyLabelRequest,
    OverviewItemRequest,
    OverviewRequest,
)
from app.schemas.response import (
    OverviewResponse
)

class DifyService():
    def __init__(self, config: Config, db: SupabaseDB):
        self.config = config
        self.db = db
    
    def send_to_summary(self, req: DataInsertSummaryRequest):
        time.sleep(5)
        try:
            print(f"Starting Dify API request for id {req.id} in the background.", flush=True)
            dify_api = DifyAPI(self.config)
            res = dify_api.get_summary(req.plain_text)
            if res is None:
                self.db.upsert(
                    table='source_emails',
                    data={
                        'id': req.id,
                        'email_tags': req.email_tags,
                        'status': Status.error.value
                    },
                    on_conflict='id'
                )
                raise Exception(f"Dify API Response is None for id {req.id}")
            
            if res.data is None:
                raise Exception(f"Dify API Response Error:{req.id}")
            if res.data.outputs is None:
                raise Exception(f"Dify API Response Output is None for id {req.id}")
            if res.data.outputs.clean_email is None:
                raise Exception(f"Dify API Response Summary is None for id {req.id}")
            
            print(f"Dify API Response time for id {req.id}: {res.data.elapsed_time}", flush=True)
            
            dify_res = res.data.outputs.clean_email
            if dify_res.sender is not None and dify_res.sender.name is None:
                dify_res.sender.name = req.sender

            if dify_res is not None:
                self.db.upsert(
                    table='source_emails',
                    data={
                        'id': req.id,
                        'email_tags': req.email_tags,
                        'status': Status.done.value
                    },
                    on_conflict='id'
                )
                self.db.upsert(
                    table='email_ai_analysis',
                    data={
                        'source_email_id': req.id,
                        **dify_res.model_dump(),
                    },
                    on_conflict='source_email_id' 
                )
                print(f"Inserted AI analysis for id {req.id} successfully", flush=True)
                
                if req.current_user.provider == "gmail":
                    provider_service = GmailAPI(self.config)
                elif req.current_user.provider == "outlook":
                    provider_service = OutlookAPI(self.config)
                else:
                    raise Exception(f"Invalid provider for id {req.id}")
                
                if dify_res.email_category is None:
                    raise Exception(f"Email category not found for id {req.id}")
                
                label = provider_service.get_label_by_name(dify_res.email_category, req.current_user, self.db)
                if label is None:
                    raise Exception(f"Label {dify_res.email_category} not found for user {req.current_user.email_address}")
                if label.id:
                    req_mod = MessageModifyLabelRequest(
                        id=req.msg_id,
                        addLabelIds=[label.id], 
                        removeLabelIds=[]
                    )
                    provider_service.message_modify_label(req_mod, req.current_user, self.db)                    
                
                return
        except Exception as e:
            print(f"Exception for id {req.id}: {str(e)}", flush=True)

    def send_to_overview(self, req: List[OverviewResponse]):
        dify_api = DifyAPI(self.config)
        dify_req = []
        for item in req:
            dify_req.append(OverviewItemRequest(
                sender=item.sender,
                email_category=item.email_category,
                summary=item.summary
            ))
        
        res = dify_api.get_overview(OverviewRequest(data=dify_req))
        return res
    
        