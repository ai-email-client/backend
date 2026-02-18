from time import time
from app.api.dify import DifyAPI
from config import Config
from database import SupabaseDB

from app.schemas.dify import (
    Status
)
from app.schemas.request import (
    DataInsertSummaryRequest
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
        except Exception as e:
            print(f"Exception for id {req.id}: {str(e)}", flush=True)