import base64
import re
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

def decode_base64(data: str) -> str:
    try:
        padding = len(data) % 4
        if padding:
            data += '=' * (4 - padding)
        return base64.urlsafe_b64decode(data).decode('utf-8')
    except Exception:
        return ""

def clean_html(html_content: str) -> str:
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=' ', strip=True)
    except Exception:
        return html_content

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.replace('\r', '')
    
    lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def get_email_subject(payload: Dict[str, Any]) -> str:
    if 'headers' in payload:
        for header in payload['headers']:
            if header['name'] == 'Subject':
                return header['value']
    return ''

def get_email_sender(payload: Dict[str, Any]) -> str:
    if 'headers' in payload:
        for header in payload['headers']:
            if header['name'] == 'From':
                return header['value']
    return ''

def get_email_snippet(payload: Dict[str, Any]) -> str:
    if 'snippet' in payload:
        return payload['snippet']
    return ''

def get_payload(txt: Dict[str, Any]) -> Dict[str, Any]:
    payload = txt['payload']
    return payload

def get_email_parts(payload: Dict[str, Any]) -> Dict[str, Any]:
    return payload['parts']

def get_part_by_mimetype(payload: Dict[str, Any], target_mimetype: str) -> Optional[Dict[str, Any]]:
    if payload['mimeType'] == target_mimetype:
        if 'body' in payload and payload['body'].get('data'):
            return payload

    if 'parts' in payload:
        for part in payload['parts']:
            found = get_part_by_mimetype(part, target_mimetype)
            if found:
                return found
    
    return None

def get_decode_by_mimetype(parts: Dict[str, Any], target_mimetype: str) -> Optional[str]:
    if parts['mimeType'] == target_mimetype:
        if 'body' in parts and parts['body'].get('data'):
            return decode_base64(parts['body']['data'])
    return None