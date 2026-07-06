"""单元测试：密码/校验、限流器、上传边界、中英文评分引擎、LLM 回退与归一化、配置。"""

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings, get_config_bool
from app.content_en import ENGLISH_GRADE_RUBRICS, ENGLISH_TEMPLATES, english_genres_for_grade
from app.llm import (
    STEP_REWRITE_KEYS,
    fallback_feedback,
    fallback_feedback_en,
    normalize_feedback,
)
from app.metrics import chinese_word_count, infer_expression_score, infer_structure_score
from app.metrics_en import (
    capitalization_ratio,
    english_word_count,
    infer_expression_score_en,
    infer_structure_score_en,
    linking_words_found,
    vocabulary_variety,
)
from app.rate_limit import FixedWindowRateLimiter
from app.security import (
    hash_password,
    validate_public_registration,
    validate_username_password,
    verify_password,
)
from app.uploads import UploadValidationError, read_uploaded_text

GOOD_EN_ESSAY = (
    "My name is Ming. I am ten years old. First, I get up at seven o'clock. "
    "Then I go to school with my best friend. We are very happy. "
    "After school, I play football. Finally, I do my homework and go to bed. "
    "What a wonderful day!"
)


class TestSecurity(unittest.TestCase):
    def test_hash_and_verify_roundtrip(self):
        hashed = hash_password("Secret123")
        self.assertTrue(verify_password("Secret123", hashed))
        self.assertFalse(verify_password("wrong", hashed))

    def test_public_registration_rejects_non_student(self):
        ok, msg = validate_public_registration(
            "user1", "password8", "teacher", "某人", "三年级", {"三年级"}, 8
        )
        self.assertFalse(ok)
        self.assertIn("学生", msg)

    def test_public_registration_password_length(self):
        ok, _ = validate_public_registration("user1", "short", "student", "某人", "三年级", {"三年级"}, 8)
        self.assertFalse(ok)

    def test_username_password_shared_validation(self):
        self.assertFalse(validate_username_password("a", "password8", 8)[0])
        self.assertFalse(validate_username_password("gooduser", "short", 8)[0])
        self.assertTrue(validate_username_password("gooduser", "password8", 8)[0])


class TestRateLimiter(unittest.TestCase):
    def test_limit_enforced_and_window_slides(self):
        limiter = FixedWindowRateLimiter(limit=2, window_seconds=60)
        self.assertTrue(limiter.allow("u", now=0))
        self.assertTrue(limiter.allow("u", now=1))
        self.assertFalse(limiter.allow("u", now=2))
        self.assertTrue(limiter.allow("u", now=61.5))

    def test_keys_are_independent(self):
        limiter = FixedWindowRateLimiter(limit=1)
        self.assertTrue(limiter.allow("a", now=0))
        self.assertTrue(limiter.allow("b", now=0))


class TestUploads(unittest.TestCase):
    def test_oversized_text_rejected(self):
        settings = Settings(max_text_upload_bytes=10)
        big = io.BytesIO(b"x" * 11)
        with self.assertRaises(UploadValidationError):
            read_uploaded_text(big, settings)

    def test_text_decoded(self):
        settings = Settings()
        data = io.BytesIO("你好 hello".encode("utf-8"))
        self.assertEqual(read_uploaded_text(data, settings), "你好 hello")


class TestChineseMetrics(unittest.TestCase):
    def test_word_count_only_han(self):
        self.assertEqual(chinese_word_count("我爱abc学习123"), 4)

    def test_scores_bounded(self):
        essay = "首先我很高兴。\n然后像花一样。\n最后！" + "内容" * 200
        self.assertLessEqual(infer_structure_score(essay), 100)
        self.assertLessEqual(infer_expression_score(essay), 100)
        self.assertGreaterEqual(infer_structure_score(""), 60)


