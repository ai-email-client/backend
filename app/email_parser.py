import base64
import email
import re
from email.policy import default
from typing import Dict, Any, Optional, List
from email.message import EmailMessage

from app.schemas.email import Attachment, Message, MessagePart, Sender


def encode_base64(data: str) -> str:
    try:
        return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""

def encode_base64_bytes(data: bytes) -> str:
    try:
        return base64.urlsafe_b64encode(data).decode("utf-8")
    except Exception:
        return ""

def decode_base64(data: str) -> str:
    try:
        padding = len(data) % 4
        if padding:
            data += "=" * (4 - padding)
        return base64.urlsafe_b64decode(data).decode("utf-8")
    except Exception:
        return ""

def parse_raw_message_from_string(raw_string: str):
    try:
        msg_bytes = base64.urlsafe_b64decode(raw_string)
        
        return email.message_from_bytes(msg_bytes, policy=default)
        
    except Exception as e:
        print(f"Error parsing message: {e}")
        return None

def parse_raw_message_from_bytes(raw_bytes: bytes):
    return email.message_from_bytes(raw_bytes, policy=default)

def sender_format(sender: str) -> Sender:
    match = re.match(r"^(.*?)(?:\s*<([^>]+)>)?$", sender.strip())
    if not match:
        return Sender(email="", name="")
    
    extracted_name = match[1].strip()
    extracted_email = match[2].strip() if match[2] else extracted_name
    
    return Sender(email=extracted_email, name=extracted_name)

def format_recipients(recipients: str) -> List[Sender]:
    recipients_list = recipients.split(",")
    return [sender_format(recipient.strip()) for recipient in recipients_list]

def get_header_value(headers: Dict[str, Any], header_name: str) -> str:
    for header in headers:
        if header["name"] == header_name:
            return header["value"]
    return ""

def get_part_by_mimetype(
    payload: Dict[str, Any], target_mimetype: str
) -> Optional[Dict[str, Any]]:
    if payload["mimeType"] == target_mimetype:
        if "body" in payload and payload["body"].get("data"):
            return payload

    if "parts" in payload:
        for part in payload["parts"]:
            found = get_part_by_mimetype(part, target_mimetype)
            if found:
                return found

    return None


def get_attachments(parts: List[Dict[str, Any]]):
    attachments = []

    for part in parts:
        if part.get("filename", ""):
            attachments.append(
                {
                    "filename": part.get("filename", ""),
                    "mimeType": part.get("mimeType", ""),
                    "size": part.get("body", {}).get("size", 0),
                    "attachmentId": part.get("body", {}).get("attachmentId", ""),
                    "headers": part.get("headers", []),
                }
            )

        if "parts" in part:
            attachments.extend(get_attachments(part))
    return attachments

def get_attachments_from_iterator(iterator: List[EmailMessage]):
    attachments = []
    for message in iterator:
        if message.get_filename():
            attachments.append(
                Attachment(
                    filename=message.get_filename(),
                    mimeType=message.get_content_type(),
                    size=len(message.get_content()),
                    data=encode_base64_bytes(message.get_content())
                )
            )
    return attachments

def get_payload(message: Dict[str, Any]) -> MessagePart:
    return message.get("payload", {})

def get_headers(message: Dict[str, Any]) -> List[MessagePart]:
    return message.get("headers", {})

def get_parts(payload: Dict[str, Any]) -> List[MessagePart]:
    parts_list: List[MessagePart] = []
    
    if "parts" in payload:
        for part in payload["parts"]:
            parts_list.extend(get_parts(part))
    else:
        parts_list.append(payload)
        
    return parts_list

def get_text_content(parts: List[Dict[str, Any]], mimetype: str) -> Optional[str]:
    for part in parts:
        if part.get("mimeType") == mimetype:
            if "body" in part and part.get("body", {}).get("data"):
                return decode_base64(part.get("body", {}).get("data"))
    return None

def parse_message_by_payload(message: Dict[str, Any]) -> Message:

    payload = get_payload(message)
    headers = get_headers(payload)
    parts = get_parts(payload)
    try:
        message = Message(
            id=message.get("id", ""),
            threadId=message.get("threadId", ""),
            message_id=get_header_value(headers, "Message-Id"),
            historyId=message.get("historyId", None),
            sender=Sender(
                email=sender_format(get_header_value(headers, "From")).email,
                name=sender_format(get_header_value(headers, "From")).name
            ),
            to=format_recipients(get_header_value(headers, "To")),
            cc=format_recipients(get_header_value(headers, "Cc")),
            bcc=format_recipients(get_header_value(headers, "Bcc")),

            subject=get_header_value(headers, "Subject"),
            snippet=message.get("snippet", ""),
            text_plain=get_text_content(parts, "text/plain"),
            text_html=get_text_content(parts, "text/html"),
            attachments=get_attachments(parts),

            in_reply_to=get_header_value(headers, "In-Reply-To"),
            references=get_header_value(headers, "References"),
            
            labelIds=message.get("labelIds", []),
            date=get_header_value(headers, "Date"),

            internalDate=message.get("internalDate", None),
            sizeEstimate=message.get("sizeEstimate", None),
        )
    except Exception as e:
        print(e)
        return None

    return message