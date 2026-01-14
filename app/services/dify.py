import requests
import json
from config import Config
from app.schemas.email import DifySummaryRequest, EmailSummaryRequest
from app.utility import html_to_text

class DifyService():
    def __init__(self, config: Config):
        self.config = config
    
    def get_summary(self, req: DifySummaryRequest):
        try:
            req = DifySummaryRequest(
                inputs=EmailSummaryRequest(email_text=req.inputs.email_text),
                user="frontend-test",
                response_mode="blocking"
            )
            response = requests.post(
                url=self.config.DIFY_URL,
                headers={
                    "Authorization": f"Bearer {self.config.DIFY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=req.dict()
            )
            response = response.json()["data"]["outputs"]["clean_email"]
            return response
        except Exception as e:
            raise Exception(f"Error function get_summary: {str(e)}")
