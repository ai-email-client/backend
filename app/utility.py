import base64
import re
import datetime
from typing import Dict, Any, Optional, List
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

def convert_timestamp_to_date(timestamp: int) -> str:
    return datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

def get_email_header(payload: Dict[str, Any], header_name: str) -> str:
    if 'headers' in payload:
        for header in payload['headers']:
            if header['name'] == header_name:
                return header['value']
    return ''

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

def get_attachments(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    attachments = []
    parts = payload.get('parts', [])
    
    for part in parts:
        # 1. เก็บไฟล์แนบ
        if part.get('filename'):
            attachments.append({
                "filename": part.get('filename'),
                "mimeType": part.get('mimeType'),
                "size": part.get('body', {}).get('size', 0),
                "attachmentId": part.get('body', {}).get('attachmentId')
            })
        
        # 2. Recursive: แก้ตรงนี้! 
        # ส่ง 'part' (Dict) เข้าไป ไม่ใช่ 'part["parts"]' (List)
        if 'parts' in part:
            attachments.extend(get_attachments(part))
    return attachments

def get_decode_by_mimetype(parts: Dict[str, Any], target_mimetype: str) -> Optional[str]:
    if parts['mimeType'] == target_mimetype:
        if 'body' in parts and parts['body'].get('data'):
            return decode_base64(parts['body']['data'])
    return None

def html_to_text(html_content: str) -> str:
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup(["script", "style", "head", "title", "meta", "[document]"]):
        element.extract()

    text = soup.get_text(separator=' ')

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

