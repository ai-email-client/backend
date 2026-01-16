from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from config import Config
from app import utility

from app.schemas.email import (
    EmailShortResponse, 
    Attachment, 
    EmailDetailResponse, 
    EmailFetchRequest, 
    EmailMessageRequest,
    EmailPlainResponse,
    EmailFetchPlainResponse
)

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

            results = service.users().messages().list(
                userId='me', 
                maxResults=req.limit,
                labelIds=req.label,
                pageToken=req.page_token
                ).execute()
            page_token = results.get('nextPageToken')
            messages = results.get('messages', [])

            email_list = []
            if not messages:
                print("No messages found.")
            else:
                for msg in messages:
                    results = service.users().messages().get(userId='me', id=msg['id']).execute()
                    payload = results['payload']

                    message_id = results['id']
                    subject = utility.get_email_header(payload, 'Subject')
                    sender = utility.get_email_header(payload, 'From')
                    snippet = results['snippet']

                    email_list.append(EmailShortResponse(
                        msg_id=message_id,
                        subject=subject,
                        sender=sender,
                        snippet=snippet,
                        time=utility.convert_timestamp_to_date(int(results['internalDate'])),
                        tag=results['labelIds'],
                        attachments=utility.get_attachments(payload)
                    ))

            return {
                'emails': email_list,
                'page_token': page_token
            }

        except Exception as e:
            raise Exception(f"Error function fetch_emails: {str(e)}")

    def get_message_by_id(self, req: EmailMessageRequest) -> EmailDetailResponse:
        try:
            service = self.build_service(req.token_data)

            result = service.users().messages().get(userId='me',id=req.message_id).execute()
            payload = result['payload']
            subject = utility.get_email_header(payload, 'Subject')
            sender = utility.get_email_header(payload, 'From')
            snippet = result['snippet']
            time = utility.convert_timestamp_to_date(int(result['internalDate']))
            tags = result['labelIds']

            html_part = utility.get_part_by_mimetype(payload, 'text/html')
            if html_part is not None:
                html = utility.get_decode_by_mimetype(html_part, 'text/html')
            else:
                html = None

            plain_text_part = utility.get_part_by_mimetype(payload, 'text/plain')
            if plain_text_part is not None:
                plain_text = utility.get_decode_by_mimetype(plain_text_part, 'text/plain')
                plain_text = utility.clean_text(plain_text)
            else:
                plain_text = None

            attachments = utility.get_attachments(payload)

            return EmailDetailResponse(
                msg_id=req.message_id,
                subject=subject,
                sender=sender,
                snippet=snippet,
                html=html,
                plain_text=plain_text,
                time=time,
                tag=tags,
                attachments=attachments,
            )

        except Exception as e:
            raise Exception(f"Error function get_message_by_id: {str(e)}")

    def get_plain_text(self, req: EmailFetchRequest): 
        try:
            service = self.build_service(req.token_data)

            results = service.users().messages().list(
                userId='me', 
                maxResults=req.limit,
                labelIds=req.label,
                pageToken=req.page_token
                ).execute()
            page_token = results.get('nextPageToken')
            messages = results.get('messages', [])

            email_list = []
            if not messages:
                print("No messages found.")
            else:
                for msg in messages:
                    results = service.users().messages().get(userId='me', id=msg['id']).execute()
                    payload = results['payload']

                    message_id = results['id']
                    subject = utility.get_email_header(payload, 'Subject')
                    sender = utility.get_email_header(payload, 'From')
                    snippet = results['snippet']

                    body = utility.get_part_by_mimetype(payload, 'text/html')
                    if body is not None:
                        body = utility.get_decode_by_mimetype(body, 'text/html')
                        body = utility.clean_html(body)
                        body = utility.clean_text(body)
                    else:
                        body = utility.get_part_by_mimetype(payload, 'text/plain')
                        body = utility.get_decode_by_mimetype(body, 'text/plain')
                        body = utility.clean_text(body)

                    email_list.append(EmailPlainResponse(
                        msg_id=message_id,
                        plain_text=body,
                        tag=results['labelIds'],
                    ))
            return EmailFetchPlainResponse(
                emails=email_list,
                page_token=page_token
            )
        except Exception as e:
            raise Exception(f"Error function get_plain_text: {str(e)}")
