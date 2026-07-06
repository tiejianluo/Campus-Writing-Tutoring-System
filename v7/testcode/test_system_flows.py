"""系统测试：在临时数据库上跑通端到端业务流。

覆盖：注册（含邀请码）→ 登录 → 建班 → 布置作业 → 学生可见 →
提交点评 → 继续改写（版本语义）→ 版本对比数据 → 成长档案 →
订阅/订单/激活码 → 权限边界。
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import Settings
from app.llm import FALLBACK_QUOTA, LLMService, SUBJECT_ENGLISH
from app.services import AppService
from app.storage import SQLiteStore

PASSWORD = "Password8"


def build_service(**settings_overrides) -> AppService:
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    settings = Settings(db_path=tmp.name, **settings_overrides)
    service = AppService(settings, SQLiteStore(settings), LLMService(settings))
    service.initialize()
    return service


class SystemFlowTest(unittest.TestCase):
    def setUp(self):
        self.service = build_service(premium_trial_days=0)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        # 教师与班级
        ok, _ = self.service.create_user_by_admin("teacher1", PASSWORD, "teacher", "张老师", None, None)
        self.assertTrue(ok)
        ok, self.invite_code = self.service.create_class("teacher1", "三年级一班", "三年级")
        self.assertTrue(ok)

    def register_student(self, username="stu1", invite=True):
        ok, msg = self.service.register_public_student(
            username, PASSWORD, "小明", "三年级", self.invite_code if invite else None
        )
        self.assertTrue(ok, msg)
        return self.service.login(username, PASSWORD)

    def test_registration_with_invite_code_joins_class(self):
        user = self.register_student()
        self.assertEqual(user["class_name"], "三年级一班")
        self.assertEqual(user["grade"], "三年级")

    def test_invalid_invite_code_rejected(self):
        ok, msg = self.service.register_public_student("stu2", PASSWORD, "小红", "三年级", "WRONG1")
        self.assertFalse(ok)
        self.assertIn("邀请码", msg)

    def test_login_rate_limited(self):
        service = build_service(login_attempts_per_minute=3, premium_trial_days=0)
        self.addCleanup(os.unlink, service.settings.db_path)
        for _ in range(3):
            service.login("nobody", "bad")
        # 第 4 次直接被限流拒绝（即使密码正确也拒绝，防爆破）
        self.assertIsNone(service.login("nobody", "bad"))

    def test_assignment_reaches_student_with_prompt(self):
        user = self.register_student()
        self.service.create_assignment(
            "teacher1", "一件难忘的事", "写事", "写你身边熟悉的人的一件事，字数要求300字", "三年级", "三年级一班", "2026-07-20"
        )
        rows = self.service.store.list_assignments_for_student(user["grade"], user["class_name"], limit=50)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "一件难忘的事")
        self.assertIn("300字", rows[0]["prompt"])

    def test_assignment_requires_owned_class(self):
        self.service.create_user_by_admin("teacher2", PASSWORD, "teacher", "李老师", None, None)
        with self.assertRaises(PermissionError):
            self.service.create_assignment(
                "teacher2", "题", "写事", "", "三年级", "三年级一班", "2026-07-20"
            )

    def test_submit_review_and_growth_record(self):
        user = self.register_student()
        sid, feedback = self.service.review_and_save_submission(
            user["username"], "三年级", "写事", "一件难忘的事", "一件难忘的事", "今天我很高兴。\n首先我们去公园。\n最后回家了。"
        )
        self.assertGreater(sid, 0)
        self.assertEqual(feedback["source"], "fallback")  # 无 API key
        growth = self.service.store.list_growth_records(user["username"])
        self.assertEqual(len(growth), 1)
        self.assertEqual(growth[0]["topic"], "一件难忘的事")

    def test_rewrite_appends_versions_not_submissions(self):
        user = self.register_student()
        sid, _ = self.service.review_and_save_submission(
            user["username"], "三年级", "写事", "题目", "题目", "第一版内容。"
        )
        v2, _ = self.service.rewrite_submission(user["username"], sid, "第二版内容，更加充实了。")
        v3, _ = self.service.rewrite_submission(user["username"], sid, "第三版内容，写得更好了，还加了细节。")
        self.assertEqual((v2, v3), (2, 3))
        # 不产生新 submission
        submissions = self.service.store.list_student_submissions(user["username"], limit=50)
        self.assertEqual(len(submissions), 1)
        versions = self.service.store.list_versions(sid)
        self.assertEqual([v["version_no"] for v in versions], [1, 2, 3])
        # submission 主记录刷新为最新版本
        latest = self.service.store.get_submission_for_student(user["username"], sid)
        self.assertIn("第三版", latest["essay_text"])

    def test_rewrite_other_students_essay_forbidden(self):
        user = self.register_student()
        sid, _ = self.service.review_and_save_submission(
            user["username"], "三年级", "写事", "题目", "题目", "内容。"
        )
        self.register_student("stu9")
        with self.assertRaises(PermissionError):
            self.service.rewrite_submission("stu9", sid, "偷改别人的作文")

    def test_english_submission_flow(self):
        user = self.register_student()
        sid, feedback = self.service.review_and_save_submission(
            user["username"], "三年级", "Picture Description 看图写话", "My Classroom", "My Classroom",
            "In the picture, I can see my classroom. It is big and clean. I like it very much.",
            subject=SUBJECT_ENGLISH,
        )
        self.assertGreater(sid, 0)
        self.assertIn("grammar_corrections", feedback)
        sub = self.service.store.get_submission_for_student(user["username"], sid)
        self.assertEqual(sub["subject"], "english")
        self.assertGreater(sub["word_count"], 10)  # 英文按单词计数

    def test_teacher_sees_class_submissions_only(self):
        user = self.register_student()
        self.service.review_and_save_submission(user["username"], "三年级", "写事", "题", "题", "内容。")
        rows = self.service.store.list_teacher_submissions("teacher1", limit=50)
        self.assertEqual(len(rows), 1)
        self.service.create_user_by_admin("teacher2", PASSWORD, "teacher", "李老师", None, None)
        self.assertEqual(self.service.store.list_teacher_submissions("teacher2", limit=50), [])

    def test_parent_permission_boundary(self):
        user = self.register_student()
        self.service.review_and_save_submission(user["username"], "三年级", "写事", "题", "题", "内容。")
        self.service.create_user_by_admin("parent1", PASSWORD, "parent", "家长", None, None)
        # 未绑定不可见
        self.assertIsNone(self.service.store.latest_submission_for_parent("parent1", user["username"]))
        self.service.store.link_parent_to_student("parent1", user["username"])
        self.assertIsNotNone(self.service.store.latest_submission_for_parent("parent1", user["username"]))

    def test_duplicate_class_name_reports_conflict(self):
        ok, message = self.service.create_class("teacher1", "三年级一班", "三年级")
        self.assertFalse(ok)
        self.assertIn("已存在", message)

    def test_subscription_order_flow(self):
        user = self.register_student()
        self.assertFalse(self.service.is_premium(user["username"]))
        order = self.service.create_payment_order(user["username"], "month")
        self.assertEqual(order["amount"], 26)
        self.assertEqual(len(self.service.store.list_pending_orders()), 1)
        ok, message = self.service.confirm_order(order["order_no"])
        self.assertTrue(ok, message)
        self.assertTrue(self.service.is_premium(user["username"]))
        # 重复核销被拒绝
        self.assertFalse(self.service.confirm_order(order["order_no"])[0])

    def test_activation_code_flow(self):
        user = self.register_student()
        code = self.service.store.create_activation_code("year", "admin")
        ok, message = self.service.redeem_code(user["username"], code)
        self.assertTrue(ok, message)
        self.assertTrue(self.service.is_premium(user["username"]))
        # 一次性
        self.register_student("stu8")
        self.assertFalse(self.service.redeem_code("stu8", code)[0])

    def test_trial_granted_on_registration(self):
        service = build_service(premium_trial_days=7)
        self.addCleanup(os.unlink, service.settings.db_path)
        service.register_public_student("trialstu", PASSWORD, "试用生", "三年级", None)
        self.assertTrue(service.is_premium("trialstu"))
        status = service.premium_status("trialstu")
        self.assertEqual(status["plan"], "trial")


class QuotaTest(unittest.TestCase):
    """免费额度：无 API key 时走本地引擎不扣额度；额度耗尽时回退基础点评（不限次，不拦截提交）。"""

    def setUp(self):
        self.service = build_service(premium_trial_days=0, free_ai_daily_quota=2)
        self.addCleanup(os.unlink, self.service.settings.db_path)
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)

    def test_fallback_feedback_does_not_consume_quota(self):
        for _ in range(5):
            self.service.review_and_save_submission("stu1", "三年级", "写事", "题", "题", "内容。")
        self.assertEqual(self.service.ai_quota_left("stu1"), 2)

    def test_quota_exhausted_falls_back_to_local_feedback(self):
        """v7 语义：额度用完后提交不被拦截，返回带 quota 标记的基础点评。"""
        self.service.store.increment_ai_usage("stu1")
        self.service.store.increment_ai_usage("stu1")
        self.assertEqual(self.service.ai_quota_left("stu1"), 0)
        feedback = self.service._feedback_with_quota("stu1", "三年级", "写事", "题", "内容。", "chinese")
        self.assertEqual(feedback["source"], "fallback")
        self.assertEqual(feedback["fallback_reason"], FALLBACK_QUOTA)
        # 整个提交流程也不报错、正常保存
        sid, _ = self.service.review_and_save_submission("stu1", "三年级", "写事", "题", "题", "内容。")
        self.assertGreater(sid, 0)

    def test_premium_bypasses_quota(self):
        code = self.service.store.create_activation_code("month", "admin")
        self.service.redeem_code("stu1", code)
        self.service.store.increment_ai_usage("stu1")
        self.service.store.increment_ai_usage("stu1")
        self.assertIsNone(self.service.ai_quota_left("stu1"))
        feedback = self.service._feedback_with_quota("stu1", "三年级", "写事", "题", "内容。", "chinese")
        self.assertIn("teacher_feedback", feedback)

    def test_fallback_reason_reported_when_no_api_key(self):
        """无 API key 时反馈必须标注原因，UI 才能准确提示。"""
        feedback = self.service._feedback_with_quota("stu1", "三年级", "写事", "题", "内容。", "chinese")
        self.assertEqual(feedback["source"], "fallback")
        self.assertEqual(feedback["fallback_reason"], "no_api_key")


class AdminTest(unittest.TestCase):
    """v7 管理后台：引导管理员、人工开通/注销账号、重置密码、运营统计。"""

    def setUp(self):
        self.service = build_service(
            premium_trial_days=0, admin_username="admin1", admin_password="AdminPass8"
        )
        self.addCleanup(os.unlink, self.service.settings.db_path)

    def test_bootstrap_admin_created_and_can_login(self):
        admin = self.service.login("admin1", "AdminPass8")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

    def test_bootstrap_admin_not_duplicated(self):
        self.service.initialize()  # 再次启动不会重复创建/报错
        users = [u for u in self.service.store.list_users(limit=50) if u["username"] == "admin1"]
        self.assertEqual(len(users), 1)

    def test_disable_user_blocks_login_and_reenable_restores(self):
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)
        ok, _ = self.service.set_user_active("admin1", "stu1", active=False)
        self.assertTrue(ok)
        self.assertIsNone(self.service.login("stu1", PASSWORD))
        ok, _ = self.service.set_user_active("admin1", "stu1", active=True)
        self.assertTrue(ok)
        self.assertIsNotNone(self.service.login("stu1", PASSWORD))

    def test_admin_cannot_disable_self(self):
        ok, message = self.service.set_user_active("admin1", "admin1", active=False)
        self.assertFalse(ok)
        self.assertIn("不能注销", message)

    def test_admin_reset_password(self):
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)
        ok, _ = self.service.admin_reset_password("stu1", "NewPass888")
        self.assertTrue(ok)
        self.assertIsNone(self.service.login("stu1", PASSWORD))
        self.assertIsNotNone(self.service.login("stu1", "NewPass888"))

    def test_dashboard_stats_counts(self):
        self.service.register_public_student("stu1", PASSWORD, "小明", "三年级", None)
        self.service.review_and_save_submission("stu1", "三年级", "写事", "题", "题", "内容。")
        order = self.service.create_payment_order("stu1", "month")
        self.service.confirm_order(order["order_no"])
        stats = self.service.dashboard_stats()
        self.assertEqual(stats["users_by_role"].get("student"), 1)
        self.assertEqual(stats["users_by_role"].get("admin"), 1)
        self.assertEqual(stats["submissions_total"], 1)
        self.assertEqual(stats["submissions_today"], 1)
        self.assertEqual(stats["active_members"], 1)
        self.assertEqual(stats["paid_revenue"], 26)
        self.assertEqual(stats["pending_orders"], 0)
        self.assertTrue(stats["daily_submissions"])

    def test_llm_status_reports_unconfigured(self):
        status = self.service.llm_status()
        self.assertFalse(status["configured"])


if __name__ == "__main__":
    unittest.main()
