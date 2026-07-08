from typing import Any, Optional

from .config import Settings
from .content import GRADE_RUBRICS
from .llm import (
    FALLBACK_NO_API_KEY,
    FALLBACK_QUOTA,
    SUBJECT_CHINESE,
    SUBJECT_ENGLISH,
    LLMService,
    fallback_feedback,
    fallback_feedback_en,
)
from .metrics import chinese_word_count, infer_expression_score, infer_structure_score
from .metrics_en import english_word_count, infer_expression_score_en, infer_structure_score_en
from .rate_limit import FixedWindowRateLimiter
from .security import normalize_username, validate_public_registration, validate_username_password
from .storage import SQLiteStore

PLAN_DAYS = {"month": 31, "year": 366}

# Premium feature identifiers used by the UI for gating.
PREMIUM_FEATURES = {"rewrite", "version_compare", "image_prompts", "english_ai", "growth_report"}


class QuotaExceededError(Exception):
    """Deprecated in v7: quota exhaustion now degrades to local feedback instead of blocking."""


class AppService:
    def __init__(self, settings: Settings, store: SQLiteStore, llm: LLMService):
        self.settings = settings
        self.store = store
        self.llm = llm
        self.login_limiter = FixedWindowRateLimiter(settings.login_attempts_per_minute)

    def initialize(self) -> None:
        self.store.initialize()
        self._bootstrap_admin()

    def _bootstrap_admin(self) -> None:
        """Create the platform admin from ESSAY_APP_ADMIN_USER/PASSWORD on first start."""
        username = self.settings.admin_username
        password = self.settings.admin_password
        if not username or not password:
            return
        ok, _ = validate_username_password(username, password, self.settings.min_password_length)
        if not ok:
            return
        if self.store.get_user(normalize_username(username)):
            return
        self.store.create_user(normalize_username(username), password, "admin", "平台管理员", None, None)

    # ------------------------------------------------------------------
    # Auth / registration
    # ------------------------------------------------------------------
    def login(self, username: str, password: str) -> Optional[dict[str, Any]]:
        username = normalize_username(username)
        if not self.login_limiter.allow(f"login:{username}"):
            return None
        return self.store.authenticate(username, password)

    def register_public_student(
        self,
        username: str,
        password: str,
        real_name: str,
        grade: str,
        invite_code: Optional[str] = None,
    ) -> tuple[bool, str]:
        class_name = None
        if invite_code and invite_code.strip():
            klass = self.store.get_class_by_invite_code(invite_code)
            if not klass:
                return False, "班级邀请码无效，请与老师核对。"
            class_name = klass["class_name"]
            grade = klass["grade"]
        ok, message = validate_public_registration(
            username=username,
            password=password,
            role="student",
            real_name=real_name,
            grade=grade,
            valid_grades=set(GRADE_RUBRICS),
            min_password_length=self.settings.min_password_length,
        )
        if not ok:
            return False, message
        created = self.store.create_user(
            normalize_username(username), password, "student", real_name.strip(), grade, class_name
        )
        if not created:
            return False, "用户名已存在。"
        if self.settings.premium_trial_days > 0:
            self.store.create_subscription(normalize_username(username), "trial", self.settings.premium_trial_days)
        if class_name:
            return True, f"注册成功，已加入 {class_name}，请登录。"
        return True, "注册成功，请登录。"

    def create_user_by_admin(
        self,
        username: str,
        password: str,
        role: str,
        real_name: str,
        grade: Optional[str],
        class_name: Optional[str],
    ) -> tuple[bool, str]:
        ok, message = validate_username_password(username, password, self.settings.min_password_length)
        if not ok:
            return False, message
        if not real_name.strip():
            return False, "姓名不能为空。"
        created = self.store.create_user(
            normalize_username(username), password, role, real_name.strip(), grade, class_name
        )
        return (True, "已创建。") if created else (False, "用户名已存在或角色无效。")

    # ------------------------------------------------------------------
    # Classes / assignments
    # ------------------------------------------------------------------
    def create_class(self, teacher_username: str, class_name: str, grade: str) -> tuple[bool, str]:
        code = self.store.create_class(class_name.strip(), grade, teacher_username)
        if code is None:
            return False, "班级名称已存在，请换一个名称。"
        return True, code

    def create_assignment(
        self,
        teacher_username: str,
        title: str,
        genre: str,
        prompt: str,
        grade: str,
        class_name: str,
        due_date: str,
        subject: str = SUBJECT_CHINESE,
    ) -> int:
        klass = self.store.get_class(class_name)
        if not klass or klass["teacher_username"] != teacher_username:
            raise PermissionError("只能给自己创建的班级布置作业。")
        return self.store.create_assignment(
            {
                "title": title.strip(),
                "genre": genre,
                "subject": subject,
                "prompt": prompt.strip(),
                "grade": grade,
                "class_name": class_name,
                "teacher_username": teacher_username,
                "due_date": due_date,
            }
        )

    # ------------------------------------------------------------------
    # Essay review flows
    # ------------------------------------------------------------------
    def _score(self, essay_text: str, grade: str, subject: str) -> tuple[int, int, int, int]:
        if subject == SUBJECT_ENGLISH:
            wc = english_word_count(essay_text)
            structure = infer_structure_score_en(essay_text, grade)
            expression = infer_expression_score_en(essay_text, grade)
        else:
            wc = chinese_word_count(essay_text)
            structure = infer_structure_score(essay_text)
            expression = infer_expression_score(essay_text)
        total = int((structure + expression) / 2)
        return wc, structure, expression, total

    def _feedback_with_quota(
        self, student_username: str, grade: str, genre: str, title: str, essay_text: str, subject: str
    ) -> dict[str, Any]:
        """AI feedback with free-tier daily quota; premium users are unlimited.

        v7 语义修正：免费额度用完时不再拦截提交，而是回退到不限次的
        本地基础点评（README 承诺"本地基础点评始终不限次"）。
        """
        if not self.is_premium(student_username):
            used = self.store.get_ai_usage_today(student_username)
            if used >= self.settings.free_ai_daily_quota:
                builder = fallback_feedback_en if subject == SUBJECT_ENGLISH else fallback_feedback
                feedback = builder(grade, genre, title, essay_text)
                feedback["fallback_reason"] = FALLBACK_QUOTA
                return feedback
        feedback = self.llm.essay_feedback(
            grade, genre, title, essay_text, user_key=student_username, subject=subject
        )
        if feedback.get("source") == "llm" and not self.is_premium(student_username):
            self.store.increment_ai_usage(student_username)
        return feedback

    def review_and_save_submission(
        self,
        student_username: str,
        grade: str,
        genre: str,
        title: str,
        prompt: str,
        essay_text: str,
        assignment_id: Optional[int] = None,
        subject: str = SUBJECT_CHINESE,
    ) -> tuple[int, dict[str, Any]]:
        if len(essay_text) > self.settings.max_essay_chars:
            raise ValueError(f"作文过长，最多允许 {self.settings.max_essay_chars} 个字符。")

        feedback = self._feedback_with_quota(student_username, grade, genre, title, essay_text, subject)
        wc, structure, expression, total = self._score(essay_text, grade, subject)
        submission_id = self.store.save_submission(
            {
                "assignment_id": assignment_id,
                "student_username": student_username,
                "title": title,
                "genre": genre,
                "subject": subject,
                "prompt": prompt,
                "essay_text": essay_text,
                "word_count": wc,
                "structure_score": structure,
                "expression_score": expression,
                "total_score": total,
                "teacher_feedback": feedback["teacher_feedback"],
                "student_feedback": feedback["student_feedback"],
                "step_rewrite": feedback["step_rewrite"],
                "feedback_json": feedback,
            }
        )
        return submission_id, feedback

    def rewrite_submission(
        self, student_username: str, submission_id: int, new_essay_text: str
    ) -> tuple[int, dict[str, Any]]:
        """Save a revision as a new version of the same submission (never a new one)."""
        original = self.store.get_submission_for_student(student_username, submission_id)
        if not original:
            raise PermissionError("只能改写自己的作文。")
        if len(new_essay_text) > self.settings.max_essay_chars:
            raise ValueError(f"作文过长，最多允许 {self.settings.max_essay_chars} 个字符。")

        grade_user = self.store.get_user(student_username) or {}
        grade = grade_user.get("grade") or "三年级"
        subject = original.get("subject", SUBJECT_CHINESE)
        feedback = self._feedback_with_quota(
            student_username, grade, original["genre"], original["title"], new_essay_text, subject
        )
        wc, structure, expression, total = self._score(new_essay_text, grade, subject)
        version_no = self.store.add_version(
            submission_id,
            {
                "student_username": student_username,
                "title": original["title"],
                "genre": original["genre"],
                "subject": subject,
                "essay_text": new_essay_text,
                "word_count": wc,
                "structure_score": structure,
                "expression_score": expression,
                "total_score": total,
                "teacher_feedback": feedback["teacher_feedback"],
                "student_feedback": feedback["student_feedback"],
                "step_rewrite": feedback["step_rewrite"],
                "feedback_json": feedback,
            },
        )
        return version_no, feedback

    # ------------------------------------------------------------------
    # Subscription / premium
    # ------------------------------------------------------------------
    def is_premium(self, username: str) -> bool:
        return self.store.get_active_subscription(username) is not None

    def premium_status(self, username: str) -> Optional[dict[str, Any]]:
        return self.store.get_active_subscription(username)

    def plan_amount(self, plan: str) -> int:
        return self.settings.premium_price_month if plan == "month" else self.settings.premium_price_year

    def create_payment_order(self, username: str, plan: str) -> dict[str, Any]:
        if plan not in PLAN_DAYS:
            raise ValueError("无效的套餐类型。")
        return self.store.create_order(username, plan, self.plan_amount(plan))

    def confirm_order(self, order_no: str) -> tuple[bool, str]:
        """Admin confirms a payment against the QR transfer, then activates."""
        order = self.store.mark_order_paid(order_no)
        if not order:
            return False, "订单不存在或已处理。"
        sub = self.store.create_subscription(order["username"], order["plan"], PLAN_DAYS[order["plan"]])
        return True, f"已为 {order['username']} 开通会员至 {sub['expires_at'][:10]}。"

    def redeem_code(self, username: str, code: str) -> tuple[bool, str]:
        plan = self.store.redeem_activation_code(code, username)
        if not plan:
            return False, "激活码无效或已被使用。"
        sub = self.store.create_subscription(username, plan, PLAN_DAYS[plan])
        return True, f"激活成功，会员有效期至 {sub['expires_at'][:10]}。"

    def ocr_extract_essay(self, username: str, image) -> dict[str, Any]:
        """v8：手写作文照片文字提取。

        识别必须调用视觉大模型，没有本地回退，因此：
        - 未配置 AI 密钥 → 直接返回失败原因（UI 提示可手动输入）；
        - 免费用户每日 AI 额度用完 → 返回失败原因（识别与点评共用同一额度）；
        - 识别成功且为免费用户 → 扣减一次每日额度（会员不限次）。
        """
        if not self.llm.is_configured():
            return {"ok": False, "text": "", "reason": FALLBACK_NO_API_KEY}
        premium = self.is_premium(username)
        if not premium:
            used = self.store.get_ai_usage_today(username)
            if used >= self.settings.free_ai_daily_quota:
                return {"ok": False, "text": "", "reason": FALLBACK_QUOTA}
        result = self.llm.ocr_essay_image(image, user_key=username)
        if result.get("ok") and not premium:
            self.store.increment_ai_usage(username)
        return result

    def ai_quota_left(self, username: str) -> Optional[int]:
        """Remaining free AI reviews today; None means unlimited (premium)."""
        if self.is_premium(username):
            return None
        return max(0, self.settings.free_ai_daily_quota - self.store.get_ai_usage_today(username))

    def page_size(self, requested: int | None = None) -> int:
        value = requested or self.settings.default_page_size
        return min(max(1, value), self.settings.max_page_size)

    # ------------------------------------------------------------------
    # Admin: account management / operations dashboard
    # ------------------------------------------------------------------
    def set_user_active(self, admin_username: str, target_username: str, active: bool) -> tuple[bool, str]:
        """人工开通/注销账号。注销＝停用（数据保留），可随时重新开通。"""
        target = self.store.get_user(target_username)
        if not target:
            return False, "用户不存在。"
        if target_username == admin_username and not active:
            return False, "不能注销当前登录的管理员自己。"
        self.store.set_user_status(target_username, "active" if active else "disabled")
        return True, f"已{'开通' if active else '注销'}账号 {target_username}。"

    def admin_reset_password(self, target_username: str, new_password: str) -> tuple[bool, str]:
        ok, message = validate_username_password(target_username, new_password, self.settings.min_password_length)
        if not ok:
            return False, message
        if not self.store.get_user(target_username):
            return False, "用户不存在。"
        self.store.update_password(target_username, new_password)
        return True, f"已重置 {target_username} 的密码。"

    def dashboard_stats(self) -> dict[str, Any]:
        return self.store.dashboard_stats()

    def llm_status(self) -> dict[str, Any]:
        return self.llm.status()
