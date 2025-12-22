from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from config import Config
from app import utility
from app.schemas.email import EmailShortResponse, EmailDetailResponse, EmailFetchRequest, EmailMessageRequest

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
        # // TODO: Save Refresh Token To Database and Use from Database
        return {
            'access_token': creds.token,
            'refresh_token': creds.refresh_token
        }

    def fetch_emails(self, req: EmailFetchRequest) -> List[EmailShortResponse]:
        try:
            service = self.build_service(req.token_data)

            results = service.users().messages().list(userId='me', maxResults=req.limit).execute()
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

                    email_list.append(EmailShortResponse(
                        id=msg['id'],
                        subject=subject,
                        sender=sender,
                        snippet=snippet,
                    ))

            return email_list

        except Exception as e:
            raise Exception(f"Error function fetch_emails: {str(e)}")

    def get_message_by_id(self, req: EmailMessageRequest) -> EmailDetailResponse:
        try:
            service = self.build_service(req.token_data)

            result = service.users().messages().get(userId='me',id=req.message_id).execute()
            payload = utility.get_payload(result)

            subject = utility.get_email_subject(payload)
            sender = utility.get_email_sender(payload)
            snippet = utility.get_email_snippet(result)

            parts = utility.get_email_parts(payload)
            code = utility.get_part_by_mimetype(payload, 'text/plain')
            plain_text = utility.get_decode_by_mimetype(code, 'text/plain')

            return EmailDetailResponse(
                id=req.message_id,
                subject=subject,
                sender=sender,
                snippet=snippet,
                body=utility.clean_text(plain_text)
            )

        except Exception as e:
            raise Exception(f"Error function get_message_by_id: {str(e)}")