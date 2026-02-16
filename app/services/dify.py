import requests
import json
from app.api.dify import DifyAPI
from config import Config

from app.schemas.dify import (
    DifySummary,
    Status
)
from app.schemas.request import (
    DataInsertSummaryRequest,
    DifySummaryRequest
)
from app.utility import html_to_text
from database import SupabaseDB

class DifyService():
    def __init__(self, config: Config):
        self.config = config
        self.db = SupabaseDB(config)
    
    def send_to_dify(self, req: DataInsertSummaryRequest):
        print(f"🚀 START Background Task: {req.msg_id}", flush=True)
        dify_api = DifyAPI(self.config)
        res = dify_api.get_summary(req.plain_text)
        summary = res.data.outputs
        if summary.clean_email is not None:
            self.db.upsert(
                table='source_emails',
                data={
                    'id': req.id,
                    'status': Status.done.value
                },
                conflict_target='id'
                
            )
            self.db.insert(
                table='email_ai_analysis',
                data={
                    'id': req.id,
                    **summary.clean_email.model_dump(mode='json')
                }
            )
             
        else:
            self.db.upsert(
                table='source_emails',
                data={
                    'id': req.id,
                    'status': Status.error.value
                },
                conflict_target='id'
            )
            