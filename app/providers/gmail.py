import base64
from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from config import Config

class GmailProvider:
    def __init__(self, config: Config):
        self.config = config
        self.scopes = ['https://mail.google.com/', 'openid']
        
    def build_service(self, token: Dict[str, Any]):
        creds = Credentials(
            token=token.get('access_token'),
            refresh_token=token.get('refresh_token'),
            token_uri=self.config.GOOGLE_TOKEN_URI,
            client_id=self.config.GOOGLE_CLIENT_ID,
            client_secret=self.config.GOOGLE_CLIENT_SECRET,
            scopes=self.scopes
        )
        return build('gmail', 'v1', credentials=creds)
    
    def login(self):
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.config.GOOGLE_CLIENT_ID,
                    "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                    "auth_uri": self.config.GOOGLE_AUTH_URI,
                    "token_uri": self.config.GOOGLE_TOKEN_URI,
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_name": "Google",
                    "redirect_uris": [self.config.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=self.scopes,
            redirect_uri=self.config.GOOGLE_REDIRECT_URI
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
                "auth_uri": self.config.GOOGLE_AUTH_URI,
                "token_uri": self.config.GOOGLE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_name": "Google",
                "redirect_uris": [self.config.GOOGLE_REDIRECT_URI]
            }
        }

        flow = Flow.from_client_config(
            client_config=client_config,
            scopes=self.scopes,
            redirect_uri=self.config.GOOGLE_REDIRECT_URI
        )

        flow.fetch_token(code=code)
        creds = flow.credentials

        return {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token
        }

    def fetch_emails(self, token_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        try:
            service = self.build_service(token_data)

            results = service.users().messages().list(userId='me', maxResults=limit).execute()
            messages = results.get('messages', [])

            email_list = []
            if not messages:
                print("No messages found.")
            else:
                for msg in messages:
                    txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                    
                    payload = txt.get('payload', {})
                    headers = payload.get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
                    snippet = txt.get('snippet', '')


                    email_list.append({
                        "id": msg['id'],
                        "subject": subject,
                        "sender": sender,
                        "snippet": snippet,
                        "body": self._get_email_body(payload)
                    })

            return email_list

        except Exception as e:
            raise Exception(f"Error fetching emails: {str(e)}")

    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        if 'body' in payload and payload['body'].get('data'):
            return self._decode_base64(payload['body']['data'])
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    return self._get_email_body(part)
                
                if 'parts' in part:
                    found_html = self._get_email_body(part)
                    if found_html: 
                        return found_html

            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return self._get_email_body(part)
        
        return "" 

    def _decode_base64(self, data: str) -> str:
        try:
            padding = len(data) % 4
            if padding:
                data += '=' * (4 - padding)
            return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception:
            return ""