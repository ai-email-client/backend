from typing import List, Dict, Any
from imap_tools import MailBox

class OutlookAPI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
