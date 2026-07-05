import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Iterator, Optional

from .config import Settings
from .security import ALL_ROLES, hash_password, verify_password


def now_iso() -> str:
    return datetime.now().isoformat()


def row_to_dict(row: sqlite3.Row | None) -> Optional[dict[str, Any]]:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


class SQLiteStore:
    """Small repository layer.

    v5 keeps SQLite for local/demo use but isolates persistence behind this
    class so production can replace it with Postgres or Supabase without
    rewriting UI and service code.
    """

    def __init__(self, settings: Settings):
        self.settings = settings

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.settings.db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        try:
            conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.DatabaseError:
            pass
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'parent', 'admin')),
                    real_name TEXT NOT NULL,
                    grade TEXT,
                    class_name TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL UNIQUE,
                    grade TEXT NOT NULL,
                    teacher_username TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    prompt TEXT,
                    grade TEXT NOT NULL,
                    class_name TEXT,
                    teacher_username TEXT NOT NULL,
                    due_date TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER,
                    student_username TEXT NOT NULL,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    prompt TEXT,
                    essay_text TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    structure_score INTEGER NOT NULL,
                    expression_score INTEGER NOT NULL,
                    total_score INTEGER NOT NULL,
                    teacher_feedback TEXT NOT NULL,
                    student_feedback TEXT NOT NULL,
                    revised_steps TEXT NOT NULL,
                    model_feedback_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS essay_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    version_no INTEGER NOT NULL,
                    essay_text TEXT NOT NULL,
                    feedback_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(submission_id, version_no)
                );

                CREATE TABLE IF NOT EXISTS parent_student_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_username TEXT NOT NULL,
                    student_username TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(parent_username, student_username)
                );

                CREATE TABLE IF NOT EXISTS growth_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_username TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    structure_score INTEGER NOT NULL,
                    expression_score INTEGER NOT NULL,
                    total_score INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
                CREATE INDEX IF NOT EXISTS idx_users_class ON users(class_name);
                CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_username);
                CREATE INDEX IF NOT EXISTS idx_assignments_grade_class ON assignments(grade, class_name, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_student_created ON submissions(student_username, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_created ON submissions(created_at);
                CREATE INDEX IF NOT EXISTS idx_growth_student_created ON growth_records(student_username, created_at);
                CREATE INDEX IF NOT EXISTS idx_parent_links_parent ON parent_student_links(parent_username);
                """
            )
        self.seed_demo_users_if_enabled()

    def seed_demo_users_if_enabled(self) -> None:
        if not self.settings.seed_demo_users:
            return
        with self.connect() as conn:
            count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            if count:
                return
            now = now_iso()
            users = [
                ("teacher1", "teacher", "张老师", None, None),
                ("student1", "student", "小明", "三年级", "三年级一班"),
                ("student2", "student", "小红", "六年级", "六年级一班"),
                ("parent1", "parent", "家长示例", None, None),
                ("admin", "admin", "管理员", None, None),
            ]
            conn.executemany(
                """
                INSERT INTO users (username, password_hash, role, real_name, grade, class_name, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (username, hash_password(self.settings.demo_password), role, real_name, grade, class_name, now)
                    for username, role, real_name, grade, class_name in users
                ],
            )
            conn.executemany(
                "INSERT OR IGNORE INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
                [
                    ("三年级一班", "三年级", "teacher1", now),
                    ("六年级一班", "六年级", "teacher1", now),
                ],
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO parent_student_links (parent_username, student_username, created_at)
                VALUES (?, ?, ?)
                """,
                ("parent1", "student1", now),
            )

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        real_name: str,
        grade: Optional[str],
        class_name: Optional[str],
    ) -> bool:
        if role not in ALL_ROLES:
            return False
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, password_hash, role, real_name, grade, class_name, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (username, hash_password(password), role, real_name, grade, class_name, now_iso()),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            return row_to_dict(conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone())

    def authenticate(self, username: str, password: str) -> Optional[dict[str, Any]]:
        user = self.get_user(username)
        if user and verify_password(password, user["password_hash"]):
            return user
        return None

    def create_class(self, class_name: str, grade: str, teacher_username: str) -> bool:
        try:
            with self.connect() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
                    (class_name, grade, teacher_username, now_iso()),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def list_teacher_classes(self, teacher_username: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT class_name, grade FROM classes WHERE teacher_username=? ORDER BY grade, class_name",
                (teacher_username,),
            ).fetchall()
            return rows_to_dicts(rows)

    def create_assignment(self, data: dict[str, Any]) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data["genre"],
                    data.get("prompt", ""),
                    data["grade"],
                    data.get("class_name"),
                    data["teacher_username"],
                    data.get("due_date"),
                    now_iso(),
                ),
            )
            return int(cur.lastrowid)

    def list_assignments_for_student(self, grade: str, class_name: Optional[str], limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, genre, prompt, grade, class_name, due_date, created_at
                FROM assignments
                WHERE grade=? AND (class_name=? OR class_name IS NULL)
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (grade, class_name, limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

    def list_teacher_submissions(self, teacher_username: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.student_username, s.title, s.genre, s.word_count, s.total_score,
                       s.created_at, u.real_name, u.class_name
                FROM submissions s
                JOIN users u ON s.student_username = u.username
                JOIN classes c ON u.class_name = c.class_name
                WHERE c.teacher_username = ?
                ORDER BY s.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (teacher_username, limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

    def get_submission_for_teacher(self, teacher_username: str, submission_id: int) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT s.*
                FROM submissions s
                JOIN users u ON s.student_username = u.username
                JOIN classes c ON u.class_name = c.class_name
                WHERE c.teacher_username=? AND s.id=?
                """,
                (teacher_username, submission_id),
            ).fetchone()
            return row_to_dict(row)

    def save_submission(self, data: dict[str, Any]) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO submissions (
                    assignment_id, student_username, title, genre, prompt, essay_text, word_count,
                    structure_score, expression_score, total_score, teacher_feedback, student_feedback,
                    revised_steps, model_feedback_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("assignment_id"),
                    data["student_username"],
                    data["title"],
                    data["genre"],
                    data["prompt"],
                    data["essay_text"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    data["teacher_feedback"],
                    data["student_feedback"],
                    json.dumps(data["step_rewrite"], ensure_ascii=False),
                    json.dumps(data["feedback_json"], ensure_ascii=False),
                    now_iso(),
                ),
            )
            submission_id = int(cur.lastrowid)
            conn.execute(
                "INSERT INTO essay_versions (submission_id, version_no, essay_text, feedback_json, created_at) VALUES (?, ?, ?, ?, ?)",
                (submission_id, 1, data["essay_text"], json.dumps(data["feedback_json"], ensure_ascii=False), now_iso()),
            )
            conn.execute(
                "INSERT INTO growth_records (student_username, genre, word_count, structure_score, expression_score, total_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    data["student_username"],
                    data["genre"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    now_iso(),
                ),
            )
            return submission_id

    def list_student_submissions(self, student_username: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, genre, word_count, total_score, created_at
                FROM submissions
                WHERE student_username=?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (student_username, limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

    def list_versions(self, submission_id: int) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT version_no, essay_text, created_at FROM essay_versions WHERE submission_id=? ORDER BY version_no",
                (submission_id,),
            ).fetchall()
            return rows_to_dicts(rows)

    def list_growth_records(self, student_username: str, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT created_at, genre, word_count, structure_score, expression_score, total_score
                FROM growth_records
                WHERE student_username=?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (student_username, limit),
            ).fetchall()
            return rows_to_dicts(rows)

    def link_parent_to_student(self, parent_username: str, student_username: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO parent_student_links (parent_username, student_username, created_at)
                VALUES (?, ?, ?)
                """,
                (parent_username, student_username, now_iso()),
            )

    def list_parent_students(self, parent_username: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT u.username, u.real_name, u.grade, u.class_name
                FROM parent_student_links l
                JOIN users u ON l.student_username = u.username
                WHERE l.parent_username=? AND u.role='student'
                ORDER BY u.grade, u.class_name, u.real_name
                """,
                (parent_username,),
            ).fetchall()
            return rows_to_dicts(rows)

    def parent_can_view_student(self, parent_username: str, student_username: str) -> bool:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM parent_student_links WHERE parent_username=? AND student_username=? LIMIT 1",
                (parent_username, student_username),
            ).fetchone()
            return row is not None

    def latest_submission_for_parent(self, parent_username: str, student_username: str) -> Optional[dict[str, Any]]:
        if not self.parent_can_view_student(parent_username, student_username):
            return None
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM submissions WHERE student_username=? ORDER BY created_at DESC LIMIT 1",
                (student_username,),
            ).fetchone()
            return row_to_dict(row)

    def list_users(self, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT username, real_name, role, grade, class_name, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

