import pandas as pd
import csv
import os

def load_test_cases(file_path: str) -> list[tuple]:
    
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"ไม่รองรับไฟล์นามสกุลนี้: {file_path} (กรุณาใช้ .csv หรือ .xlsx)")
    
    test_data = df[['Test Case ID', 'Input Email', 'Expected sender_type', 'Expected email_category', 'Expected Spam','Remark']]
    
    return list(test_data.itertuples(index=False, name=None))

def save_result_to_csv(
        tc_id, input_email, 
        actual_sender_type, expected_sender_type,
        actual_email_category, expected_email_category,
        actual_spam, expected_spam,
        result,status, remark=""
    ):

    file_name = 'test_results_report.csv'
    path = os.path.join(os.path.dirname(__file__), file_name)
    file_exists = os.path.isfile(path)
    
    with open(path, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow(['Test Case ID', 
            'Input Email', 
            'Actual sender_type', 'Expected sender_type', 
            'Actual email_category', 'Expected email_category', 
            'Actual Spam', 'Expected Spam', 
            'Result', 'Status', 'Error Remark'])
        
        writer.writerow([
            tc_id, input_email, 
            actual_sender_type, expected_sender_type, 
            actual_email_category, expected_email_category, 
            actual_spam, expected_spam, 
            result, status, remark
        ])