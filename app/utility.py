import base64
from typing import Dict, Any
from bs4 import BeautifulSoup

def get_email_body(payload: Dict[str, Any]) -> str:
    if 'body' in payload and payload['body'].get('data'):
        content = decode_base64(payload['body']['data'])
        if payload.get('mimeType') == 'text/html':
            return clean_html(content)
        return content

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return get_email_body(part)
        
        for part in payload['parts']:
            if part['mimeType'] == 'text/html':
                html_body = get_email_body(part)
                return clean_html(html_body)
                
        if 'parts' in payload:
            found = get_email_body(payload)
            if found:
                return found
                    
    return ""

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