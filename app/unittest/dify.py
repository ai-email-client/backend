import pytest
import urllib3
from app.schemas.dify import DifySummary
from helper import load_test_cases, save_result_to_csv, strip_ansi
from app.services.dify import DifyService
from config import Config
from database import SupabaseDB

urllib3.disable_warnings()


def build_csv_row(tc_id: str, input_email: str, result_data: DifySummary, expected: dict, status: str, error_msg: str = "", remark: str = ""):
    actual_sender   = result_data.sender.type      if result_data else None
    actual_category = result_data.email_category   if result_data else None
    actual_spam     = result_data.is_spam          if result_data else None
    actual_json     = result_data.model_dump_json() if result_data else None

    save_result_to_csv(
        tc_id, input_email,
        actual_sender,   expected["sender_type"],
        actual_category, expected["category"],
        actual_spam,     expected["spam"],
        actual_json, status, error_msg, remark,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tc_id, input_email, expected_sender_type, expected_category, expected_spam, remark",
    load_test_cases("app/unittest/ai_email_client_e2e_test_cases.csv"),
)
async def test_email_classification(
    tc_id: str,
    input_email: str,
    expected_sender_type: str,
    expected_category: str,
    expected_spam: str,
    remark: str,
):
    dify_service = DifyService(config=Config(), db=SupabaseDB(Config()))
    expected = {
        "sender_type": expected_sender_type,
        "category":    expected_category,
        "spam":        expected_spam,
    }

    result = await dify_service.test_summary(input_email)

    if result is None:
        build_csv_row(tc_id, input_email, None, expected, status="FAIL", remark=remark)
        pytest.fail(f"[{tc_id}] Dify service returned None")

    result_data = result.data.outputs.clean_email

    assertions = [
        (
            result_data.sender.type == expected_sender_type,
            f"[{tc_id}] Expected sender type '{expected_sender_type}' but got '{result_data.sender.type}'",
        ),
        (
            result_data.email_category == expected_category,
            f"[{tc_id}] Expected category '{expected_category}' but got '{result_data.email_category}'",
        ),
        (
            str(result_data.is_spam).lower() == str(expected_spam).lower(),
            f"[{tc_id}] Expected spam '{expected_spam}' but got '{result_data.is_spam}'",
        ),
    ]

    failed = [msg for ok, msg in assertions if not ok]

    if failed:
        error_msg = " | ".join(failed)
        build_csv_row(tc_id, input_email, result_data, expected, status="FAIL", error_msg=error_msg, remark=remark)
        pytest.fail(error_msg)

    build_csv_row(tc_id, input_email, result_data, expected, status="PASS", remark=remark)