import hashlib
import hmac
import re
import secrets
from typing import Optional

try:
    import bcrypt  # type: ignore
except Exception:
    bcrypt = None

ALLOWED_PUBLIC_REGISTER_ROLES = {"student"}
ADMIN_CREATED_ROLES = {"teacher", "parent", "admin"}
ALL_ROLES = ALLOWED_PUBLIC_REGISTER_ROLES | ADMIN_CREATED_ROLES
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")


def hash_password(password: str) -> str:
    if bcrypt:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    iterations = 260_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    if bcrypt and hashed.startswith("$2"):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False
    if hashed.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt, expected = hashed.split("$", 3)
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations))
            return hmac.compare_digest(digest.hex(), expected)
        except Exception:
            return False
    legacy_sha256 = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_sha256, hashed)


def normalize_username(username: str) -> str:
    return username.strip()


def password_is_strong_enough(password: str, min_length: int) -> bool:
    return bool(password) and len(password) >= min_length


def validate_username_password(username: str, password: str, min_password_length: int) -> tuple[bool, str]:
    """Shared checks for any account creation path, including admin-created ones."""
    username = normalize_username(username)
    if not username or not USERNAME_RE.fullmatch(username):
        return False, "用户名需为 3-32 位字母、数字或下划线。"
    if not password_is_strong_enough(password, min_password_length):
        return False, f"密码至少需要 {min_password_length} 位。"
    return True, ""


def validate_public_registration(
    username: str,
    password: str,
    role: str,
    real_name: str,
    grade: Optional[str],
    valid_grades: set[str],
    min_password_length: int,
) -> tuple[bool, str]:
    username = normalize_username(username)
    if role not in ALLOWED_PUBLIC_REGISTER_ROLES:
        return False, "公开注册只允许学生账号。"
    if not username or not USERNAME_RE.fullmatch(username):
        return False, "用户名需为 3-32 位字母、数字或下划线。"
    if not password_is_strong_enough(password, min_password_length):
        return False, f"密码至少需要 {min_password_length} 位。"
    if not real_name.strip():
        return False, "姓名不能为空。"
    if grade not in valid_grades:
        return False, "学生账号必须选择有效年级。"
    return True, ""

