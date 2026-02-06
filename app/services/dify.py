import requests
import json
from app.api.dify import DifyAPI
from config import Config
from app.schemas.dify import (
    DifySummaryRequest,
    DifySummaryResponse
)
from app.utility import html_to_text
from database import SupabaseDB

class DifyService():
    def __init__(self, config: Config):
        self.config = config
        self.db = SupabaseDB(config)
    
    def get_summary(self, req: DifySummaryRequest):
        res = self.db.select(
            table='source_emails',
            columns='msg_id , plain_text, email_tags, status',
            filters={'msg_id': req.msg_id}
        )
        
        if len(res.data) == 0:
            res =self.db.insert('source_emails', {
                'msg_id': req.msg_id,
                'plain_text': req.plain_text,
                'email_tags': req.email_tags,
                'status': "new"
            }
            )
            # dify_api = DifyAPI(self.config)
            # summary = dify_api.get_summary(req)
            return res
            
        else:
            # res = self.db.select(
            #     'email_ai_analysis',
            #     columns='msg_id, sender_type, email_category, summary',
            #     filters={'msg_id': req.msg_id}
            # )
            return res
        
