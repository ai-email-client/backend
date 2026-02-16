from app.schemas.dify import Status
from app.schemas.request import DifySummaryRequest
from config import Config
from database import SupabaseDB

class DatabaseService():
    def __init__(self, config: Config, db: SupabaseDB = None):
        self.config = config
        self.db = db
    
    def get_summary(self, 
                    msg_id: str,
                    email_address: str
                    ):
        res = self.db.select(
            table='source_emails',
            columns='id',
            filters={
                'msg_id': msg_id, 
                'user_email_address': email_address
                }
            )
        if res and 'data' in res and len(res['data']) > 0:
            source_email_id = res['data'][0].get('id')
            analysis_res = self.db.select(
                table='email_ai_analysis',
                columns='*',
                filters={
                    'source_email_id': source_email_id
                    }
                )
            return analysis_res
        
        return None

    
    def get_user_pin(self, email_address: str):
        res = self.db.select(
            table='google_accounts',
            columns='pin',
            filters={
                'email_address': email_address
                }
            )
        if res and 'data' in res and len(res['data']) > 0:
            return res['data'][0].get('pin')
        return None
    
    def insert_source_email(self, req: DifySummaryRequest, user_email: str):
        res = self.db.insert('source_emails', {
                'msg_id': req.msg_id,
                'plain_text': req.plain_text,
                'email_tags': req.email_tags,
                'status': Status.new.value,
                'user_email_address': user_email,
                'created_at': 'now()'
                
            }
        )
        return res
    
    def get_email_source(self, req: DifySummaryRequest, user_email:str):
        res = self.db.select(
            table='source_emails',
            columns='id, msg_id, plain_text, email_tags, status, user_email_address',
            filters={
                'msg_id': req.msg_id,
                'user_email_address': user_email
                }
            )
        return res