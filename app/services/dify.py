import time
import asyncio
from typing import List
from app.api.dify import DifyAPI
from app.api.gmail import GmailAPI
from app.api.outlook import OutlookAPI
from config import Config
from database import SupabaseDB
from app.utility import clean_content, parse_json_response

from app.schemas.dify import (
    Status,
    DifyDraft
)
from app.schemas.request import (
    DataInsertSummaryRequest,
    MessageModifyLabelRequest,
    OverviewItemRequest,
    OverviewRequest,
    WritterRequest
)
from app.schemas.response import (
    OverviewResponse
)

class DifyService():
    def __init__(self, config: Config, db: SupabaseDB):
        self.config = config
        self.db = db
    
    async def send_to_summary(self, req: DataInsertSummaryRequest):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_to_summary_sync, req)

    def _send_to_summary_sync(self, req: DataInsertSummaryRequest):
        print(f"Starting Dify API request for id {req.id} in the background.", flush=True)
        try:
            dify_api = DifyAPI(self.config)
            text = clean_content(req.text_plain)

            res = dify_api.get_summary(text)

            if res is None:
                raise ValueError(f"[{req.id}] res is None — Dify API returned None")
            if res.data.status != 'succeeded':
                raise ValueError(f"[{req.id}] Dify API returned status: {res.data.status} error: {res.data.error}")

            print(f"Dify API Response time for id {req.id}: {res.data.elapsed_time}", flush=True)

            dify_res = res.data.outputs.clean_email
            if dify_res.sender is not None and dify_res.sender.name is None:
                dify_res.sender.name = req.sender

            self.db.upsert(
                table='source_emails',
                data={'id': req.id, 'email_tags': req.email_tags, 'status': Status.done.value},
                on_conflict='id'
            )
            self.db.upsert(
                table='email_ai_analysis',
                data={'source_email_id': req.id, **dify_res.model_dump()},
                on_conflict='source_email_id'
            )
            try:
                if req.current_user.provider == "gmail":
                    provider_service = GmailAPI(self.config)
                elif req.current_user.provider == "outlook":
                    provider_service = OutlookAPI(self.config)
                else:
                    raise ValueError(f"Invalid provider: {req.current_user.provider}")

                if dify_res.email_category:
                    label = provider_service.get_label_by_name(
                        dify_res.email_category.lower(), req.current_user, self.db
                    )
                    if label and label.get("id"):
                        provider_service.message_modify_label(
                                MessageModifyLabelRequest(
                                    id=req.msg_id,
                                    addLabelIds=[label.get("id")],
                                    removeLabelIds=[]
                                ),
                                req.current_user,
                                self.db
                            )
            except Exception as label_err:
                print(f"[Warning] Label sync failed for id {req.id}: {label_err}", flush=True)

        except Exception as e:
            print(f"Exception for id {req.id}: {e}", flush=True)
            self.db.upsert(
                table='source_emails',
                data={'id': req.id, 'email_tags': req.email_tags, 'status': Status.error.value},
                on_conflict='id'
            )
            raise

    async def test_summary(self, plain_text: str):
        try:
            print(f"Starting Test Dify API request.", flush=True)
            dify_api = DifyAPI(self.config)
            res = await dify_api.test_summary(plain_text)
            
            return res
        except Exception as e:
            print(f"Exception for plain_text: {str(e)}", flush=True)

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
        return dify_req
    
    def send_to_writter(self, req: WritterRequest):
        dify_api = DifyAPI(self.config)
        req = WritterRequest(
            email_text=clean_content(req.email_text),
            ai_summary=clean_content(req.ai_summary),
            user_draft=clean_content(req.user_draft),
            topic=clean_content(req.topic),
            target_person=clean_content(req.target_person)
        )
        try:
            res = dify_api.get_writter(req)
            return DifyDraft(**parse_json_response(res.data.outputs.result))
        except Exception as e:
            print(f"Exception in send_to_writter: {str(e)}", flush=True)
            return None 