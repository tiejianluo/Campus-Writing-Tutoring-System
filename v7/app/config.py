import os
from dataclasses import dataclass
from typing import Optional


def get_config_value(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read deployment config from env first, then Streamlit secrets."""
    env_value = os.getenv(name)
    if env_value not in (None, ""):
        return env_value
    try:
        import streamlit as st

        secret_value = st.secrets.get(name)
    except Exception:
        return default
    return secret_value or default


def get_config_bool(name: str, default: bool = False) -> bool:
    value = get_config_value(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_title: str = "写作陪练"
    db_path: str = "essay_campus_system_v7.db"
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-2025-04-14"
    seed_demo_users: bool = False
    demo_password: str = "change-me-before-demo"
    min_password_length: int = 8
    max_text_upload_bytes: int = 64 * 1024
    max_image_upload_bytes: int = 5 * 1024 * 1024
    max_image_pixels: int = 4_000_000
    max_model_image_side: int = 1024
    max_essay_chars: int = 6000
    default_page_size: int = 50
    max_page_size: int = 200
    llm_requests_per_minute: int = 12
    login_attempts_per_minute: int = 10
    # Freemium / subscription
    premium_price_month: int = 26
    premium_price_year: int = 288
    free_ai_daily_quota: int = 3
    premium_trial_days: int = 7
    payment_qr_month_url: Optional[str] = None
    payment_qr_year_url: Optional[str] = None
    # Bootstrap admin：设置这两个变量后，启动时若该管理员不存在则自动创建
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=get_config_value("ESSAY_APP_DB", cls.db_path) or cls.db_path,
            openai_api_key=get_config_value("OPENAI_API_KEY"),
            openai_base_url=get_config_value("OPENAI_BASE_URL", cls.openai_base_url) or cls.openai_base_url,
            openai_model=get_config_value("OPENAI_MODEL", cls.openai_model) or cls.openai_model,
            seed_demo_users=get_config_bool("ESSAY_APP_SEED_DEMO_USERS", cls.seed_demo_users),
            demo_password=get_config_value("ESSAY_APP_DEMO_PASSWORD", cls.demo_password) or cls.demo_password,
            min_password_length=int(get_config_value("MIN_PASSWORD_LENGTH", str(cls.min_password_length))),
            max_text_upload_bytes=int(get_config_value("MAX_TEXT_UPLOAD_BYTES", str(cls.max_text_upload_bytes))),
            max_image_upload_bytes=int(get_config_value("MAX_IMAGE_UPLOAD_BYTES", str(cls.max_image_upload_bytes))),
            max_image_pixels=int(get_config_value("MAX_IMAGE_PIXELS", str(cls.max_image_pixels))),
            max_model_image_side=int(get_config_value("MAX_MODEL_IMAGE_SIDE", str(cls.max_model_image_side))),
            max_essay_chars=int(get_config_value("MAX_ESSAY_CHARS", str(cls.max_essay_chars))),
            default_page_size=int(get_config_value("DEFAULT_PAGE_SIZE", str(cls.default_page_size))),
            max_page_size=int(get_config_value("MAX_PAGE_SIZE", str(cls.max_page_size))),
            llm_requests_per_minute=int(get_config_value("LLM_REQUESTS_PER_MINUTE", str(cls.llm_requests_per_minute))),
            login_attempts_per_minute=int(
                get_config_value("LOGIN_ATTEMPTS_PER_MINUTE", str(cls.login_attempts_per_minute))
            ),
            premium_price_month=int(get_config_value("PREMIUM_PRICE_MONTH", str(cls.premium_price_month))),
            premium_price_year=int(get_config_value("PREMIUM_PRICE_YEAR", str(cls.premium_price_year))),
            free_ai_daily_quota=int(get_config_value("FREE_AI_DAILY_QUOTA", str(cls.free_ai_daily_quota))),
            premium_trial_days=int(get_config_value("PREMIUM_TRIAL_DAYS", str(cls.premium_trial_days))),
            payment_qr_month_url=get_config_value("PAYMENT_QR_MONTH_URL"),
            payment_qr_year_url=get_config_value("PAYMENT_QR_YEAR_URL"),
            admin_username=get_config_value("ESSAY_APP_ADMIN_USER"),
            admin_password=get_config_value("ESSAY_APP_ADMIN_PASSWORD"),
        )
