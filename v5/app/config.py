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
    app_title: str = "校园作文辅导系统 v5"
    db_path: str = "essay_campus_system_v5.db"
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
        )

