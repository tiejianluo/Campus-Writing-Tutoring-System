import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import LLMService
from app.metrics import (
    chinese_word_count,
    generate_topics,
    grade_expectation,
    infer_expression_score,
    infer_structure_score,
    paragraph_count,
    sentence_count,
)
from app.services import AppService
from app.storage import SQLiteStore


class TestMetricsServices(unittest.TestCase):
    def test_metrics_return_bounded_values(self):
        essay = "首先，今天我很高兴。\n然后，我和同学一起活动。\n最后，我明白了合作很重要。"

        self.assertGreater(chinese_word_count(essay), 0)
        self.assertEqual(paragraph_count(essay), 3)
        self.assertEqual(sentence_count(essay), 3)
        self.assertGreaterEqual(infer_structure_score(essay), 60)
        self.assertLessEqual(infer_expression_score(essay), 100)
        self.assertIn("建议字数", grade_expectation("三年级"))
        self.assertGreaterEqual(len(generate_topics("五年级", "想象作文", "未来")), 3)

    def test_service_rejects_overlong_essay(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(db_path=os.path.join(tmpdir, "test.db"), max_essay_chars=4)
            service = AppService(settings, SQLiteStore(settings), LLMService(settings))
            service.initialize()

            with self.assertRaises(ValueError):
                service.review_and_save_submission("student", "三年级", "写事", "题目", "题目", "超过四个字")

    def test_service_saves_submission_growth_and_versions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = Settings(db_path=os.path.join(tmpdir, "test.db"))
            service = AppService(settings, SQLiteStore(settings), LLMService(settings))
            service.initialize()

            sid, feedback = service.review_and_save_submission("student", "三年级", "写事", "题目", "题目", "今天我很高兴。")

            self.assertGreater(sid, 0)
            self.assertIn("teacher_feedback", feedback)
            self.assertEqual(len(service.store.list_student_submissions("student", limit=10)), 1)
            self.assertEqual(len(service.store.list_growth_records("student")), 1)
            self.assertEqual(len(service.store.list_versions(sid)), 1)


if __name__ == "__main__":
    unittest.main()

