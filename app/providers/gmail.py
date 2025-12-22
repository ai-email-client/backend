from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from config import Config
from app import utility

class GmailProvider:
    def __init__(self, config: Config):
        self.config = config
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.insert',
            'https://www.googleapis.com/auth/gmail.labels',
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'https://www.googleapis.com/auth/gmail.settings.sharing',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]

    def login(self):
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.config.GOOGLE_CLIENT_ID,
                    "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_name": "Google",
                    "redirect_uris": ["http://localhost:8000/auth/gmail/callback"]
                }
            },
            scopes=self.scopes,
            redirect_uri="http://localhost:8000/auth/gmail/callback"
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return authorization_url
    
    def exchange_code_for_token(self, code: str):
        client_config = {
            "web": {
                "client_id": self.config.GOOGLE_CLIENT_ID,
                "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_name": "Google",
                "redirect_uris": ["http://localhost:8000/auth/gmail/callback"]
            }
        }

        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=self.scopes,
            redirect_uri="http://localhost:8000/auth/gmail/callback"
        )

        flow.fetch_token(code=code)
        creds = flow.credentials

        return {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }

    def fetch_emails(self, token_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        try:
            creds = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )

            service = build('gmail', 'v1', credentials=creds)

            results = service.users().messages().list(userId='me', maxResults=limit).execute()
            messages = results.get('messages', [])

            email_list = []
            if not messages:
                print("No messages found.")
            else:
                for msg in messages:
                    txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                    payload = utility.get_payload(txt)

                    subject = utility.get_email_subject(payload)
                    sender = utility.get_email_sender(payload)
                    snippet = utility.get_email_snippet(txt)

                    email_list.append({
                        "id": msg['id'],
                        "subject": subject,
                        "sender": sender,
                        "snippet": snippet,
                    })

            return email_list

        except Exception as e:
            raise Exception(f"Error fetching emails: {str(e)}")

    def get_message_by_id(self, token_data: Dict[str, Any], message_id: str) -> Dict[str, Any]:
        try:
            creds = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )

            service = build('gmail', 'v1', credentials=creds)

            txt = service.users().messages().get(userId='me', id=message_id).execute()
            payload = utility.get_payload(txt)

            subject = utility.get_email_subject(payload)
            sender = utility.get_email_sender(payload)
            snippet = utility.get_email_snippet(txt)

            parts = utility.get_email_parts(payload)
            plain_text = utility.get_plain_text(parts)

            return {
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "snippet": snippet,
                "body": utility.clean_text(plain_text)
            }

        except Exception as e:
            raise Exception(f"Error fetching message by id: {str(e)}")