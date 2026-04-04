import pandas as pd
import os
import re

def load_test_cases(file_path: str) -> list[tuple]:
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"ไม่รองรับไฟล์นามสกุลนี้: {file_path} (กรุณาใช้ .csv หรือ .xlsx)")
    
    test_data = df[[
        "Test Case ID",
        "Input Email",
        "Expected sender_type",
        "Expected email_category",
        "Expected Summary",
        "Expected Importance",
        "Expected Spam"
    ]]
    
    return list(test_data.itertuples(index=False, name=None))

def save_result_to_csv(
    file_path: str,
    test_case_id: str,
    actual_sender_type: str,
    actual_email_category: str,
    actual_summary: str,
    actual_importance: str,
    actual_spam: str,
    status: str,
    error_message: str = ""
):
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    new_columns = [
        "Actual sender_type", "Actual email_category", "Actual Summary", 
        "Actual Importance", "Actual Spam", "Status", "Error Message"
    ]
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = ""
            
        df[col] = df[col].astype('object')

    idx = df.index[df['Test Case ID'] == test_case_id]
    
    if not idx.empty:
        i = idx[0]
        df.at[i, 'Actual sender_type'] = actual_sender_type
        df.at[i, 'Actual email_category'] = actual_email_category
        df.at[i, 'Actual Summary'] = actual_summary
        df.at[i, 'Actual Importance'] = actual_importance
        df.at[i, 'Actual Spam'] = actual_spam

    if file_path.lower().endswith('.csv'):
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        df.to_excel(file_path, index=False)

def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)