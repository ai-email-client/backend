from helper import load_test_cases,save_result_to_csv
from app.services.dify import DifyService
import pytest
from config import Config
from database import SupabaseDB

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tc_id, input_email, expected_sender_type, expected_category, expected_spam, remark", 
    load_test_cases('app/unittest/ai_email_client_e2e_test_cases.csv')
)
async def test_email_classification(tc_id, input_email: str, expected_sender_type: str, expected_category: str, expected_spam: str, remark: str):
    dify_service = DifyService(
        config=Config(),
        db=SupabaseDB(Config()),
    )
    
    result = await dify_service.send_to_summary(input_email)
    
    if result is None:
        status = "FAIL"
        save_result_to_csv(
            tc_id, input_email, 
            None, expected_sender_type, 
            None, expected_category, 
            None, expected_spam,
            None, status, remark)
        raise Exception(f"[{tc_id}] Dify service returned None")
    
    status = "PASS"

    result_data = result.data.outputs.clean_email
    
    try:
        assert result_data.sender.type == expected_sender_type, f"[{tc_id}] Expected sender type '{expected_sender_type}' but got '{result_data.sender.type}'"
        assert result_data.email_category == expected_category, f"[{tc_id}] Expected category '{expected_category}' but got '{result_data.email_category}'"
        assert str(result_data.is_spam).lower() == str(expected_spam).lower(), f"[{tc_id}] Expected spam '{expected_spam}' but got '{result_data.is_spam}'"
        
    except AssertionError:
        status = "FAIL"
        
    finally:
        save_result_to_csv(
            tc_id, input_email, 
            result_data.sender.type, expected_sender_type, 
            result_data.email_category, expected_category, 
            result_data.is_spam, expected_spam,
            result_data.model_dump_json(), status, remark)