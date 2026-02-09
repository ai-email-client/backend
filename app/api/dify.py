import requests
import json
from config import Config
from app.schemas.request import (
    DifySummaryRequest
)
from app.schemas.response import (
    DifyResponse
)
from app.utility import html_to_text

class DifyAPI():
    def __init__(self, config: Config):
        self.config = config
    
    def get_summary(self, req: DifySummaryRequest) -> DifyResponse:
        payload = {
            "inputs": {
                "email_text": req.plain_text,
            },
            "response_mode": "blocking",
            "user": "frontend-test"
        }

        try:
            response = requests.post(
                url=self.config.DIFY_URL,
                headers={
                    "Authorization": f"Bearer {self.config.DIFY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            if response.json().get("error"):
                print(response.json())
                raise Exception(f"Error function get_summary: {response.json().get('error')}")
            return DifyResponse(**response.json())
        except Exception as e:
            raise Exception(f"Error function get_summary: {str(e)}")
