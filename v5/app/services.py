from typing import Any, Optional

from .config import Settings
from .content import GRADE_RUBRICS
from .llm import LLMService
from .metrics import chinese_word_count, infer_expression_score, infer_structure_score
from .security import normalize_username, validate_public_registration
from .storage import SQLiteStore


class AppService:
    def __init__(self, settings: Settings, store: SQLiteStore, llm: LLMService):
        self.settings = settings
        self.store = store
        self.llm = llm

    def initialize(self) -> None:
        self.store.initialize()

    def login(self, username: str, password: str) -> Optional[dict[str, Any]]:
        return self.store.authenticate(normalize_username(username), password)

    def register_public_student(
        self,
        username: str,
        password: str,
        real_name: str,
        grade: str,
        class_name: Optional[str],
    ) -> tuple[bool, str]:
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
        created = self.store.create_user(normalize_username(username), password, "student", real_name.strip(), grade, class_name)
        return (True, "注册成功，请登录。") if created else (False, "用户名已存在。")

    def create_user_by_admin(
        self,
        username: str,
        password: str,
        role: str,
        real_name: str,
        grade: Optional[str],
        class_name: Optional[str],
    ) -> bool:
        return self.store.create_user(normalize_username(username), password, role, real_name.strip(), grade, class_name)

    def create_assignment(
        self,
        teacher_username: str,
        title: str,
        genre: str,
        prompt: str,
        grade: str,
        class_name: str,
        due_date: str,
    ) -> int:
        return self.store.create_assignment(
            {
                "title": title.strip(),
                "genre": genre,
                "prompt": prompt.strip(),
                "grade": grade,
                "class_name": class_name,
                "teacher_username": teacher_username,
                "due_date": due_date,
            }
        )

    def review_and_save_submission(
        self,
        student_username: str,
        grade: str,
        genre: str,
        title: str,
        prompt: str,
        essay_text: str,
        assignment_id: Optional[int] = None,
    ) -> tuple[int, dict[str, Any]]:
        if len(essay_text) > self.settings.max_essay_chars:
            raise ValueError(f"作文过长，最多允许 {self.settings.max_essay_chars} 个字符。")

        feedback = self.llm.essay_feedback(grade, genre, title, essay_text, user_key=student_username)
        structure = infer_structure_score(essay_text)
        expression = infer_expression_score(essay_text)
        total = int((structure + expression) / 2)
        submission_id = self.store.save_submission(
            {
                "assignment_id": assignment_id,
                "student_username": student_username,
                "title": title,
                "genre": genre,
                "prompt": prompt,
                "essay_text": essay_text,
                "word_count": chinese_word_count(essay_text),
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

    def page_size(self, requested: int | None = None) -> int:
        value = requested or self.settings.default_page_size
        return min(max(1, value), self.settings.max_page_size)

