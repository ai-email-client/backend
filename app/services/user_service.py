from typing import Dict, Any
from app.schemas.user_schema import UserLoginRequest
from app.providers.gmail import GmailProvider
from app.providers.outlook import OutlookProvider
from config import Config

class UserService:
    def __init__(self):
        self.config = Config()

    def _get_provider(self, provider_name: str):
        if provider_name == 'gmail':
            return GmailProvider()
        elif provider_name == 'outlook':
            return OutlookProvider()
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")

    def login_email(self, login_data: UserLoginRequest):
        if "gmail.com" in login_data.email:
            provider = self._get_provider('gmail')
            return provider.login(login_data.dict())
        elif "outlook.com" in login_data.email or "hotmail.com" in login_data.email:
            provider = self._get_provider('outlook')
            return provider.login(login_data.dict())
        else:
            provider = self._get_provider('outlook')
            return provider.login(login_data.dict())
