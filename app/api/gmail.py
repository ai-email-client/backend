from typing import List, Dict, Any
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2 import id_token
from googleapiclient import errors as google_api_errors
from email.message import EmailMessage

import logging
import base64


from app.schemas.email import Format, Message
from config import Config
from app import utility
from database import SupabaseDB

from app.schemas.request import (
    EmailFetchRequest,
    MessageIdRequest,
    MessageBatchDeleteRequest,
    UserRequest,
    CreateLabelRequest,
    MessageModifyLabelRequest,
    MessageBatchModifyLabelRequest,
    SyncLabelsRequest,
    CreateDraftRequest,
)

from app.schemas.response import (
    CredentialResponse,
    EmailDetailResponse,
    EmailShortResponse,
    EmailFetchResponse,
    EmailPlainResponse,
    EmailFetchPlainResponse,
    CategoryListResponse,
    MessagesResponse,
)

from app.schemas.category import (
    Category,
    MessageListVisibility,
    LabelListVisibility,
    CategoryType,
    CategoryColor,
)
from app.schemas.query import DraftsQueryParams, MessageParam, MessagesParam

from exception import CodeExchangeException, FlowExchangeError

from app.schemas.category import INITIAL_LABELS


class GmailAPI:
    def __init__(self, config: Config):
        self.config = config
        self.scopes = [
            "https://mail.google.com/",
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
        ]
        self.client_config = {
            "web": {
                "client_id": config.GOOGLE_CLIENT_ID,
                "client_secret": config.GOOGLE_CLIENT_SECRET,
                "auth_uri": config.GOOGLE_AUTH_URI,
                "token_uri": config.GOOGLE_TOKEN_URI,
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_name": "Google",
                "redirect_uris": [config.GOOGLE_REDIRECT_URI],
            }
        }

    def build_service(self, creds):
        try:
            creds = Credentials(
                token=creds.get("access_token"),
                refresh_token=creds.get("refresh_token"),
                token_uri=self.config.GOOGLE_TOKEN_URI,
                client_id=self.config.GOOGLE_CLIENT_ID,
                client_secret=self.config.GOOGLE_CLIENT_SECRET,
                scopes=creds.get("scopes"),
            )
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            raise e

    def verify_oauth2_token(self, creds: dict[str, str]):
        return id_token.verify_oauth2_token(
            creds["id_token"],
            requests.Request(),
            audience=self.config.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=60,
        )

    def exchange_code(self, authorization_code: str):
        """Exchange an authorization code for OAuth 2.0 credentials.

        Args:
            authorization_code: Authorization code to exchange for OAuth 2.0
                                credentials.

        Returns:
            oauth2client.client.OAuth2Credentials instance.

        Raises:
            CodeExchangeException: an error occurred.
        """
        flow = Flow.from_client_config(self.client_config, " ".join(self.scopes))
        flow.redirect_uri = self.config.GOOGLE_REDIRECT_URI
        try:
            credentials = flow.fetch_token(code=authorization_code)
            return credentials
        except FlowExchangeError as error:
            logging.error("An error occurred: %s", error)
            raise CodeExchangeException(authorization_code)

    def get_user_info(self, credentials: dict[str, str]) -> dict[str, str]:
        """Send a request to the UserInfo API to retrieve the user's information.

        Args:
            credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                        request.

        Returns:
            User information as a dict.
        """
        user_info_service = self.build_service(credentials)

        user_info = {}
        try:
            user_info = user_info_service.users().getProfile(userId="me").execute()
        except google_api_errors.HttpError as e:
            logging.error("An error occurred: %s", e)
        return user_info

    def get_authorization_url(self):
        """Retrieve the authorization URL.
        Returns:
            Authorization URL to redirect the user to.
        """
        flow = Flow.from_client_config(self.client_config, " ".join(self.scopes))
        flow.redirect_uri = self.config.GOOGLE_REDIRECT_URI
        return flow.authorization_url()

    def get_credentials(self, authorization_code: str, state: str, db: SupabaseDB):
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
            if credentials.get("refresh_token") is not None:
                return self.store_credentials(
                    user_info.get("email", ""), credentials, db
                )
            else:
                return self.get_stored_credentials(user_info.get("email", ""), db)
        except Exception as e:
            raise e

    def get_stored_credentials(self, email_address: str, db: SupabaseDB):
        """Retrieved stored credentials for the provided user ID.

        Args:
            user_id: User's ID.

        Returns:
            Stored oauth2client.client.OAuth2Credentials if found, None otherwise.
        """
        if email_address == "":
            raise Exception("Email address is required")
        try:
            res = db.select(
                "google_accounts", "credentials", {"email_address": email_address}
            )
            if res:
                return res[0]["credentials"]
            return None

        except Exception as e:
            print(f"Error: {e}")

    def store_credentials(
        self, email_address: str, credentials: Credentials, db: SupabaseDB
    ):
        """Store OAuth 2.0 credentials in the application's database.

        This function stores the provided OAuth 2.0 credentials using the user ID as
        key.

        Args:
            user_id: User's ID.
            credentials: OAuth 2.0 credentials to store.
        """
        if email_address == "":
            raise Exception("Email address is required")
        try:
            res = db.upsert(
                "google_accounts",
                {
                    "email_address": email_address,
                    "credentials": credentials,
                    "updated_at": "now()",
                },
                "email_address",
            )
            return res[0]["credentials"]
        except Exception as e:
            print(f"Error: {e}")

    def initialize_labels(self, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            for label in INITIAL_LABELS:
                service.users().labels().create(userId="me", body=label).execute()

            return {"message": "Labels initialized successfully"}
        except Exception as e:
            raise Exception(f"Error function initialize_labels: {str(e)}")

    def fetch_emails(
        self, param: MessagesParam, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    maxResults=param.maxResults,
                    labelIds=param.labelIds,
                    pageToken=param.pageToken,
                    q=param.q,
                    includeSpamTrash=param.includeSpamTrash,
                )
                .execute()
            )

            return MessagesResponse(**results)

        except Exception as e:
            raise Exception(f"Error function fetch_emails: {str(e)}")

    def get_message_batch(
        self,
        msgs: List[Message],
        param: MessageParam,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = []

            def callback(request_id, response, exception):
                if exception is not None:
                    print(f"เกิดข้อผิดพลาดที่ ID {request_id}: {exception}")
                else:
                    results.append(response)

            batch = service.new_batch_http_request()

            for msg in msgs:
                req = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg.id,
                        format=param.format,
                        metadataHeaders=param.metadataHeaders,
                    )
                )
                batch.add(req, callback=callback)

            batch.execute()
            return results

        except Exception as e:
            raise Exception(f"Error function get_message_batch: {str(e)}")

    def get_message_by_id(
        self,
        msg_id: str,
        param: MessageParam,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            result = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg_id,
                    format=param.format,
                    metadataHeaders=param.metadataHeaders,
                )
                .execute()
            )

            return result

        except Exception as e:
            raise Exception(f"Error function get_message_by_id: {str(e)}")

    def get_labels(
        self, current_user: UserRequest, db: SupabaseDB
    ) -> CategoryListResponse:
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            category_list = []
            for label in labels:
                category_list.append(
                    Category(
                        id=label.get("id"),
                        name=label.get("name"),
                        messageListVisibility=MessageListVisibility(
                            label.get("messageListVisibility", "show")
                        ),
                        labelListVisibility=LabelListVisibility(
                            label.get("labelListVisibility", "labelShow")
                        ),
                        type=CategoryType(label.get("type")),
                        messagesTotal=label.get("messagesTotal", 0),
                        messagesUnread=label.get("messagesUnread", 0),
                        threadsTotal=label.get("threadsTotal", 0),
                        threadsUnread=label.get("threadsUnread", 0),
                        color=label.get(
                            "color",
                            CategoryColor(
                                textColor="#000000", backgroundColor="#FFFFFF"
                            ),
                        ),
                    )
                )
            return CategoryListResponse(categories=category_list)
        except Exception as e:
            raise Exception(f"Error function get_labels: {str(e)}")

    def get_attachments(
        self, msg_id: str, attachment_id: str, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", id=attachment_id, messageId=msg_id)
                .execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function get_attachments: {str(e)}")

    def get_label_by_id(self, label_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().get(userId="me", id=label_id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function get_label_by_id: {str(e)}")

    def get_label_by_name(
        self, label_name: str, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label.get("name").lower() == label_name.lower():
                    return Category(**label)
            return None
        except Exception as e:
            raise Exception(f"Error function get_label_by_name: {str(e)}")

    def create_label(
        self, req: CreateLabelRequest, current_user: UserRequest, db: SupabaseDB
    ) -> Category:
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
                "color": req.body.color.model_dump() if req.body.color else None,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().create(userId="me", body=body).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function create_label: {str(e)}")

    def sync_labels(
        self, req: SyncLabelsRequest, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            results = []
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            existing_labels = service.users().labels().list(userId="me").execute()
            for name in req.names:
                print("Syncing label:", name)
                if name.lower() in INITIAL_LABELS and name not in [
                    label["name"] for label in existing_labels["labels"]
                ]:
                    print("Creating label:", name)
                    body = INITIAL_LABELS[name.lower()]
                    results.append(
                        service.users()
                        .labels()
                        .create(userId="me", body=body)
                        .execute()
                    )
            return results
        except google_api_errors.HttpError as e:
            if e.resp.status == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            if e.resp.status == 401:
                raise Exception("Unauthorized. Please try again later.")
            if e.resp.status == 404:
                raise Exception("Resource not found. Please try again later.")
            if e.resp.status == 409:
                raise Exception("Conflict error. Please try again later.")
            if e.resp.status >= 400 and e.resp.status < 500:
                raise Exception("Bad request. Please try again later.")
            if e.resp.status >= 500:
                raise Exception("Google server error. Please try again later.")
            raise Exception(f"Error function sync_labels: {str(e)}")

    def message_modify_label(
        self, req: MessageModifyLabelRequest, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            body = {
                "addLabelIds": req.addLabelIds,
                "removeLabelIds": req.removeLabelIds,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users()
                .messages()
                .modify(userId="me", id=req.id, body=body)
                .execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function modify_label: {str(e)}")

    def message_batch_modify_label(
        self,
        req: MessageBatchModifyLabelRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
            body = {
                "ids": req.ids,
                "addLabelIds": req.addLabelIds,
                "removeLabelIds": req.removeLabelIds,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().batchModify(userId="me", body=body).execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function message_batch_modify_label: {str(e)}")

    def message_delete(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().delete(userId="me", id=msg_id).execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function message_delete: {str(e)}")

    def message_batch_delete(
        self, req: MessageBatchDeleteRequest, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            body = {
                "ids": req.ids,
            }
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().batchDelete(userId="me", body=body).execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function message_batch_delete: {str(e)}")

    def message_trash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().trash(userId="me", id=msg_id).execute()
            return results
        except Exception as e:
            raise Exception(f"Error function message_trash: {str(e)}")

    def message_untrash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().untrash(userId="me", id=msg_id).execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function message_untrash: {str(e)}")

    def create_draft(
        self,
        req: CreateDraftRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            message = EmailMessage()

            message["To"] = req.To
            message["From"] = current_user.email_address
            message["Subject"] = req.Subject
            message.set_content(req.Content)

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"message": {"raw": encoded_message}}

            results = (
                service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function create_draft: {str(e)}")

    def delete_draft(self, draft_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = (
                service.users().drafts().delete(userId="me", id=draft_id).execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function delete_draft: {str(e)}")

    def get_draft(
        self, draft_id: str, current_user: UserRequest, db: SupabaseDB, format: str
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = (
                service.users()
                .drafts()
                .get(userId="me", id=draft_id, format=format)
                .execute()
            )
            return results
        except Exception as e:
            raise Exception(f"Error function get_draft: {str(e)}")

    def get_drafts(
        self, params: DraftsQueryParams, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = (
                service.users()
                .drafts()
                .list(
                    userId="me",
                    maxResults=params.maxResults,
                    pageToken=params.pageToken,
                    q=params.q,
                    includeSpamTrash=params.includeSpamTrash,
                )
                .execute()
            )

            return results
        except Exception as e:
            raise Exception(f"Error function get_drafts: {str(e)}")
