from http.client import HTTPException
from time import time
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
    MessageModifyLabelRequest
)

class DifyService():
    def __init__(self, config: Config, db: SupabaseDB = None):
        self.config = config
        self.db = db
    
    def send_to_dify(self, req: DataInsertSummaryRequest):
        self.db.upsert(
            table='source_emails',
            data={
                'id': req.id,
                'email_tags': req.email_tags,
                'status': Status.processing.value
                },
                on_conflict='id'
            )
        try:
            print(f"Starting Dify API request for id {req.id} in the background.", flush=True)
            dify_api = DifyAPI(self.config)
            res = dify_api.get_summary(req.plain_text[:4000])
            if res is None:
                print(f"Dify API Error for msg_id {req.id}", flush=True)
                self.db.upsert(
                    table='source_emails',
                    data={
                        'id': req.id,
                        'email_tags': req.email_tags,
                        'status': Status.error.value
                    },
                    on_conflict='id'
                )
                return
            print(f"Dify API Response time for id {req.id}: {res.data.elapsed_time}", flush=True)
            dify_res = res.data.outputs.clean_email
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
                
                if req.provider == "gmail":
                    provider_service = GmailAPI(self.config)
                elif req.provider == "outlook":
                    provider_service = OutlookAPI(self.config)
                else:
                    raise HTTPException(status_code=400, detail="Invalid provider")
                labels =provider_service.get_labels(req.current_user,self.db)
                req = MessageModifyLabelRequest(
                    id=req.msg_id,
                    addLabelIds=[label['id'] for label in labels if label['name'] == dify_res.email_category]
                )
                provider_service.message_modify_label(req, req.current_user, self.db)                    
                
                return
        except Exception as e:
            print(f"Exception for id {req.id}: {str(e)}", flush=True)