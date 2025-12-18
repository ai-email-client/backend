from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GmailProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config