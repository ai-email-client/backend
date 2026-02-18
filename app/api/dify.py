import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from app.schemas.response import DifyResponse 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DifyAPI():
    def __init__(self, config: Config):
        self.config = config
    
    def get_summary(self, plain_text: str):
        payload = {
            "inputs": {
                "email_text": plain_text,
            },
            "response_mode": "blocking",
            "user": "frontend-test"
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.DIFY_API_KEY}",
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
                url=self.config.DIFY_URL,
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