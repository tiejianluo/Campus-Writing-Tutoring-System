import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from typing import Any, Iterator, Optional

from .config import Settings
from .security import ALL_ROLES, hash_password, verify_password


def now_iso() -> str:
    return datetime.now().isoformat()


def today_str() -> str:
    return date.today().isoformat()


def new_invite_code() -> str:
    return secrets.token_hex(3).upper()


def new_order_no() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(3).upper()


def row_to_dict(row: sqlite3.Row | None) -> Optional[dict[str, Any]]:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


class SQLiteStore:
    """Small repository layer.

    v6 keeps SQLite for local/demo use but isolates persistence behind this
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
                    invite_code TEXT UNIQUE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    subject TEXT NOT NULL DEFAULT 'chinese',
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
                    subject TEXT NOT NULL DEFAULT 'chinese',
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
                    word_count INTEGER NOT NULL DEFAULT 0,
                    total_score INTEGER NOT NULL DEFAULT 0,
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
                    subject TEXT NOT NULL DEFAULT 'chinese',
                    topic TEXT NOT NULL DEFAULT '',
                    word_count INTEGER NOT NULL,
                    structure_score INTEGER NOT NULL,
                    expression_score INTEGER NOT NULL,
                    total_score INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    plan TEXT NOT NULL CHECK(plan IN ('month', 'year', 'trial')),
                    started_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    plan TEXT NOT NULL CHECK(plan IN ('month', 'year')),
                    amount INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'paid', 'cancelled')),
                    created_at TEXT NOT NULL,
                    paid_at TEXT
                );

                CREATE TABLE IF NOT EXISTS activation_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    plan TEXT NOT NULL CHECK(plan IN ('month', 'year')),
                    created_by TEXT NOT NULL,
                    used_by TEXT,
                    used_at TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS ai_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(username, usage_date)
                );

                CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
                CREATE INDEX IF NOT EXISTS idx_users_class ON users(class_name);
                CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_username);
                CREATE INDEX IF NOT EXISTS idx_assignments_grade_class ON assignments(grade, class_name, created_at);
                CREATE INDEX IF NOT EXISTS idx_assignments_teacher ON assignments(teacher_username, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_student_created ON submissions(student_username, created_at);
                CREATE INDEX IF NOT EXISTS idx_submissions_created ON submissions(created_at);
                CREATE INDEX IF NOT EXISTS idx_growth_student_created ON growth_records(student_username, created_at);
                CREATE INDEX IF NOT EXISTS idx_parent_links_parent ON parent_student_links(parent_username);
                CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(username, expires_at);
                CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status, created_at);
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
                """
                INSERT OR IGNORE INTO classes (class_name, grade, teacher_username, invite_code, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("三年级一班", "三年级", "teacher1", new_invite_code(), now),
                    ("六年级一班", "六年级", "teacher1", new_invite_code(), now),
                ],
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO parent_student_links (parent_username, student_username, created_at)
                VALUES (?, ?, ?)
                """,
                ("parent1", "student1", now),
            )

    # ------------------------------------------------------------------
    # Users / auth
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Classes / invite codes
    # ------------------------------------------------------------------
    def create_class(self, class_name: str, grade: str, teacher_username: str) -> Optional[str]:
        """Create a class and return its invite code, or None if the name is taken."""
        code = new_invite_code()
        try:
            with self.connect() as conn:
                conn.execute(
                    """
                    INSERT INTO classes (class_name, grade, teacher_username, invite_code, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (class_name, grade, teacher_username, code, now_iso()),
                )
            return code
        except sqlite3.IntegrityError:
            return None

    def get_class_by_invite_code(self, invite_code: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT class_name, grade, teacher_username, invite_code FROM classes WHERE invite_code=?",
                (invite_code.strip().upper(),),
            ).fetchone()
            return row_to_dict(row)

    def get_class(self, class_name: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM classes WHERE class_name=?", (class_name,)).fetchone()
            return row_to_dict(row)

    def list_teacher_classes(self, teacher_username: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT class_name, grade, invite_code FROM classes WHERE teacher_username=? ORDER BY grade, class_name",
                (teacher_username,),
            ).fetchall()
            return rows_to_dicts(rows)

    # ------------------------------------------------------------------
    # Assignments
    # ------------------------------------------------------------------
    def create_assignment(self, data: dict[str, Any]) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO assignments (title, genre, subject, prompt, grade, class_name, teacher_username, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["title"],
                    data["genre"],
                    data.get("subject", "chinese"),
                    data.get("prompt", ""),
                    data["grade"],
                    data.get("class_name"),
                    data["teacher_username"],
                    data.get("due_date"),
                    now_iso(),
                ),
            )
            return int(cur.lastrowid)

    def list_assignments_for_student(
        self, grade: str, class_name: Optional[str], limit: int, offset: int = 0
    ) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, genre, subject, prompt, grade, class_name, due_date, created_at
                FROM assignments
                WHERE grade=? AND (class_name IS NULL OR class_name=?)
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (grade, class_name, limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

    def list_teacher_assignments(self, teacher_username: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, genre, subject, prompt, grade, class_name, due_date, created_at
                FROM assignments
                WHERE teacher_username=?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (teacher_username, limit, offset),
            ).fetchall()
            return rows_to_dicts(rows)

    # ------------------------------------------------------------------
    # Submissions / versions
    # ------------------------------------------------------------------
    def list_teacher_submissions(self, teacher_username: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT s.id, s.student_username, s.title, s.genre, s.subject, s.word_count, s.total_score,
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

    def get_submission_for_student(self, student_username: str, submission_id: int) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM submissions WHERE id=? AND student_username=?",
                (submission_id, student_username),
            ).fetchone()
            return row_to_dict(row)

    def save_submission(self, data: dict[str, Any]) -> int:
        feedback_json = json.dumps(data["feedback_json"], ensure_ascii=False)
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO submissions (
                    assignment_id, student_username, title, genre, subject, prompt, essay_text, word_count,
                    structure_score, expression_score, total_score, teacher_feedback, student_feedback,
                    revised_steps, model_feedback_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("assignment_id"),
                    data["student_username"],
                    data["title"],
                    data["genre"],
                    data.get("subject", "chinese"),
                    data["prompt"],
                    data["essay_text"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    data["teacher_feedback"],
                    data["student_feedback"],
                    json.dumps(data["step_rewrite"], ensure_ascii=False),
                    feedback_json,
                    now_iso(),
                ),
            )
            submission_id = int(cur.lastrowid)
            conn.execute(
                """
                INSERT INTO essay_versions (submission_id, version_no, essay_text, word_count, total_score, feedback_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (submission_id, 1, data["essay_text"], data["word_count"], data["total_score"], feedback_json, now_iso()),
            )
            conn.execute(
                """
                INSERT INTO growth_records (student_username, genre, subject, topic, word_count, structure_score, expression_score, total_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["student_username"],
                    data["genre"],
                    data.get("subject", "chinese"),
                    data["title"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    now_iso(),
                ),
            )
            return submission_id

    def add_version(self, submission_id: int, data: dict[str, Any]) -> int:
        """Append a new version to an existing submission and refresh its latest state.

        Unlike deployed-B, a rewrite never creates a second submission row, so
        version counting and comparison stay consistent.
        """
        feedback_json = json.dumps(data["feedback_json"], ensure_ascii=False)
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(version_no), 0) AS m FROM essay_versions WHERE submission_id=?",
                (submission_id,),
            ).fetchone()
            next_no = int(row["m"]) + 1
            conn.execute(
                """
                INSERT INTO essay_versions (submission_id, version_no, essay_text, word_count, total_score, feedback_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    next_no,
                    data["essay_text"],
                    data["word_count"],
                    data["total_score"],
                    feedback_json,
                    now_iso(),
                ),
            )
            conn.execute(
                """
                UPDATE submissions
                SET essay_text=?, word_count=?, structure_score=?, expression_score=?, total_score=?,
                    teacher_feedback=?, student_feedback=?, revised_steps=?, model_feedback_json=?
                WHERE id=?
                """,
                (
                    data["essay_text"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    data["teacher_feedback"],
                    data["student_feedback"],
                    json.dumps(data["step_rewrite"], ensure_ascii=False),
                    feedback_json,
                    submission_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO growth_records (student_username, genre, subject, topic, word_count, structure_score, expression_score, total_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["student_username"],
                    data["genre"],
                    data.get("subject", "chinese"),
                    data["title"],
                    data["word_count"],
                    data["structure_score"],
                    data["expression_score"],
                    data["total_score"],
                    now_iso(),
                ),
            )
            return next_no

    def list_student_submissions(self, student_username: str, limit: int, offset: int = 0) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, genre, subject, word_count, total_score, created_at
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
                """
                SELECT version_no, essay_text, word_count, total_score, feedback_json, created_at
                FROM essay_versions
                WHERE submission_id=?
                ORDER BY version_no
                """,
                (submission_id,),
            ).fetchall()
            return rows_to_dicts(rows)

    def list_growth_records(self, student_username: str, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT created_at, subject, genre, topic, word_count, structure_score, expression_score, total_score
                FROM growth_records
                WHERE student_username=?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (student_username, limit),
            ).fetchall()
            return rows_to_dicts(rows)

    # ------------------------------------------------------------------
    # Parent links
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Subscriptions / orders / activation codes / AI quota
    # ------------------------------------------------------------------
    def get_active_subscription(self, username: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM subscriptions
                WHERE username=? AND status='active' AND expires_at > ?
                ORDER BY expires_at DESC LIMIT 1
                """,
                (username, now_iso()),
            ).fetchone()
            return row_to_dict(row)

    def create_subscription(self, username: str, plan: str, days: int) -> dict[str, Any]:
        """Create or extend a subscription; extension starts from current expiry."""
        current = self.get_active_subscription(username)
        start = datetime.now()
        if current:
            start = max(start, datetime.fromisoformat(current["expires_at"]))
        expires = start + timedelta(days=days)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions (username, plan, started_at, expires_at, status, created_at)
                VALUES (?, ?, ?, ?, 'active', ?)
                """,
                (username, plan, start.isoformat(), expires.isoformat(), now_iso()),
            )
        return {"username": username, "plan": plan, "expires_at": expires.isoformat()}

    def create_order(self, username: str, plan: str, amount: int) -> dict[str, Any]:
        order_no = new_order_no()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO orders (order_no, username, plan, amount, status, created_at)
                VALUES (?, ?, ?, ?, 'pending', ?)
                """,
                (order_no, username, plan, amount, now_iso()),
            )
        return {"order_no": order_no, "username": username, "plan": plan, "amount": amount, "status": "pending"}

    def get_order(self, order_no: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_no=?", (order_no,)).fetchone()
            return row_to_dict(row)

    def list_pending_orders(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM orders WHERE status='pending' ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return rows_to_dicts(rows)

    def mark_order_paid(self, order_no: str) -> Optional[dict[str, Any]]:
        with self.connect() as conn:
            cur = conn.execute(
                "UPDATE orders SET status='paid', paid_at=? WHERE order_no=? AND status='pending'",
                (now_iso(), order_no),
            )
            if cur.rowcount == 0:
                return None
        return self.get_order(order_no)

    def create_activation_code(self, plan: str, created_by: str) -> str:
        code = secrets.token_hex(6).upper()
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO activation_codes (code, plan, created_by, created_at) VALUES (?, ?, ?, ?)",
                (code, plan, created_by, now_iso()),
            )
        return code

    def redeem_activation_code(self, code: str, username: str) -> Optional[str]:
        """Mark a code used and return its plan, or None if invalid/used."""
        with self.connect() as conn:
            cur = conn.execute(
                "UPDATE activation_codes SET used_by=?, used_at=? WHERE code=? AND used_by IS NULL",
                (username, now_iso(), code.strip().upper()),
            )
            if cur.rowcount == 0:
                return None
            row = conn.execute("SELECT plan FROM activation_codes WHERE code=?", (code.strip().upper(),)).fetchone()
            return row["plan"] if row else None

    def get_ai_usage_today(self, username: str) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT count FROM ai_usage WHERE username=? AND usage_date=?",
                (username, today_str()),
            ).fetchone()
            return int(row["count"]) if row else 0

    def increment_ai_usage(self, username: str) -> int:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO ai_usage (username, usage_date, count) VALUES (?, ?, 1)
                ON CONFLICT(username, usage_date) DO UPDATE SET count = count + 1
                """,
                (username, today_str()),
            )
            row = conn.execute(
                "SELECT count FROM ai_usage WHERE username=? AND usage_date=?",
                (username, today_str()),
            ).fetchone()
            return int(row["count"])
