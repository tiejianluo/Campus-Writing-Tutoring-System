"""验收测试：逐条对应《软件测试报告》（2026-06-26，王芳）的缺陷与商业需求。

每个用例的 docstring 标注了对应的报告条目或需求编号。
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import LLMService, SUBJECT_ENGLISH, fallback_feedback, normalize_feedback
from app.services import AppService
from app.storage import SQLiteStore

PASSWORD = "Password8"


def build_service(**overrides) -> AppService:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    settings = Settings(db_path=tmp.name, **overrides)
    service = AppService(settings, SQLiteStore(settings), LLMService(settings))
    service.initialize()
    return service


class TestReportDefects(unittest.TestCase):
    """测试报告 2.2 节缺陷验收。"""

    def setUp(self):
        self.service = build_service(premium_trial_days=0)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        self.service.create_user_by_admin("teacher1", PASSWORD, "teacher", "张老师", None, None)
        _, self.invite = self.service.create_class("teacher1", "三年级二班", "三年级")
        self.service.register_public_student("student1a", PASSWORD, "韩梅梅", "三年级", self.invite)
        self.user = self.service.login("student1a", PASSWORD)

    def test_a2_student_sees_assignment_requirements(self):
        """A-2：学生端必须能看到作文要求（布置说明）。"""
        self.service.create_assignment(
            "teacher1", "熟悉的人的一件事", "写事", "写你身边熟悉的人的一件事，字数要求300字",
            "三年级", "三年级二班", "2026-07-20",
        )
        rows = self.service.store.list_assignments_for_student("三年级", "三年级二班", limit=10)
        self.assertTrue(rows[0]["prompt"])
        self.assertIn("300字", rows[0]["prompt"])

    def test_a3_login_info_contains_grade_and_class(self):
        """A-3：登录信息应包含学生年级与班级。"""
        self.assertEqual(self.user["grade"], "三年级")
        self.assertEqual(self.user["class_name"], "三年级二班")

    def test_a4_class_membership_recognized(self):
        """A-4：学生填写的班级必须被正确识别（邀请码机制），不再被归到默认班。"""
        klass = self.service.store.get_class_by_invite_code(self.invite)
        self.assertEqual(klass["class_name"], "三年级二班")
        self.assertEqual(self.user["class_name"], "三年级二班")

    def test_a5_teacher_sees_published_assignment_history(self):
        """A-5：老师能查到已布置作文题的历史。"""
        self.service.create_assignment(
            "teacher1", "题一", "写人", "", "三年级", "三年级二班", "2026-07-20"
        )
        history = self.service.store.list_teacher_assignments("teacher1", limit=10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["title"], "题一")

    def test_b1_published_assignment_reaches_student(self):
        """B-1：教师下发作文后学生端必须能收到。"""
        self.service.create_assignment(
            "teacher1", "下发测试", "写事", "说明", "三年级", "三年级二班", "2026-07-20"
        )
        rows = self.service.store.list_assignments_for_student(
            self.user["grade"], self.user["class_name"], limit=10
        )
        self.assertEqual([r["title"] for r in rows], ["下发测试"])

    def test_b2_second_rewrite_succeeds(self):
        """B-2：同一篇作文第二次改写不得报错。"""
        sid, _ = self.service.review_and_save_submission(
            "student1a", "三年级", "写事", "我的妈妈", "我的妈妈", "第一版。"
        )
        v2, _ = self.service.rewrite_submission("student1a", sid, "第二版，加了细节。")
        v3, _ = self.service.rewrite_submission("student1a", sid, "第三版，结构更好了。")
        self.assertEqual((v2, v3), (2, 3))

    def test_b2_step_rewrite_never_leaks_raw_json(self):
        """B-2 截图问题：step_rewrite 即使被 LLM 返回成 list 也要归一化成四键 dict。"""
        fallback = fallback_feedback("三年级", "写事", "题", "文")
        for weird in (["a", "b"], "字符串", None, {"其它键": "值"}):
            fixed = normalize_feedback({"step_rewrite": weird}, fallback)
            self.assertIsInstance(fixed["step_rewrite"], dict)
            self.assertEqual(len(fixed["step_rewrite"]), 4)

    def test_b3_rewrite_count_accurate(self):
        """B-3：提交 2 次改写后系统必须记录 3 个版本、仍是 1 篇作文。"""
        sid, _ = self.service.review_and_save_submission(
            "student1a", "三年级", "写事", "题", "题", "第一版。"
        )
        self.service.rewrite_submission("student1a", sid, "第二版。")
        self.service.rewrite_submission("student1a", sid, "第三版。")
        self.assertEqual(len(self.service.store.list_versions(sid)), 3)
        self.assertEqual(len(self.service.store.list_student_submissions("student1a", limit=50)), 1)

    def test_b4_growth_records_show_topic(self):
        """B-4：成长档案必须包含具体作文题目。"""
        self.service.review_and_save_submission(
            "student1a", "三年级", "写人", "我的妈妈", "我的妈妈", "内容。"
        )
        growth = self.service.store.list_growth_records("student1a")
        self.assertEqual(growth[0]["topic"], "我的妈妈")


class SecurityAcceptance(unittest.TestCase):
    """安全验收：默认口令、越权、注册权限。"""

    def setUp(self):
        self.service = build_service(premium_trial_days=0)
        self.addCleanup(os.unlink, self.service.settings.db_path)

    def test_no_default_accounts_without_env(self):
        """默认不得存在 teacher1/123456 等演示账号。"""
        self.assertEqual(self.service.store.list_users(limit=50), [])
        self.assertIsNone(self.service.login("teacher1", "123456"))

    def test_teacher_self_registration_blocked(self):
        from app.security import validate_public_registration

        ok, _ = validate_public_registration(
            "hacker", PASSWORD, "teacher", "黑客", None, {"三年级"}, 8
        )
        self.assertFalse(ok)

    def test_admin_created_user_still_validated(self):
        ok, _ = self.service.create_user_by_admin("t2", "123", "teacher", "弱密码老师", None, None)
        self.assertFalse(ok)

    def test_parent_cannot_view_unbound_student(self):
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)
        self.service.review_and_save_submission("stu1", "三年级", "写事", "题", "题", "内容。")
        self.service.create_user_by_admin("p1", PASSWORD, "parent", "家长", None, None)
        self.assertIsNone(self.service.store.latest_submission_for_parent("p1", "stu1"))


class BusinessAcceptance(unittest.TestCase):
    """商业需求验收：定价 26/288、免费额度、演示免费、高级付费。"""

    def setUp(self):
        self.service = build_service(premium_trial_days=0)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)

    def test_pricing_26_month_288_year(self):
        month = self.service.create_payment_order("stu1", "month")
        year = self.service.create_payment_order("stu1", "year")
        self.assertEqual(month["amount"], 26)
        self.assertEqual(year["amount"], 288)

    def test_free_tier_can_still_write_and_get_feedback(self):
        """演示功能免费：免费用户随时可提交并获得（基础）点评。"""
        sid, feedback = self.service.review_and_save_submission(
            "stu1", "三年级", "写事", "题", "题", "内容。"
        )
        self.assertGreater(sid, 0)
        self.assertIn("teacher_feedback", feedback)

    def test_premium_activation_via_paid_order(self):
        order = self.service.create_payment_order("stu1", "year")
        self.service.confirm_order(order["order_no"])
        status = self.service.premium_status("stu1")
        self.assertEqual(status["plan"], "year")

    def test_quota_visible_to_free_user(self):
        self.assertEqual(self.service.ai_quota_left("stu1"), self.service.settings.free_ai_daily_quota)

    def test_local_basic_feedback_unlimited_after_quota(self):
        """商业需求：每天 3 次 AI 点评，本地基础点评始终不限次（额度用完不拦截提交）。"""
        for _ in range(self.service.settings.free_ai_daily_quota):
            self.service.store.increment_ai_usage("stu1")
        self.assertEqual(self.service.ai_quota_left("stu1"), 0)
        sid, feedback = self.service.review_and_save_submission(
            "stu1", "三年级", "写事", "题", "题", "内容。"
        )
        self.assertGreater(sid, 0)
        self.assertEqual(feedback["source"], "fallback")
        self.assertEqual(feedback["fallback_reason"], "quota_exhausted")


class EnglishWritingAcceptance(unittest.TestCase):
    """K12 英语写作验收：分年级题型、英文计数、双语反馈、成长档案入档。"""

    def setUp(self):
        self.service = build_service(premium_trial_days=0)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)

    def test_grade_specific_genres(self):
        from app.content_en import english_genres_for_grade

        g3 = english_genres_for_grade("三年级")
        g6 = english_genres_for_grade("六年级")
        self.assertIn("About Me / My Family 自我介绍", g3)
        self.assertIn("Story / My Dream 小故事与梦想", g6)
        self.assertNotIn("Story / My Dream 小故事与梦想", g3)

    def test_english_submission_recorded_with_subject(self):
        sid, feedback = self.service.review_and_save_submission(
            "stu1", "三年级", "Picture Description 看图写话", "My Classroom", "My Classroom",
            "In the picture, I can see my classroom. It is big and clean. First we read books. Then we play. I am very happy.",
            subject=SUBJECT_ENGLISH,
        )
        sub = self.service.store.get_submission_for_student("stu1", sid)
        self.assertEqual(sub["subject"], "english")
        growth = self.service.store.list_growth_records("stu1")
        self.assertEqual(growth[0]["subject"], "english")
        self.assertEqual(growth[0]["topic"], "My Classroom")
        # 双语反馈字段
        self.assertIn("grammar_corrections", feedback)
        self.assertTrue(feedback["strengths"])


if __name__ == "__main__":
    unittest.main()
