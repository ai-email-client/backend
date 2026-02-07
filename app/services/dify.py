import requests
import json
from app.api.dify import DifyAPI
from config import Config

from app.schemas.dify import (
    DifySummary,
    Status
)
from app.schemas.request import (
    DifySummaryRequest
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
        
        if len(res) == 0:
            res =self.db.insert('source_emails', {
                'msg_id': req.msg_id,
                'plain_text': req.plain_text,
                'email_tags': req.email_tags,
                'status': Status.new
            }
            )
            # dify_api = DifyAPI(self.config)
            # summary = dify_api.get_summary(req)
            return res
            
        else:
            if res and res[0].get('status') == Status.new: 
                
                dify_api = DifyAPI(self.config)
                summary = dify_api.get_summary(req)

                is_success = False
                if summary.data.error is None :
                    is_success = True

                new_status = Status.done if is_success else Status.error
                res = self.db.update(
                    table='source_emails',
                    data={'status': new_status},
                    filters={'msg_id': req.msg_id}
                )
                self.db.insert('email_ai_analysis',
                    {
                        'source_email_id': res[0].get('id'),
                        **summary.data.outputs.clean_email.model_dump()
                    }
                )

                return summary.data.outputs.clean_email


            return res
        
