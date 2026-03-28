import logging
from typing import List, Optional
from app.schemas.dify import Status
from app.schemas.email import Sender
from app.schemas.request import (
    DifySummaryRequest
)
from app.schemas.response import (
    OverviewResponse,
    SpamResponse,
    SourceEmailResponse, 
    EmailAIAnalysisResponse
)
from config import Config
from database import SupabaseDB
from app.utility import clean_content

logger = logging.getLogger(__name__)

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
                    "summary","importance","is_spam","is_threat",
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
        columns = [ "id","msg_id","text_plain","email_tags","status","user_email_address" ]
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
            "summary",
            "importance",
        ]
        columns_str = ', '.join(columns)

        res = self.db.select(
            table='email_ai_analysis',
            columns=f"{columns_str}, source_emails!inner(msg_id, user_email_address, email_tags)",
            eq={
                'source_emails.user_email_address': email_address
            }
        )

        if not res:
            return None

        overview_results = []
        for r in res:
            source = r.pop('source_emails', {}) or {}

            email_tags = source.get('email_tags', [])
            if 'UNREAD' not in email_tags:
                continue

            r['msg_id'] = source.get('msg_id')
            overview_results.append(OverviewResponse(**r))

        return overview_results if overview_results else None
    
    def get_spam(self, email_address: str):
        columns = [
            "source_email_id",
            "sender",
            "summary",
            "is_spam",
            "is_threat",
            "spam_type",
            "spam_confidence",
            "security_type",
            "security_confidence"
        ]
        columns_str = ', '.join(columns)

        res = self.db.select(
            table='email_ai_analysis',
            columns=f"{columns_str}, source_emails!inner(msg_id, user_email_address)",
            eq={
                'source_emails.user_email_address': email_address,
                'is_spam': True
            }
        )

        if not res:
            return None

        spam_results = []
        for r in res:
            source = r.pop('source_emails', {}) or {}
            r['msg_id'] = source.get('msg_id') 
            spam_results.append(SpamResponse(**r))

        return spam_results if spam_results else None

    def get_source_email_with_summary(self, msg_id: str, user_email: str):
        result = self.db.select(
            table='source_emails',
            columns='*, email_ai_analysis(*)',
            eq={
                'msg_id': msg_id,
                'user_email_address': user_email
            }
        )

        if not result:
            return None, None

        data = result[0]
        summary = result[0]['email_ai_analysis']
        source = SourceEmailResponse(**data)
        summary_record = EmailAIAnalysisResponse(**summary[0]) if summary else None
        return source, summary_record

    def get_source_emails_with_summary_batch(
        self, msg_ids: List[str], user_email: str
    ) -> dict[str, tuple[SourceEmailResponse, Optional[EmailAIAnalysisResponse]]]:

        rows = self.db.select_in(
            table='source_emails',
            columns='*, email_ai_analysis(*)',
            in_filter={'msg_id': msg_ids},
            eq={'user_email_address': user_email},
        )

        output = {}
        for row in (rows or []):
            summary_data = row.pop('email_ai_analysis', None)
            if isinstance(summary_data, list):
                summary_data = summary_data[0] if summary_data else None

            try:
                source = SourceEmailResponse(**row)
            except Exception as e:
                logger.warning(f"[Batch] SourceEmailResponse parse error: {e}")
                continue

            summary = None
            if summary_data:
                try:
                    summary = EmailAIAnalysisResponse(**summary_data)
                except Exception as e:
                    logger.warning(f"[Batch] EmailAIAnalysisResponse parse error: {e}")

            output[source.msg_id] = (source, summary)

        return output

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
                'text_plain': req.text_plain,
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
        text_plain = clean_content(req.text_plain)
        res = self.db.upsert(
            table='source_emails',
            data={
                'msg_id': req.msg_id,
                'text_plain': text_plain,
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

    