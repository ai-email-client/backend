import pytest
import urllib3
from app.schemas.dify import DifySummary
from helper import load_test_cases, save_result_to_csv, strip_ansi
from app.services.dify import DifyService
from config import Config
from database import SupabaseDB

urllib3.disable_warnings()

TEST_DATA_FILE = "app/unittest/ai_email_client_end_to_end.csv"

def build_csv_row(
    tc_id: str, 
    result_data: DifySummary, 
):
    actual_sender   = result_data.sender.type      if result_data else None
    actual_category = result_data.email_category   if result_data else None
    actual_summary  = result_data.summary          if result_data else None
    actual_importance = result_data.importance     if result_data else None
    actual_spam     = result_data.is_spam          if result_data else None

    save_result_to_csv(
        file_path=TEST_DATA_FILE,
        test_case_id=tc_id, 
        actual_sender_type=actual_sender,
        actual_email_category=actual_category,
        actual_summary=actual_summary, 
        actual_importance=actual_importance,
        actual_spam=actual_spam,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tc_id, input_email, expected_sender_type, expected_category, expected_summary, expected_importance, expected_spam",
    load_test_cases(TEST_DATA_FILE),
)
async def test_email_classification(
    tc_id: str,
    input_email: str,
    expected_sender_type: str,
    expected_category: str,
    expected_summary: str,
    expected_importance: str,
    expected_spam: str,
):
    dify_service = DifyService(config=Config(), db=SupabaseDB(Config()))
    expected = {
        "sender_type": expected_sender_type,
        "category":    expected_category,
        "summary":     expected_summary,
        "importance":  expected_importance,
        "spam":        expected_spam,
    }

    result = await dify_service.test_to_summary(input_email)

    if result is None:
        build_csv_row(tc_id, None)
        pytest.fail(f"[{tc_id}] Dify service returned None")

    result_data = result.data.outputs.clean_email

    if result_data is None:
        build_csv_row(tc_id, None)
        pytest.fail(f"[{tc_id}] Dify service failed to process the email")

    try:
        assert result_data.sender.type == expected["sender_type"]
        assert result_data.email_category == expected["category"]
        assert result_data.summary == expected["summary"]
        assert result_data.importance == expected["importance"]
        assert result_data.is_spam == expected["spam"]
    except Exception as e:
        build_csv_row(tc_id, result_data)
        pytest.fail(f"[{tc_id}] Validation failed: {e}")
    
    build_csv_row(tc_id, result_data)