import imaplib
import email as email_lib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from app.services.providers.base import BaseEmailProvider
from app.schemas.email import Message, Attachment
from app.services.email_parser import (
    _decode_mime_words, _parse_address_single,
    _parse_address_raw, _parse_date,
)


IMAP_PRESETS = {
    # provider  : (imap_host, imap_port, smtp_host, smtp_port)
    "yahoo"     : ("imap.mail.yahoo.com",  993, "smtp.mail.yahoo.com",  465),
    "zoho"      : ("imap.zoho.com",        993, "smtp.zoho.com",        465),
    "outlook"   : ("outlook.office365.com",993, "smtp.office365.com",   587),
    "icloud"    : ("imap.mail.me.com",     993, "smtp.mail.me.com",     587),
    "custom"    : ("",                       0, "",                       0),
}


class IMAPProvider(BaseEmailProvider):

    def __init__(
        self,
        email_address: str,
        password: str,
        imap_host: str,
        imap_port: int = 993,
        smtp_host: str = "",
        smtp_port: int = 587,
    ):
        self.email_address = email_address
        self.password = password
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        conn = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        conn.login(self.email_address, self.password)
        return conn

    def list_messages(
        self,
        folder: str = "INBOX",
        query: str = "",
        max_results: int = 20,
        page_token: Optional[str] = None,
    ) -> dict:
        conn = self._connect_imap()
        conn.select(folder)

        search_criteria = self._build_search(query)
        _, data = conn.search(None, search_criteria)
        all_ids = data[0].split()

        offset = int(page_token) if page_token else 0
        page_ids = all_ids[-(offset + max_results): len(all_ids) - offset or None]
        page_ids = list(reversed(page_ids))

        messages = []
        for uid in page_ids:
            _, msg_data = conn.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw)
            messages.append(self._parse_imap_message(msg, uid.decode()))

        conn.logout()
        next_token = str(offset + max_results) if len(all_ids) > offset + max_results else None

        return {"messages": messages, "nextPageToken": next_token}

    def get_message(self, message_id: str) -> Message:
        conn = self._connect_imap()
        conn.select("INBOX")
        _, msg_data = conn.fetch(message_id.encode(), "(RFC822)")
        raw = msg_data[0][1]
        msg = email_lib.message_from_bytes(raw)
        conn.logout()
        return self._parse_imap_message(msg, message_id)

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """
        IMAP ไม่มี attachment ID แบบ Gmail
        attachment_id ที่ส่งมาคือ index ของ part เช่น "0", "1"
        """
        conn = self._connect_imap()
        conn.select("INBOX")
        _, msg_data = conn.fetch(message_id.encode(), "(RFC822)")
        raw = msg_data[0][1]
        msg = email_lib.message_from_bytes(raw)
        conn.logout()

        parts_with_file = [
            p for p in msg.walk()
            if p.get_filename()
        ]
        idx = int(attachment_id)
        if idx < len(parts_with_file):
            return parts_with_file[idx].get_payload(decode=True)
        return b""

    def mark_as_read(self, message_id: str) -> None:
        conn = self._connect_imap()
        conn.select("INBOX")
        conn.store(message_id.encode(), "+FLAGS", "\\Seen")
        conn.logout()

    def mark_as_unread(self, message_id: str) -> None:
        conn = self._connect_imap()
        conn.select("INBOX")
        conn.store(message_id.encode(), "-FLAGS", "\\Seen")
        conn.logout()

    def trash_message(self, message_id: str) -> None:
        conn = self._connect_imap()
        conn.select("INBOX")
        conn.store(message_id.encode(), "+FLAGS", "\\Deleted")
        conn.expunge()
        conn.logout()

    def get_labels(self) -> list[dict]:
        conn = self._connect_imap()
        _, folders = conn.list()
        conn.logout()
        result = []
        for f in folders:
            parts = f.decode().split('"/"')
            name = parts[-1].strip().strip('"')
            result.append({"id": name, "name": name})
        return result

    def send_message(self, to, subject, body, html_body=None,
                     cc=None, bcc=None, thread_id=None,
                     in_reply_to=None, references=None, attachments=None) -> dict:
        msg = MIMEMultipart("alternative")
        msg["From"]    = self.email_address
        msg["To"]      = to
        msg["Subject"] = subject
        if cc:  msg["Cc"] = cc
        if bcc: msg["Bcc"] = bcc
        if in_reply_to: msg["In-Reply-To"] = in_reply_to
        if references:  msg["References"]  = references

        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))

        if attachments:
            for f in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f["content"])
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{f["filename"]}"')
                msg.attach(part)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, to, msg.as_string())

        return {"message_id": "", "thread_id": thread_id or ""}

    def _parse_imap_message(self, msg, uid: str) -> Message:
        plain, html, attachments = "", "", []

        for part in msg.walk():
            mime = part.get_content_type()
            fname = part.get_filename()
            disposition = str(part.get("Content-Disposition", ""))

            if fname:
                attachments.append(Attachment(
                    filename=_decode_mime_words(fname) or "unnamed",
                    mimeType=mime,
                    size=len(part.get_payload(decode=True) or b""),
                    attachmentId=str(len(attachments)),  # ใช้ index แทน
                ))
            elif mime == "text/plain" and not plain and "attachment" not in disposition:
                plain = (part.get_payload(decode=True) or b"").decode("utf-8", errors="ignore")
            elif mime == "text/html" and not html and "attachment" not in disposition:
                html = (part.get_payload(decode=True) or b"").decode("utf-8", errors="ignore")

        return Message(
            id           = uid,
            threadId     = msg.get("Message-ID", uid),
            subject      = _decode_mime_words(msg.get("Subject")),
            sender       = _parse_address_single(msg.get("From")),
            to           = _parse_address_raw(msg.get("To")),
            cc           = _parse_address_raw(msg.get("Cc")),
            bcc          = _parse_address_raw(msg.get("Bcc")),
            date         = _parse_date(msg.get("Date")),
            message_id   = msg.get("Message-ID"),
            in_reply_to  = msg.get("In-Reply-To"),
            references   = msg.get("References"),
            text_plain   = plain or None,
            text_html    = html or None,
            attachments  = attachments or None,
            snippet      = plain[:100] if plain else None,
            labelIds     = [],
        )

    def _build_search(self, query: str) -> str:
        if not query:
            return "ALL"
        mapping = {
            "is:unread": "UNSEEN",
            "is:read":   "SEEN",
            "is:starred":"FLAGGED",
        }
        for k, v in mapping.items():
            if k in query:
                return v
        return f'OR SUBJECT "{query}" BODY "{query}"'
