from typing import List, Dict, Any
from unittest import result
from fastapi import HTTPException
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from google.oauth2 import id_token
from googleapiclient import errors as google_api_errors
from email.message import EmailMessage

import logging
from pyparsing import results


from app.schemas.email import Draft, Format, MessageGmail,Attachment
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
    DraftsResposnse,
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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_user_email(self, credentials):
        service = self.build_service(credentials)

        user_info = service.users().getProfile(userId="me").execute()

        return user_info

    def exchange_code(self, authorization_code: str, state: str = ""):
        """Exchange an authorization code for OAuth 2.0 credentials.

        Args:
            authorization_code: Authorization code to exchange for OAuth 2.0
                                credentials.

        Returns:
            oauth2client.client.OAuth2Credentials instance.

        Raises:
            CodeExchangeException: an error occurred.
        """
        flow = Flow.from_client_config(
            self.client_config, " ".join(self.scopes), state=state
        )
        flow.redirect_uri = self.config.GOOGLE_REDIRECT_URI
        try:
            credentials = flow.fetch_token(code=authorization_code)
            return credentials
        except FlowExchangeError as error:
            logging.error("An error occurred: %s", error)
            raise CodeExchangeException(authorization_code)

    def get_user_info(self, credentials):
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
        flow.autogenerate_code_verifier = False
        url, state = flow.authorization_url(
            include_granted_scopes="true",
        )

        return url, state

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
            credentials = self.exchange_code(authorization_code, state)
            user_info = self.get_user_info(credentials)
            if credentials.get("refresh_token") is not None:
                return self.store_credentials(
                    user_info.get("emailAddress", ""), credentials, db
                )
            else:
                return self.get_stored_credentials(
                    user_info.get("emailAddress", ""), db
                )
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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

        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def initialize_labels(self, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            for label in INITIAL_LABELS:
                service.users().labels().create(userId="me", body=label).execute()

            return {"message": "Labels initialized successfully"}
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_messages(
        self, param: MessagesParam, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = []
            req = (
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
            nextPageToken = req.get("nextPageToken")
            resultSizeEstimate = req.get("resultSizeEstimate")

            def callback(request_id, response, exception):
                if exception is not None:
                    print(f"Error ID {request_id}: {exception}")
                else:
                    results.append(response)

            batch = service.new_batch_http_request()

            for msg in req.get("messages", []):
                req = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg.get("id"),
                        format=param.format,
                        metadataHeaders=param.metadataHeaders,
                    )
                )
                batch.add(req, callback=callback)

            batch.execute()

            return {"messages": results, "nextPageToken": nextPageToken, "resultSizeEstimate": resultSizeEstimate}

        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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

        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_labels(self, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().list(userId="me").execute()

            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_attachment(
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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_label_by_id(self, label_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().labels().get(userId="me", id=label_id).execute()
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def sync_labels(self, current_user: UserRequest, db: SupabaseDB):
        try:
            results = []
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            def callback(request_id, response, exception):
                if exception is not None:
                    print(f"Error ID {request_id}: {exception}")
                else:
                    results.append(response)

            batch = service.new_batch_http_request()

            labels = service.users().labels().list(userId="me").execute()
            for missing in INITIAL_LABELS.keys():
                if missing not in [label.get("name") for label in labels["labels"]]:
                    req = (
                        service.users()
                        .labels()
                        .create(userId="me", body=INITIAL_LABELS[missing])
                    )
                    batch.add(req, callback=callback)
            batch.execute()
            labels["labels"].extend(results)
            return labels
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def message_delete(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().delete(userId="me", id=msg_id).execute()
            )
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def message_trash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = service.users().messages().trash(userId="me", id=msg_id).execute()
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def message_untrash(self, msg_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = (
                service.users().messages().untrash(userId="me", id=msg_id).execute()
            )
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

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

            message["To"] = req.to
            message["From"] = current_user.email_address
            message["Subject"] = req.subject
            if req.cc:
                message["Cc"] = req.cc
            if req.bcc:
                message["Bcc"] = req.bcc
            message.set_content(req.content)

            encoded_message = utility.encode_base64(message.as_bytes())
            if req.message is not None:
                create_message = {
                    "message": {
                        "raw": encoded_message,
                        'threadId': req.message.threadId
                    }
                }
            else:
                create_message = {
                    "message": {
                        "raw": encoded_message,
                    }
                    }

            results = (
                service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )
            print("Results:", results)
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def delete_draft(self, draft_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = (
                service.users().drafts().delete(userId="me", id=draft_id).execute()
            )
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_draft(
        self, draft_id: str, current_user: UserRequest, db: SupabaseDB, format: str
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            results = service.users().drafts().get(userId="me", id=draft_id, format=format).execute()
            draft_id = results.get("id", "")
            
            
            return {"id": draft_id, "message": results.get("message", {})}
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def get_drafts(
        self, params: DraftsQueryParams, current_user: UserRequest, db: SupabaseDB
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)
            results = []

            res = service.users().drafts().list(
                userId="me",
                maxResults=params.maxResults,
                pageToken=params.pageToken,
                q=params.q,
                includeSpamTrash=params.includeSpamTrash,
            ).execute()

            nextPageToken = res.get("nextPageToken", None)
            resultSizeEstimate = res.get("resultSizeEstimate", 0)

            def callback(request_id, response, exception):
                if exception is not None:
                    print(f"Error ID {request_id}: {exception}")
                else:
                    results.append({
                        "id": response.get("id", ""),
                        "message": response.get("message", {})
                    })

            batch = service.new_batch_http_request()

            for draft in res.get("drafts", []):
                
                req = (
                    service.users()
                    .drafts()
                    .get(userId="me", id=draft.get("id"), format=params.format)
                )
                batch.add(req, callback=callback)

            batch.execute()

            return {
                "drafts": results,
                "nextPageToken": nextPageToken,
                "resultSizeEstimate": resultSizeEstimate
            }

        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def update_draft(
        self,
        draft_id: str,
        req: CreateDraftRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
                credentials = self.get_stored_credentials(current_user.email_address, db)
                service = self.build_service(credentials)
                                
                message = EmailMessage()
                message["To"] = req.to
                message["Cc"] = req.cc
                message["Bcc"] = req.bcc
                message["From"] = current_user.email_address
                message["Subject"] = req.subject
                
                message.set_content(req.content)
                if req.attachments:
                    for att in req.attachments:
                        if att.data:
                            file_data = utility.decode_base64(att.data)
                            
                            if '/' in att.mimeType:
                                m_type, s_type = att.mimeType.split('/', 1)
                            else:
                                m_type, s_type = 'application', 'octet-stream'

                            message.add_attachment(
                                file_data,
                                maintype=m_type,
                                subtype=s_type,
                                filename=att.filename
                            )

                raw_bytes = message.as_bytes()
                encoded_message = utility.encode_base64_bytes(raw_bytes)
                
                update_body = {"message": 
                    {
                        "raw": encoded_message,
                        'threadId': req.threadId
                    }
                }

                results = (
                    service.users()
                    .drafts()
                    .update(userId="me", id=draft_id, body=update_body)
                    .execute()
                )
                
                return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def upload_draft(
        self,
        draft_id: str,
        req: CreateDraftRequest,
        current_user: UserRequest,
        db: SupabaseDB,
    ):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            message = EmailMessage()

            message["To"] = req.to
            message["From"] = current_user.email_address
            message["Subject"] = req.subject
            message.set_content(req.content)

            encoded_message = utility.encode_base64(message.as_bytes())

            update_message = {"message": {"raw": encoded_message}}

            results = (
                service.users()
                .drafts()
                .upload(userId="me", body=update_message)
                .execute()
            )
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())

    def send_draft(self, draft_id: str, current_user: UserRequest, db: SupabaseDB):
        try:
            credentials = self.get_stored_credentials(current_user.email_address, db)
            service = self.build_service(credentials)

            draft = service.users().drafts().get(userId="me", id=draft_id).execute()

            results = service.users().drafts().send(userId="me", body=draft).execute()
            return results
        except google_api_errors.HttpError as e:
            raise HTTPException(status_code=e.status_code, detail=e._get_reason())
