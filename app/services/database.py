from ast import List
from sqlalchemy import column
from app.schemas.dify import Status
from app.schemas.email import Sender
from app.schemas.request import (
    DifySummaryRequest
)
from app.schemas.response import (
    OverviewResponse,
    SourceEmailResponse, 
    EmailAIAnalysisResponse
)
from config import Config
from database import SupabaseDB

class DatabaseService():
    def __init__(self, config: Config, db: SupabaseDB):
        self.config: Config = config
        self.db: SupabaseDB = db
    
    def get_summary(self, 
                    source_email_id: str,
                    ):
        columns = [
                    "source_email_id","sender","email_category",
                    "date","time","location","instructions","required_items",
                    "summary","is_spam","is_threat",
                    "spam_type","spam_confidence",
                    "security_type","security_confidence",
                    "extraction_status","confidence"
                ]
        columns_str = ', '.join(columns)
            
        res = self.db.select(
            table='email_ai_analysis',
            columns = columns_str,
            eq={
                'source_email_id': source_email_id
                }
            )
        if res and len(res) > 0:
            return EmailAIAnalysisResponse(**res[0])
        return None
    
    def get_source_email(self,                     
                        msg_id: str,
                        email_address: str
        ):
        columns = [ "id","msg_id","plain_text","email_tags","status","user_email_address" ]
        columns_str = ', '.join(columns)
        
        res = self.db.select(
            table='source_emails',
            columns=columns_str,
            eq={
                'msg_id': msg_id,
                'user_email_address': email_address
                }
            )
        if res and len(res) > 0:
            return SourceEmailResponse(**res[0])
        return None

    def get_overview(self, email_address: str):
        columns = [
            "source_email_id",
            "sender",
            "email_category",
            "summary"
        ]
        columns_str = ', '.join(columns)

        res = self.db.select(
            table='email_ai_analysis',
            columns=f"{columns_str}, source_emails!inner(user_email_address)",
            eq={
                'source_emails.user_email_address': email_address
            },
            contains={
                'source_emails.email_tags': ['UNREAD']
            }
        )
        if res and len(res) > 0:
            overview_results = []
            for r in res:
                overview_results.append(OverviewResponse(**r))
            return overview_results
        return None

    def upsert_sender(self, source_email_id: str, sender: Sender):
        res = self.db.upsert(
            table='email_ai_analysis',
            data={
                'source_email_id': source_email_id,
                'sender': sender.model_dump()
            },
            on_conflict='source_email_id'
         )
        if res and len(res) > 0:
            return EmailAIAnalysisResponse(**res[0])
        return None
    
    def get_user_pin(self, email_address: str):
        res = self.db.select(
            table='google_accounts',
            columns='pin',
            eq={
                'email_address': email_address
                }
            )
        if res and len(res) > 0:
            return res[0].get('pin')
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
        if res and len(res) > 0:
            return SourceEmailResponse(**res[0])
        return None
    
    def upsert_email_source(self, req: DifySummaryRequest, user_email: str):
        res = self.db.upsert(
            table='source_emails',
            data={
                'msg_id': req.msg_id,
                'plain_text': req.plain_text,
                'email_tags': req.email_tags,
                'status': Status.new.value,
                'user_email_address': user_email,
                'created_at': 'now()'
            },
             on_conflict='msg_id'
         )
        if res and len(res) > 0:
            return SourceEmailResponse(**res[0])
        return None
    
    def upsert_email_tags(self, msg_id: str, email_tags: str):
        res = self.db.upsert(
            table='source_emails',
            data={
                'msg_id': msg_id,
                'email_tags': email_tags
            },
             on_conflict='msg_id'
         )
        if res and len(res) > 0:
            return SourceEmailResponse(**res[0])
        return None  

    def upsert_status(self, source_email_id: str, status: str):
        res = self.db.upsert(
            table='source_emails',
            data={
                'id': source_email_id,
                'status': status
            },
             on_conflict='id'
         )
        if res and len(res) > 0:
            return SourceEmailResponse(**res[0])
        return None

    