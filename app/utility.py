import base64
import hashlib
import hmac
import re
import datetime
import unicodedata
import jwt
import json
import html
from typing import Dict, Any
from bs4 import BeautifulSoup
from fastapi import HTTPException


def clean_html(html_content: str) -> str:
    if not html_content:
        return ""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        for element in soup(["script", "style", "head", "meta", "noscript"]):
            element.extract()
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)
        return clean_text(text)
    except Exception:
        return clean_text(html_content)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)

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

def parse_json_response(raw_json):
    clean_json = raw_json.replace('```json', '').replace('```', '').strip()

    try:
        data = json.loads(clean_json)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def is_html(text: str) -> bool:
    return bool(re.search(r'<[a-zA-Z][^>]*>', text))

def clean_content(text: str) -> str:
    if not text or not text.strip():
        return ''
    return clean_html(text) if is_html(text) else clean_text(text)

def encode_state(origin: str, oauth_state: str) -> str:
    payload = json.dumps({"origin": origin, "state": oauth_state})
    return base64.urlsafe_b64encode(payload.encode()).decode()
 
def decode_state(encoded: str) -> dict:
    payload = base64.urlsafe_b64decode(encoded.encode()).decode()
    return json.loads(payload)