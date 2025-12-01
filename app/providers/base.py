from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class EmailProvider(ABC):
    @abstractmethod
    def login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate with the email provider.
        :param credentials: Dictionary containing authentication details (e.g., token, email, password)
        :return: Dictionary with user info or success message
        """
        pass

    @abstractmethod
    def fetch_emails(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch emails from the provider.
        :param limit: Number of emails to fetch
        :return: List of email dictionaries
        """
        pass