class TestEnglishMetrics(unittest.TestCase):
    def test_english_word_count(self):
        self.assertEqual(english_word_count("I don't like it"), 4)
        self.assertEqual(english_word_count("你好"), 0)

    def test_capitalization_ratio(self):
        self.assertAlmostEqual(capitalization_ratio("I am here. she is here."), 0.5)

    def test_linking_words(self):
        found = linking_words_found(GOOD_EN_ESSAY)
        self.assertIn("first", found)
        self.assertIn("finally", found)

    def test_vocabulary_variety_range(self):
        self.assertGreater(vocabulary_variety(GOOD_EN_ESSAY), 0.5)

    def test_scores_reward_good_essay(self):
        weak = "i like it"
        self.assertGreater(
            infer_structure_score_en(GOOD_EN_ESSAY, "四年级"),
            infer_structure_score_en(weak, "四年级"),
        )
        self.assertGreater(
            infer_expression_score_en(GOOD_EN_ESSAY, "四年级"),
            infer_expression_score_en(weak, "四年级"),
        )


class TestEnglishContent(unittest.TestCase):
    def test_all_grades_have_rubric_and_targets(self):
        for grade in ["三年级", "四年级", "五年级", "六年级"]:
            self.assertIn(grade, ENGLISH_GRADE_RUBRICS)
            low, high = ENGLISH_GRADE_RUBRICS[grade]["target_words"]
            self.assertLess(low, high)
            self.assertTrue(english_genres_for_grade(grade))

    def test_templates_complete(self):
        for genre, tpl in ENGLISH_TEMPLATES.items():
            self.assertIn("结构", tpl)
            self.assertIn("万能开头", tpl)
            self.assertIn("万能结尾", tpl)
            self.assertTrue(tpl["grades"], genre)


class TestFeedbackFallbackAndNormalize(unittest.TestCase):
    REQUIRED = ("teacher_feedback", "student_feedback", "strengths", "suggestions", "step_rewrite")

    def test_chinese_fallback_schema(self):
        fb = fallback_feedback("三年级", "写事", "一件难忘的事", "我今天很高兴。")
        for key in self.REQUIRED:
            self.assertIn(key, fb)
        self.assertEqual(fb["source"], "fallback")
        self.assertEqual(set(fb["step_rewrite"]), set(STEP_REWRITE_KEYS))

    def test_english_fallback_schema(self):
        fb = fallback_feedback_en("四年级", "Diary 英语日记", "My Happy Day", GOOD_EN_ESSAY)
        for key in self.REQUIRED:
            self.assertIn(key, fb)
        self.assertIn("grammar_corrections", fb)
        self.assertEqual(len(fb["strengths"]), 3)

    def test_normalize_repairs_list_step_rewrite(self):
        """B 版事故场景：LLM 把 step_rewrite 返回成 list。"""
        fallback = fallback_feedback("三年级", "写事", "题", "文")
        raw = {"teacher_feedback": "好", "step_rewrite": ["补内容", "改句子"]}
        fixed = normalize_feedback(raw, fallback)
        self.assertIsInstance(fixed["step_rewrite"], dict)
        self.assertEqual(set(fixed["step_rewrite"]), set(STEP_REWRITE_KEYS))
        self.assertEqual(fixed["source"], "llm")

    def test_normalize_fills_missing_keys(self):
        fallback = fallback_feedback("三年级", "写事", "题", "文")
        fixed = normalize_feedback({}, fallback)
        for key in self.REQUIRED:
            self.assertIn(key, fixed)

    def test_normalize_rejects_non_dict(self):
        fallback = fallback_feedback("三年级", "写事", "题", "文")
        self.assertEqual(normalize_feedback("garbage", fallback), fallback)


class TestConfig(unittest.TestCase):
    def test_bool_parsing(self):
        os.environ["V6_TEST_FLAG"] = "true"
        try:
            self.assertTrue(get_config_bool("V6_TEST_FLAG"))
        finally:
            del os.environ["V6_TEST_FLAG"]
        self.assertFalse(get_config_bool("V6_TEST_MISSING", default=False))

    def test_pricing_defaults(self):
        settings = Settings()
        self.assertEqual(settings.premium_price_month, 26)
        self.assertEqual(settings.premium_price_year, 288)
        self.assertEqual(settings.free_ai_daily_quota, 3)


if __name__ == "__main__":
    unittest.main()
