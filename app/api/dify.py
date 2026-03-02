from typing import List
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.schemas.request import (
    OverviewRequest, WritterRequest
)
from app.utility import clean_text
from config import Config
from app.schemas.response import (
    DifyResponse, OverviewResponse
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DifyAPI():
    def __init__(self, config: Config):
        self.config = config
    
    def get_summary(self, plain_text: str):
        url = self.config.DIFY_URL
        if not url:
            raise Exception("Dify URL is not configured")
            
        payload = {
            "inputs": {
                "email_text": clean_text(plain_text)[:4000],
            },
            "response_mode": "blocking",
            "user": "frontend-test"
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.DIFY_SUMMARY}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
        }
        
        try:
            session = requests.Session()
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.post(
                url=url,
                headers=headers,
                json=payload,
                verify=False,      
                timeout=(10, 500)
            )
            
            response.raise_for_status()
            
            return DifyResponse(**response.json())

        except Exception as e:
            print(f"Error in DifyAPI.get_summary: {e}")
            return None

    def get_writer(self, req: WritterRequest):
        url = self.config.DIFY_URL
        if not url:
            raise Exception("Dify URL is not configured")

        headers = {
            "Authorization": f"Bearer {self.config.DIFY_WRITER}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
        }

        payload = {
            "inputs": {
                **req.model_dump()
            },
            "response_mode": "blocking",
            "user": "frontend-test"
        }
        
        try:
            session = requests.Session()
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.post(
                url=url,
                headers=headers,
                json=payload,
                verify=False,      
                timeout=(10, 500)
            )
            
            response.raise_for_status()
            
            return response

        except Exception as e:
            print(f"Error in DifyAPI.get_overview: {e}")
            return None

    def get_overview(self, req: OverviewRequest):
        url = self.config.DIFY_URL
        if not url:
            raise Exception("Dify URL is not configured")

        headers = {
            "Authorization": f"Bearer {self.config.DIFY_OVERVIEW}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true"
        }

        payload = {
            "inputs": {
                **req.model_dump()
            },
            "response_mode": "blocking",
            "user": "frontend-test"
        }
        
        try:
            session = requests.Session()
            
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.post(
                url=url,
                headers=headers,
                json=payload,
                verify=False,      
                timeout=(10, 500)
            )
            
            response.raise_for_status()
            
            return response

        except Exception as e:
            print(f"Error in DifyAPI.get_overview: {e}")
            return None