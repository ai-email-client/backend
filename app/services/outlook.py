from app.providers.outlook import OutlookProvider
from config import Config

class OutlookService:
    def __init__(self, config: Config):
        self.config = config