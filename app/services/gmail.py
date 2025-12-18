from typing import Dict, Any
from config import Config
from app.providers.gmail import GmailProvider

class GmailService:
    def __init__(self, config: Config):
        self.config = config    