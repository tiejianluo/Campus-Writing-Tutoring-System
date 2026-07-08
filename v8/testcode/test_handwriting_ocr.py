"""v8 手写作文识别测试：LLM OCR 调用路径 + 业务额度语义。

- LLMService.ocr_essay_image：未配置密钥 / 限流 / 成功 / 出错 / 异常返回结构。
- AppService.ocr_extract_essay：识别与 AI 点评共用每日额度；会员不限次；
  失败不扣额度。
"""

import json
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import (
    FALLBACK_API_ERROR,
    FALLBACK_NO_API_KEY,
    FALLBACK_QUOTA,
    FALLBACK_RATE_LIMITED,
    LLMService,
)
from app.rate_limit import FixedWindowRateLimiter
from app.services import AppService
from app.storage import SQLiteStore

PASSWORD = "Password8"
IMAGE = Image.new("RGB", (60, 40), "white")


def fake_openai_client(payload) -> MagicMock:
    """构造返回固定 JSON 的假 OpenAI 客户端。"""
    client = MagicMock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
    )
    return client


class TestOcrEssayImage(unittest.TestCase):
    def test_no_api_key_reports_reason(self):
        llm = LLMService(Settings())
        result = llm.ocr_essay_image(IMAGE)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], FALLBACK_NO_API_KEY)

    def test_rate_limited_reports_reason(self):
        llm = LLMService(Settings(openai_api_key="sk-test"), limiter=FixedWindowRateLimiter(1))
        self.assertTrue(llm.limiter.allow("ocr:stu"))  # 用真实时钟占满当前窗口额度
        result = llm.ocr_essay_image(IMAGE, user_key="stu")
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], FALLBACK_RATE_LIMITED)

    def test_successful_extraction(self):
        llm = LLMService(Settings(openai_api_key="sk-test"))
        client = fake_openai_client({"text": "我的妈妈是一名医生。\n她每天都很忙。"})
        with patch("openai.OpenAI", return_value=client):
            result = llm.ocr_essay_image(IMAGE, user_key="stu")
        self.assertTrue(result["ok"])
        self.assertIn("医生", result["text"])
        self.assertEqual(result["source"], "llm")
        self.assertIsNotNone(llm.last_success_at)
        # 请求确实带上了图片
        kwargs = client.chat.completions.create.call_args.kwargs
        contents = kwargs["messages"][1]["content"]
        self.assertTrue(any(part.get("type") == "image_url" for part in contents))

    def test_blank_text_still_ok_but_empty(self):
        llm = LLMService(Settings(openai_api_key="sk-test"))
        with patch("openai.OpenAI", return_value=fake_openai_client({"text": "   "})):
            result = llm.ocr_essay_image(IMAGE)
        self.assertTrue(result["ok"])
        self.assertEqual(result["text"], "")

    def test_api_error_reports_reason_and_logs(self):
        llm = LLMService(Settings(openai_api_key="sk-test"))
        with patch("openai.OpenAI", side_effect=RuntimeError("boom")):
            result = llm.ocr_essay_image(IMAGE)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], FALLBACK_API_ERROR)
        self.assertIn("boom", llm.last_error)


class FakeOcrLLM:
    """替身 LLM：记录调用次数，按预设结果响应。"""

    def __init__(self, result, configured=True):
        self.result = result
        self.configured = configured
        self.calls = 0

    def is_configured(self):
        return self.configured

    def ocr_essay_image(self, image, user_key="anonymous"):
        self.calls += 1
        return dict(self.result)


def build_service(llm, **overrides) -> AppService:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    settings = Settings(db_path=tmp.name, premium_trial_days=0, **overrides)
    service = AppService(settings, SQLiteStore(settings), llm)
    service.initialize()
    return service


class TestOcrQuotaSemantics(unittest.TestCase):
    OK_RESULT = {"ok": True, "text": "识别出的作文内容。", "source": "llm"}

    def setUp(self):
        self.llm = FakeOcrLLM(self.OK_RESULT)
        self.service = build_service(self.llm, free_ai_daily_quota=2)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)

    def test_not_configured_blocks_with_reason(self):
        self.llm.configured = False
        result = self.service.ocr_extract_essay("stu1", IMAGE)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], FALLBACK_NO_API_KEY)
        self.assertEqual(self.llm.calls, 0)

    def test_success_consumes_free_quota(self):
        result = self.service.ocr_extract_essay("stu1", IMAGE)
        self.assertTrue(result["ok"])
        self.assertEqual(self.service.ai_quota_left("stu1"), 1)

    def test_quota_exhausted_blocks_ocr_without_calling_llm(self):
        self.service.store.increment_ai_usage("stu1")
        self.service.store.increment_ai_usage("stu1")
        result = self.service.ocr_extract_essay("stu1", IMAGE)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], FALLBACK_QUOTA)
        self.assertEqual(self.llm.calls, 0)

    def test_failed_ocr_does_not_consume_quota(self):
        self.llm.result = {"ok": False, "text": "", "reason": FALLBACK_API_ERROR}
        result = self.service.ocr_extract_essay("stu1", IMAGE)
        self.assertFalse(result["ok"])
        self.assertEqual(self.service.ai_quota_left("stu1"), 2)

    def test_premium_unlimited_and_no_quota_charge(self):
        code = self.service.store.create_activation_code("month", "admin")
        self.service.redeem_code("stu1", code)
        # 即使额度记录已满，会员仍可识别
        self.service.store.increment_ai_usage("stu1")
        self.service.store.increment_ai_usage("stu1")
        for _ in range(3):
            result = self.service.ocr_extract_essay("stu1", IMAGE)
            self.assertTrue(result["ok"])
        self.assertEqual(self.llm.calls, 3)
        self.assertIsNone(self.service.ai_quota_left("stu1"))


if __name__ == "__main__":
    unittest.main()
