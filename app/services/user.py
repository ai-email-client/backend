from typing import List, Dict, Any
from app.providers.base import EmailProvider
from config import Config

class UserService:
    def __init__(self):
        self.config = Config()
        self.emails = []

    def login(self, credentials: Dict[str, Any]):
        pass

    def fetch_emails(self, limit: int = 10):
        pass

    def logout(self):
        pass

    def get_emails(self):
        pass
