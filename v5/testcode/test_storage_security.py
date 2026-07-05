import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import LLMService
from app.services import AppService
from app.storage import SQLiteStore


def make_service(tmpdir: str, seed_demo_users: bool = False) -> AppService:
    settings = Settings(
        db_path=os.path.join(tmpdir, "test.db"),
        seed_demo_users=seed_demo_users,
        demo_password="DemoPass123",
        openai_api_key=None,
    )
    store = SQLiteStore(settings)
    service = AppService(settings, store, LLMService(settings))
    service.initialize()
    return service


class TestStorageSecurity(unittest.TestCase):
    def test_production_init_does_not_seed_demo_accounts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir, seed_demo_users=False)

            self.assertEqual(service.store.list_users(limit=10), [])

    def test_demo_seed_requires_explicit_opt_in_and_custom_password(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir, seed_demo_users=True)

            self.assertIsNotNone(service.login("teacher1", "DemoPass123"))
            self.assertIsNone(service.login("teacher1", "123456"))

    def test_public_registration_allows_only_students(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir)

            ok, _ = service.register_public_student("new_student", "Student123", "学生", "三年级", "三年级一班")
            self.assertTrue(ok)
            ok, message = service.register_public_student("weak_student", "123456", "学生", "三年级", "三年级一班")
            self.assertFalse(ok)
            self.assertIn("密码", message)
            self.assertTrue(service.create_user_by_admin("teacher_a", "Teacher123", "teacher", "老师", None, None))

    def test_teacher_submission_query_is_scoped_to_owned_classes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir)
            service.create_user_by_admin("teacher_a", "Teacher123", "teacher", "甲老师", None, None)
            service.create_user_by_admin("teacher_b", "Teacher123", "teacher", "乙老师", None, None)
            service.create_user_by_admin("student_a", "Student123", "student", "甲学生", "三年级", "三年级一班")
            service.create_user_by_admin("student_b", "Student123", "student", "乙学生", "三年级", "三年级二班")
            service.store.create_class("三年级一班", "三年级", "teacher_a")
            service.store.create_class("三年级二班", "三年级", "teacher_b")

            service.review_and_save_submission("student_a", "三年级", "写事", "甲作文", "甲作文", "今天我很高兴。")
            service.review_and_save_submission("student_b", "三年级", "写事", "乙作文", "乙作文", "今天我很高兴。")

            rows = service.store.list_teacher_submissions("teacher_a", limit=10)

            self.assertEqual([row["student_username"] for row in rows], ["student_a"])
            self.assertIsNone(service.store.get_submission_for_teacher("teacher_a", rows[0]["id"] + 1))

    def test_parent_query_requires_explicit_link(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir)
            service.create_user_by_admin("parent_a", "Parent123", "parent", "家长", None, None)
            service.create_user_by_admin("student_a", "Student123", "student", "甲学生", "三年级", "三年级一班")
            service.create_user_by_admin("student_b", "Student123", "student", "乙学生", "三年级", "三年级二班")
            service.review_and_save_submission("student_a", "三年级", "写事", "甲作文", "甲作文", "今天我很高兴。")
            service.review_and_save_submission("student_b", "三年级", "写事", "乙作文", "乙作文", "今天我很高兴。")
            service.store.link_parent_to_student("parent_a", "student_a")

            self.assertEqual([row["username"] for row in service.store.list_parent_students("parent_a")], ["student_a"])
            self.assertIsNotNone(service.store.latest_submission_for_parent("parent_a", "student_a"))
            self.assertIsNone(service.store.latest_submission_for_parent("parent_a", "student_b"))

    def test_schema_has_indexes_for_common_scoped_queries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            service = make_service(tmpdir)
            conn = sqlite3.connect(service.settings.db_path)
            cur = conn.cursor()

            indexes = {}
            for table in ["users", "classes", "assignments", "submissions", "growth_records", "parent_student_links"]:
                cur.execute(f"PRAGMA index_list({table})")
                indexes[table] = {row[1] for row in cur.fetchall()}
            conn.close()

            self.assertIn("idx_users_role", indexes["users"])
            self.assertIn("idx_classes_teacher", indexes["classes"])
            self.assertIn("idx_assignments_grade_class", indexes["assignments"])
            self.assertIn("idx_submissions_student_created", indexes["submissions"])
            self.assertIn("idx_growth_student_created", indexes["growth_records"])
            self.assertIn("idx_parent_links_parent", indexes["parent_student_links"])


if __name__ == "__main__":
    unittest.main()

