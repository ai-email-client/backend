from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2 import id_token
from googleapiclient import errors as google_api_errors

import time
import httplib2
import logging

from config import Config
from app import utility
from database import SupabaseDB

from app.schemas.auth import (
    CredentialResponse
)

from app.schemas.email import (
    EmailShortResponse, Attachment,EmailDetailResponse, 
    EmailFetchRequest, EmailMessageRequest,EmailPlainResponse,
    EmailFetchPlainResponse,AttachmentRequest,
    MessageIdRequest, MessageBatchDeleteRequest, EmailFetchResponse
)

from app.schemas.category import (
    Category,CategoryListResponse,MessageListVisibility,
    LabelListVisibility,CategoryType,CategoryColor,
    CreateLabelRequest, GetLabelRequest,
    MessageModifyLabelRequest, MessageBatchModifyLabelRequest,
    SyncLabelsRequest
)

from app.schemas.user import UserRequest

from exception import (
    CodeExchangeException,
    NoRefreshTokenException,
    NoUserIdException,
    FlowExchangeError
)

from app.schemas.category import INITIAL_LABELS

class GmailProvider:
    def __init__(self, config: Config):
        self.config = config
        self.scopes = [
            'https://mail.google.com/',
            'openid',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        self.client_config = {
            "web": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "auth_uri": config.GOOGLE_AUTH_URI,
                "token_uri": config.GOOGLE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_name": "Google",
                "redirect_uris": [config.GOOGLE_REDIRECT_URI]
            }
        }

    def build_service(self, 
        creds
    ):
        try:
            creds = Credentials(
                token=creds['access_token'],
                refresh_token=creds['refresh_token'],
                token_uri=self.config.GOOGLE_TOKEN_URI,
                client_id=self.config.GOOGLE_CLIENT_ID,
                client_secret=self.config.GOOGLE_CLIENT_SECRET,
                scopes=creds['scope'],
            )
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            return None
    
    def verify_oauth2_token(self, 
        creds
    ):
        time.sleep(2)
        return id_token.verify_oauth2_token(
            creds['id_token'], 
            requests.Request(), 
            audience=self.config.GOOGLE_CLIENT_ID
        )

    def exchange_code(self, 
        authorization_code: str
    ):
        """Exchange an authorization code for OAuth 2.0 credentials.

        Args:
            authorization_code: Authorization code to exchange for OAuth 2.0
                                credentials.

        Returns:
            oauth2client.client.OAuth2Credentials instance.

        Raises:
            CodeExchangeException: an error occurred.
        """
        flow = Flow.from_client_config(self.client_config, ' '.join(self.scopes))
        flow.redirect_uri = self.config.GOOGLE_REDIRECT_URI
        try:
            credentials = flow.fetch_token(code=authorization_code)
            return credentials
        except FlowExchangeError as error:
            logging.error('An error occurred: %s', error)
            raise CodeExchangeException(None)
    
    def get_user_info(self, 
        credentials
    ):
        """Send a request to the UserInfo API to retrieve the user's information.

        Args:
            credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                        request.

        Returns:
            User information as a dict.
        """
        user_info_service = self.build_service(credentials)

        user_info = None
        try:
            user_info = user_info_service.users().getProfile(userId='me').execute()
        except google_api_errors.HttpError as e:
            logging.error('An error occurred: %s', e)
        return user_info
    
    def get_authorization_url(self) -> str:
        """Retrieve the authorization URL.
        Returns:
            Authorization URL to redirect the user to.
        """
        flow = Flow.from_client_config(self.client_config, ' '.join(self.scopes))
        flow.redirect_uri = self.config.GOOGLE_REDIRECT_URI
        return flow.authorization_url()
    
    def get_credentials(self, 
        authorization_code: str,
        state: str,
        db: SupabaseDB
    ) -> Credentials:
        """Retrieve credentials using the provided authorization code.

        This function exchanges the authorization code for an access token and queries
        the UserInfo API to retrieve the user's e-mail address.

        If a refresh token has been retrieved along with an access token, it is stored
        in the application database using the user's e-mail address as key.

        Args:
            authorization_code: Authorization code to use to retrieve an access token.
            state: State to set to the authorization URL in case of error.

        Returns:
            oauth2client.client.OAuth2Credentials instance containing an access and
            refresh token.
        """
        try:
            credentials = self.exchange_code(authorization_code)
            user_info = self.verify_oauth2_token(credentials)
            if credentials.get('refresh_token') is not None:
                return self.store_credentials(user_info.get('email'), credentials, db)
            else:
                return self.get_stored_credentials(user_info.get('email'), db)
        except Exception as e:
            print(f"Error: {e}")

    def get_stored_credentials(
        self, 
        email_address: str, 
        db: SupabaseDB
    ):
        """Retrieved stored credentials for the provided user ID.

        Args:
            user_id: User's ID.

        Returns:
            Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
        """
        try:
            res = db.supabase.table("google_accounts").select(
                "credentials"
            ).eq(
                "email_address", email_address
            ).execute()
            if res.data:
                return res.data[0]['credentials']
            return None

        except Exception as e:
            print(f"Error: {e}")


    def store_credentials(self,
        email_address: str,
        credentials: Credentials,
        db: SupabaseDB
    ):
        """Store OAuth 2.0 credentials in the application's database.

        This function stores the provided OAuth 2.0 credentials using the user ID as
        key.

        Args:
            user_id: User's ID.
            credentials: OAuth 2.0 credentials to store.
        """
        try:
            res = db.supabase.table("google_accounts").upsert({
                "email_address": email_address,
                "credentials": credentials,
                "updated_at": "now()"
            },on_conflict="email_address").execute()
            return res.data[0]['credentials']
        except Exception as e:
            print(f"Error: {e}")
    
    def initialize_labels(self, 
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            for label in INITIAL_LABELS:
                service.users().labels().create(userId='me', body=label).execute()

            return {
                'message': "Labels initialized successfully"
            }
        except Exception as e:
            raise Exception(f"Error function initialize_labels: {str(e)}")

    def fetch_emails(self, 
        req: EmailFetchRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ) -> EmailFetchResponse:
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = service.users().messages().list(
                userId='me', 
                maxResults=req.limit,
                labelIds=req.label,
                pageToken=req.page_token
                ).execute()
            page_token = results.get('nextPageToken')
            messages_list = results.get('messages', [])

            messages = []
            if not messages_list:
                print("No messages found.")
            else:
                for msg in messages_list:
                    results = service.users().messages().get(userId='me', id=msg['id']).execute()
                    payload = results['payload']

                    message_id = results['id']
                    subject = utility.get_email_header(payload, 'Subject')
                    sender = utility.get_email_header(payload, 'From')
                    snippet = results['snippet']

                    messages.append(EmailShortResponse(
                        msg_id=message_id,
                        subject=subject,
                        sender=sender,
                        snippet=snippet,
                        time=utility.convert_timestamp_to_date(int(results['internalDate'])),
                        tag=results['labelIds'],
                        attachments=utility.get_attachments(payload)
                    ))
            return {
                'messages': messages,
                'page_token': page_token
            }

        except Exception as e:
            raise Exception(f"Error function fetch_emails: {str(e)}")

    def get_message_by_id(self, 
        req: EmailMessageRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ) -> EmailDetailResponse:
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            result = service.users().messages().get(userId='me',id=req.msg_id).execute()
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
                msg_id=req.msg_id,
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

    def get_plain_text(self, 
        req: EmailFetchRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ) -> EmailFetchResponse: 
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

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

    def get_labels(self, 
        current_user: UserRequest,
        db: SupabaseDB
    ) -> CategoryListResponse:
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            category_list = []
            for label in labels:
                category_list.append(Category(
                    id=label.get('id'),
                    name=label.get('name'),
                    messageListVisibility=MessageListVisibility(label.get('messageListVisibility', 'show')),
                    labelListVisibility=LabelListVisibility(label.get('labelListVisibility', 'labelShow')),
                    type=CategoryType(label.get('type')),
                    messagesTotal=label.get('messagesTotal', 0),
                    messagesUnread=label.get('messagesUnread', 0),
                    threadsTotal=label.get('threadsTotal', 0),
                    threadsUnread=label.get('threadsUnread', 0),
                    color=label.get('color', CategoryColor(
                        textColor="#000000",
                        backgroundColor="#FFFFFF"
                    )),
                ))
            # return labels

            return CategoryListResponse(categories=category_list)
        except Exception as e:
            raise Exception(f"Error function get_labels: {str(e)}")

    def get_attachments(self, 
        req: AttachmentRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().attachments().get(
                userId='me', 
                id=req.attachment_id,
                messageId=req.msg_id
            ).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function get_attachments: {str(e)}")
    
    def get_label_by_id(self, 
        req: GetLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().get(userId='me', id=req.id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function get_label_by_id: {str(e)}")
    
    def create_label(self, 
        req: CreateLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            body = {
                "name": req.body.name,
                "messageListVisibility": req.body.messageListVisibility,
                "labelListVisibility": req.body.labelListVisibility,
                "type": req.body.type,
                "messagesTotal": req.body.messagesTotal,
                "messagesUnread": req.body.messagesUnread,
                "threadsTotal": req.body.threadsTotal,
                "threadsUnread": req.body.threadsUnread,
                "color": req.body.color.model_dump(),
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().create(userId='me', body=body).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function create_label: {str(e)}")

    def sync_labels(self, 
        req: SyncLabelsRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            results = []
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            existing_labels = service.users().labels().list(userId='me').execute()
            for name in req.names:
                if name in INITIAL_LABELS and name not in [label['name'] for label in existing_labels['labels']]:
                    body = INITIAL_LABELS[name]
                    results.append(service.users().labels().create(userId='me', body=body).execute())
            return results
        except Exception as e:
            raise Exception(f"Error function sync_labels: {str(e)}")

    def message_modify_label(self, 
        req: MessageModifyLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            body = {
                "addLabelIds": req.addLabelIds,
                "removeLabelIds": req.removeLabelIds,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().modify(userId='me', id=req.id, body=body).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function modify_label: {str(e)}")
    
    def message_batch_modify_label(self, 
        req: MessageBatchModifyLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            body = {
                "ids": req.ids,
                "addLabelIds": req.addLabelIds,
                "removeLabelIds": req.removeLabelIds,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().batchModify(userId='me', body=body).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_batch_modify_label: {str(e)}")
    
    def message_delete(self, 
        req: MessageIdRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().delete(userId='me', id=req.id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_delete: {str(e)}")

    def message_batch_delete(self, 
        req: MessageBatchDeleteRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            body = {
                "ids": req.ids,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().batchDelete(userId='me', body=body).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_batch_delete: {str(e)}")

    def message_trash(self, 
        req: MessageIdRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().trash(userId='me', id=req.id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_trash: {str(e)}")
    
    def message_untrash(self, 
        req: MessageIdRequest,
        current_user: UserRequest,
        db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().untrash(userId='me', id=req.id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_untrash: {str(e)}")