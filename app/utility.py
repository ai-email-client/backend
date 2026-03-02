import base64
import hashlib
import hmac
import re
import datetime
import unicodedata
import jwt
import email
import json
from email.policy import default
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.schemas.email import Header


def decode_base64(data: str) -> str:
    try:
        padding = len(data) % 4
        if padding:
            data += "=" * (4 - padding)
        return base64.urlsafe_b64decode(data).decode("utf-8")
    except Exception:
        return ""


def raw_to_json(raw_string: str):
    msg_bytes = base64.urlsafe_b64decode(raw_string)

    msg = email.message_from_bytes(msg_bytes, policy=default)

    email_data = {
        "headers": {
            "subject": msg.get("Subject", ""),
            "from": msg.get("From", ""),
            "to": msg.get("To", ""),
            "date": msg.get("Date", ""),
        },
        "body": {"text": None, "html": None},
        "attachments": [],
    }

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    email_data["attachments"].append(filename)
                continue

            try:
                charset = part.get_content_charset("utf-8")

                if content_type == "text/plain" and not email_data["body"]["text"]:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        email_data["body"]["text"] = payload.decode(
                            charset or "utf-8", errors="ignore"
                        )
                    elif isinstance(payload, str):
                        email_data["body"]["text"] = payload

                elif content_type == "text/html" and not email_data["body"]["html"]:
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        email_data["body"]["html"] = payload.decode(
                            charset or "utf-8", errors="ignore"
                        )
                    elif isinstance(payload, str):
                        email_data["body"]["html"] = payload
            except Exception as e:
                print(f"Error decoding part: {e}")

    else:
        content_type = msg.get_content_type()
        charset = msg.get_content_charset("utf-8")
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            email_data["body"]["text"] = payload.decode(
                charset or "utf-8", errors="ignore"
            )
        elif isinstance(payload, str):
            email_data["body"]["text"] = payload

        if content_type == "text/plain":
            email_data["body"]["text"] = payload
        elif content_type == "text/html":
            email_data["body"]["html"] = payload

    return email_data


def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        for element in soup(["script", "style", "head", "meta", "noscript"]):
            element.extract()

        text = soup.get_text(separator="\n")

        lines = (line.strip() for line in text.splitlines())
        clean_text = "\n".join(line for line in lines if line)
        return clean_text

    except Exception:
        return html_content


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"<[^>]+>", "", text, flags=re.DOTALL)

    text = re.sub(r"\[https?://[^\]]+\]", "", text)
    text = re.sub(r"https?://\S+", "", text)

    invisible_chars = (
        r"[\u200b\u200c\u200d\u2060\ufeff\u00ad\u034f\u2007\u200e\u200f\u202a-\u202e]"
    )
    text = re.sub(invisible_chars, "", text)
    text = text.replace("\ufffd", "")
    text = text.replace("\r", "")

    text = re.sub(r"[-_=*+~#]{2,}", "", text)

    text = re.sub(r"[\t\xa0]", " ", text)
    text = re.sub(r" +", " ", text)

    footer_markers = [
        "follow us:",
        "to unsubscribe",
        "unsubscribe from this newsletter",
        "terms of use:",
        "privacy policy:",
        "view web version",
        "you're receiving this e-mail because",
        "this email message was auto-generated",
        "cheers,",
        "© valve corporation",
    ]

    text_lower = text.lower()
    cutoff_index = len(text)

    for marker in footer_markers:
        idx = text_lower.find(marker)
        if idx != -1 and idx < cutoff_index:
            cutoff_index = idx

    text = text[:cutoff_index]

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    text = "\n\n".join(lines)

    return text.strip()


def convert_timestamp_to_date(timestamp: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_email_header(headers: List[Header], header_name: str) -> str:
    for header in headers:
        if header.name == header_name:
            return header.value
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


def get_attachments(payload: Dict[str, Any]):
    attachments = []

    parts = payload.get("parts", [])

    for part in parts:
        if part.get("filename", ""):
            attachments.append(
                {
                    "filename": part.get("filename", ""),
                    "mimeType": part.get("mimeType", ""),
                    "size": part.get("body", {}).get("size", 0),
                    "attachmentId": part.get("body", {}).get("attachmentId", ""),
                }
            )

        if "parts" in part:
            attachments.extend(get_attachments(part))
    return attachments


def get_decode_by_mimetype(parts: Dict[str, Any], target_mimetype: str):
    if parts["mimeType"] == target_mimetype:
        if "body" in parts and parts["body"].get("data"):
            return decode_base64(parts["body"]["data"])
    return ""


def html_to_text(html_content: str) -> str:
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup(["script", "style", "head", "title", "meta", "[document]"]):
        element.extract()

    text = soup.get_text(separator=" ")

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text


def jwt_encode(payload: Dict[str, Any], secret_key: str):
    try:
        return jwt.encode(payload, secret_key, algorithm="HS256")
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


def jwt_decode(token: str, secret_key: str):
    try:
        return jwt.decode(token, secret_key, algorithms="HS256")
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))


def hash_pin(pin: str, salt: str) -> str:
    salted_pin = pin + salt

    hashed = hashlib.sha256(salted_pin.encode("utf-8")).hexdigest()
    return hashed


def verify_pin(plain_pin: str, stored_hash: str, salt: str) -> bool:
    new_hash = hash_pin(plain_pin, salt)

    return hmac.compare_digest(new_hash, stored_hash)
