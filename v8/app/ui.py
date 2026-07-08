import json

import pandas as pd
import streamlit as st

from .config import Settings
from .content import ESSAY_TEMPLATES, GRADE_RUBRICS
from .content_en import ENGLISH_TEMPLATES, english_genres_for_grade
from .i18n import DEFAULT_LANG, LANG_LABELS, LANGS, tr
from .llm import (
    FALLBACK_API_ERROR,
    FALLBACK_NO_API_KEY,
    FALLBACK_QUOTA,
    FALLBACK_RATE_LIMITED,
    SUBJECT_CHINESE,
    SUBJECT_ENGLISH,
    LLMService,
)
from .metrics import compare_with_model_essay, generate_topics, grade_expectation
from .metrics_en import generate_topics_en, grade_expectation_en
from .responsive import inject_responsive_styles, render_records
from .services import AppService
from .storage import SQLiteStore
from .uploads import UploadValidationError, load_uploaded_image, read_uploaded_text

# 点评回退原因 → 界面文案 key（show_feedback 用）
FALLBACK_TEXT_KEYS = {
    FALLBACK_QUOTA: "fb_quota",
    FALLBACK_NO_API_KEY: "fb_no_api_key",
    FALLBACK_RATE_LIMITED: "fb_rate_limited",
    FALLBACK_API_ERROR: "fb_api_error",
}

# 手写识别失败原因 → 界面文案 key（手写作文页用）
OCR_TEXT_KEYS = {
    FALLBACK_NO_API_KEY: "ocr_no_api_key",
    FALLBACK_QUOTA: "ocr_quota",
    FALLBACK_RATE_LIMITED: "ocr_rate_limited",
    FALLBACK_API_ERROR: "ocr_api_error",
}

# 学生端菜单：key 固定（切换语言不丢状态），显示文字随语言变化
STUDENT_MENU_KEYS = (
    "menu_write",
    "menu_handwriting",
    "menu_picture",
    "menu_rewrite",
    "menu_versions",
    "menu_growth",
    "menu_membership",
)


def ui_lang() -> str:
    return st.session_state.get("ui_lang", DEFAULT_LANG)


def L(key: str, **kwargs) -> str:
    """当前界面语言的文案。"""
    return tr(key, ui_lang(), **kwargs)


def subject_options() -> dict:
    return {L("subject_chinese"): SUBJECT_CHINESE, L("subject_english"): SUBJECT_ENGLISH}


def subject_short(subject: str) -> str:
    return L("subject_short_en") if subject == SUBJECT_ENGLISH else L("subject_short_cn")


@st.cache_resource
def build_service() -> AppService:
    settings = Settings.from_env()
    store = SQLiteStore(settings)
    service = AppService(settings, store, LLMService(settings))
    service.initialize()
    return service


def dataframe(rows: list[dict]) -> None:
    render_records(rows, empty_message=L("no_data"))


def require_premium(service: AppService, user: dict, feature_label: str) -> bool:
    if service.is_premium(user["username"]):
        return True
    st.warning(
        L(
            "premium_required",
            feature=feature_label,
            month=service.settings.premium_price_month,
            year=service.settings.premium_price_year,
        )
    )
    return False


def language_switcher() -> None:
    st.sidebar.radio(
        L("language_label"),
        LANGS,
        format_func=lambda code: LANG_LABELS.get(code, code),
        horizontal=True,
        key="ui_lang",
    )


def auth_sidebar(service: AppService):
    language_switcher()
    st.sidebar.title(L("account_system"))
    st.session_state.setdefault("user", None)
    user = st.session_state.user
    if user:
        parts = [user["real_name"], f"（{user['role']}）" if ui_lang() == "zh" else f" ({user['role']})"]
        if user.get("grade"):
            parts.append(f" {user['grade']}")
        if user.get("class_name"):
            parts.append(f" {user['class_name']}")
        st.sidebar.success(L("logged_in", who="".join(parts)))
        status = service.premium_status(user["username"])
        if status:
            st.sidebar.info(L("member_until", date=status["expires_at"][:10]))
        else:
            quota = service.ai_quota_left(user["username"])
            st.sidebar.caption(L("quota_left", n=quota))
        if st.sidebar.button(L("logout")):
            st.session_state.user = None
            st.rerun()
        return

    login_tab, register_tab = st.sidebar.tabs([L("tab_login"), L("tab_register")])
    with login_tab:
        username = st.text_input(L("username"), key="login_user")
        password = st.text_input(L("password"), type="password", key="login_pwd")
        if st.button(L("login_btn")):
            logged_in = service.login(username, password)
            if logged_in:
                st.session_state.user = logged_in
                st.rerun()
            st.error(L("login_failed"))
    with register_tab:
        username = st.text_input(L("new_username"), key="reg_user")
        real_name = st.text_input(L("real_name"), key="reg_name")
        grade = st.selectbox(L("grade"), list(GRADE_RUBRICS), key="reg_grade")
        invite_code = st.text_input(L("invite_code_opt"), key="reg_invite")
        password = st.text_input(L("set_password"), type="password", key="reg_pwd")
        if st.button(L("register_btn")):
            ok, message = service.register_public_student(username, password, real_name, grade, invite_code or None)
            if ok:
                st.success(message + L("trial_bonus", days=service.settings.premium_trial_days))
            else:
                st.error(message)


# ----------------------------------------------------------------------
# Teacher
# ----------------------------------------------------------------------
def teacher_view(service: AppService, user: dict):
    st.header(L("teacher_home"))
    assign_tab, submissions_tab, class_tab = st.tabs(
        [L("tab_assign"), L("tab_class_submissions"), L("tab_class_manage")]
    )
    classes = service.store.list_teacher_classes(user["username"])

    with assign_tab:
        if not classes:
            st.info(L("create_class_first"))
        else:
            class_options = [c["class_name"] for c in classes]
            class_name = st.selectbox(L("select_class"), class_options, key="assign_class")
            grade = next((c["grade"] for c in classes if c["class_name"] == class_name), "三年级")
            labels = subject_options()
            subject_label = st.radio(L("subject_label"), list(labels), horizontal=True, key="assign_subject")
            subject = labels[subject_label]
            genres = list(ESSAY_TEMPLATES) if subject == SUBJECT_CHINESE else english_genres_for_grade(grade)
            genre = st.selectbox(L("essay_genre"), genres, key="assign_genre")
            title = st.text_input(L("essay_title_input"))
            prompt = st.text_area(L("assignment_prompt"))
            due_date = st.date_input(L("due_date"))
            if st.button(L("publish_btn")) and title.strip():
                try:
                    service.create_assignment(
                        user["username"], title, genre, prompt, grade, class_name, str(due_date), subject
                    )
                    st.success(L("publish_ok"))
                except PermissionError as exc:
                    st.error(str(exc))

        st.markdown(f"#### {L('published_history')}")
        history = service.store.list_teacher_assignments(user["username"], limit=service.page_size())
        if history:
            dataframe(
                [
                    {
                        L("col_id"): r["id"],
                        L("col_title"): r["title"],
                        L("col_subject"): subject_short(r["subject"]),
                        L("col_genre"): r["genre"],
                        L("col_class"): r["class_name"],
                        L("col_due"): r["due_date"],
                        L("col_prompt"): r["prompt"],
                    }
                    for r in history
                ]
            )
        else:
            st.caption(L("no_published_yet"))

    with submissions_tab:
        page = st.number_input(L("page_number"), min_value=1, value=1, step=1)
        size = service.page_size()
        rows = service.store.list_teacher_submissions(user["username"], limit=size, offset=(page - 1) * size)
        dataframe(rows)
        if rows:
            sid = st.selectbox(L("view_submission"), [r["id"] for r in rows])
            detail = service.store.get_submission_for_teacher(user["username"], int(sid))
            if detail:
                st.subheader(detail["title"])
                st.write(detail["essay_text"])
                st.markdown(f"**{L('teacher_feedback_hdr')}**")
                st.write(detail["teacher_feedback"])

    with class_tab:
        grade = st.selectbox(L("grade"), list(GRADE_RUBRICS), key="class_grade")
        class_name = st.text_input(L("new_class_name"))
        if st.button(L("add_class_btn")) and class_name.strip():
            ok, result = service.create_class(user["username"], class_name, grade)
            if ok:
                st.success(L("class_created", code=result))
            else:
                st.error(result)
        dataframe(service.store.list_teacher_classes(user["username"]))


# ----------------------------------------------------------------------
# Student
# ----------------------------------------------------------------------
def student_view(service: AppService, user: dict):
    st.header(L("student_home"))
    menu = st.radio(
        L("choose_feature"),
        STUDENT_MENU_KEYS,
        format_func=lambda key: L(key),
        horizontal=True,
        key="student_menu",
    )
    grade = user.get("grade") or "三年级"

    if menu == "menu_write":
        _writing_page(service, user, grade)
    elif menu == "menu_handwriting":
        _handwriting_page(service, user, grade)
    elif menu == "menu_picture":
        _image_page(service, user, grade)
    elif menu == "menu_rewrite":
        _rewrite_page(service, user)
    elif menu == "menu_versions":
        _version_page(service, user)
    elif menu == "menu_growth":
        _growth_page(service, user)
    elif menu == "menu_membership":
        membership_page(service, user)


def _assignment_expander(service: AppService, user: dict, grade: str) -> None:
    rows = service.store.list_assignments_for_student(grade, user.get("class_name"), limit=service.page_size())
    with st.expander(L("assignments_expander"), expanded=True):
        if not rows:
            st.info(L("no_assignments"))
        for r in rows:
            st.markdown(
                L(
                    "assignment_line",
                    subject=subject_short(r["subject"]),
                    title=r["title"],
                    genre=r["genre"],
                    due=r["due_date"],
                )
            )
            if r.get("prompt"):
                st.caption(L("assignment_requirement", prompt=r["prompt"]))


def _subject_topic_controls(grade: str, key_prefix: str) -> tuple[str, str, str, dict]:
    """科目 + 类型 + 题目选择控件，写作页与手写页共用。"""
    labels = subject_options()
    subject_label = st.radio(L("subject_label"), list(labels), horizontal=True, key=f"{key_prefix}_subject")
    subject = labels[subject_label]
    if subject == SUBJECT_CHINESE:
        genre = st.selectbox(L("essay_genre"), list(ESSAY_TEMPLATES), key=f"{key_prefix}_genre")
        topic = st.selectbox(L("topic_label"), generate_topics(grade, genre), key=f"{key_prefix}_topic")
        st.caption(grade_expectation(grade))
        tpl = ESSAY_TEMPLATES[genre]
    else:
        genres = english_genres_for_grade(grade)
        genre = st.selectbox(L("genre_label_en_subject"), genres, key=f"{key_prefix}_genre")
        topic = st.selectbox(L("topic_label_en_subject"), generate_topics_en(grade, genre), key=f"{key_prefix}_topic")
        st.caption(grade_expectation_en(grade))
        tpl = ENGLISH_TEMPLATES[genre]
    return subject, genre, topic, tpl


def _writing_page(service: AppService, user: dict, grade: str):
    _assignment_expander(service, user, grade)
    subject, genre, topic, tpl = _subject_topic_controls(grade, "write")

    title = st.text_input(L("custom_title_opt")) or topic
    with st.expander(L("writing_guide")):
        st.markdown(f"**{L('recommended_structure')}**")
        for x in tpl["结构"]:
            st.markdown(f"- {x}")
        st.markdown(f"**{L('ref_opening')}**：{tpl['万能开头']}")
        st.markdown(f"**{L('ref_ending')}**：{tpl['万能结尾']}")
        for pattern in tpl.get("常用句型", []):
            st.markdown(f"- {L('common_pattern')}：`{pattern}`")

    essay = st.text_area(L("essay_area"), height=280)
    uploaded_txt = st.file_uploader(L("upload_txt"), type=["txt"])
    if uploaded_txt:
        try:
            essay = read_uploaded_text(uploaded_txt, service.settings)
            st.text_area(L("draft_loaded"), essay, height=180)
        except UploadValidationError as exc:
            st.error(str(exc))
    if st.button(L("review_save_btn")):
        if not essay.strip():
            st.warning(L("need_content"))
            return
        try:
            sid, feedback = service.review_and_save_submission(
                user["username"], grade, genre, title, title, essay, subject=subject
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        show_feedback(title, genre, essay, feedback, subject)
        st.success(L("saved_ok", sid=sid))


def _handwriting_page(service: AppService, user: dict, grade: str):
    """v8 新增：上传手写作文照片 → 提取文字 → 点评并保存。"""
    st.subheader(L("handwriting_title"))
    st.caption(L("handwriting_intro"))

    image_file = st.file_uploader(L("handwriting_upload"), type=["png", "jpg", "jpeg"], key="hw_upload")
    if image_file:
        try:
            image = load_uploaded_image(image_file, service.settings)
        except UploadValidationError as exc:
            st.error(str(exc))
            return
        st.image(image, caption=L("handwriting_image_caption"), use_container_width=True)
        if st.button(L("handwriting_extract_btn"), type="primary"):
            with st.spinner(L("handwriting_extracting")):
                result = service.ocr_extract_essay(user["username"], image)
            if result.get("ok"):
                text = result.get("text", "")
                if text:
                    st.session_state["hw_text"] = text
                    st.success(L("handwriting_ok", n=len(text)))
                else:
                    st.warning(L("handwriting_empty"))
            else:
                key = OCR_TEXT_KEYS.get(result.get("reason"), "ocr_api_error")
                st.error(L(key))
                st.caption(L("handwriting_manual_hint"))

    subject, genre, topic, _tpl = _subject_topic_controls(grade, "hw")
    title = st.text_input(L("custom_title_opt"), key="hw_title") or topic
    essay = st.text_area(
        L("handwriting_extracted"),
        value=st.session_state.get("hw_text", ""),
        height=280,
        key="hw_text_edit",
    )
    if st.button(L("review_save_btn"), key="hw_review"):
        if not essay.strip():
            st.warning(L("need_content"))
            return
        try:
            sid, feedback = service.review_and_save_submission(
                user["username"], grade, genre, title, title, essay, subject=subject
            )
        except ValueError as exc:
            st.error(str(exc))
            return
        show_feedback(title, genre, essay, feedback, subject)
        st.success(L("saved_ok", sid=sid))


def _image_page(service: AppService, user: dict, grade: str):
    if not require_premium(service, user, L("picture_feature")):
        return
    image_file = st.file_uploader(L("upload_image"), type=["png", "jpg", "jpeg"])
    if image_file:
        try:
            image = load_uploaded_image(image_file, service.settings)
        except UploadValidationError as exc:
            st.error(str(exc))
            return
        st.image(image, caption=L("uploaded_image"), use_container_width=True)
        if st.button(L("gen_observation_btn")):
            obs = service.llm.image_prompts(image, grade, user_key=user["username"])
            st.subheader(L("scene_summary"))
            st.write(obs.get("scene", ""))
            st.subheader(L("observation_hints"))
            for item in obs.get("observe", []):
                st.markdown(f"- {item}")
            st.subheader(L("inspiring_questions"))
            for item in obs.get("questions", []):
                st.markdown(f"- {item}")
            if obs.get("source") == "fallback":
                key = FALLBACK_TEXT_KEYS.get(obs.get("fallback_reason"))
                st.warning(L(key) if key else L("basic_prompts_notice"))


def _rewrite_page(service: AppService, user: dict):
    st.subheader(L("rewrite_title"))
    if not require_premium(service, user, L("rewrite_feature")):
        return
    submissions = service.store.list_student_submissions(user["username"], limit=service.page_size())
    if not submissions:
        st.info(L("no_essays_yet"))
        return
    options = {
        L(
            "essay_option",
            id=r["id"],
            title=r["title"],
            genre=r["genre"],
            date=r["created_at"][:10],
            score=r["total_score"],
        ): r["id"]
        for r in submissions
    }
    label = st.selectbox(L("select_essay_rewrite"), list(options))
    submission_id = options[label]
    original = service.store.get_submission_for_student(user["username"], submission_id)
    if not original:
        st.error(L("cannot_load_essay"))
        return

    versions = service.store.list_versions(submission_id)
    st.caption(L("versions_so_far", n=len(versions)))
    st.markdown(f"#### {L('original_latest')}")
    st.text_area(L("original_text"), original["essay_text"], height=160, disabled=True)

    st.markdown(f"#### {L('rewrite_guide')}")
    try:
        steps = json.loads(original["revised_steps"])
    except Exception:
        steps = {}
    if isinstance(steps, dict) and steps:
        for key, value in steps.items():
            st.info(f"**{key}**：{value}")
    else:
        st.caption(L("no_rewrite_guide"))

    rewritten = st.text_area(L("rewritten_area"), height=280, placeholder=L("rewrite_placeholder"))
    if st.button(L("submit_version_btn"), type="primary"):
        if not rewritten.strip():
            st.warning(L("fill_rewrite_first"))
            return
        try:
            version_no, feedback = service.rewrite_submission(user["username"], submission_id, rewritten)
        except (PermissionError, ValueError) as exc:
            st.error(str(exc))
            return
        st.success(L("version_saved", n=version_no))
        show_feedback(original["title"], original["genre"], rewritten, feedback, original.get("subject", SUBJECT_CHINESE))


def _version_page(service: AppService, user: dict):
    st.subheader(L("versions_title"))
    if not require_premium(service, user, L("versions_feature")):
        return
    submissions = service.store.list_student_submissions(user["username"], limit=service.page_size())
    if not submissions:
        st.info(L("no_records_yet"))
        return
    options = {
        L("essay_option_short", id=r["id"], title=r["title"], date=r["created_at"][:10]): r["id"]
        for r in submissions
    }
    label = st.selectbox(L("select_essay"), list(options))
    versions = service.store.list_versions(options[label])
    if len(versions) < 2:
        st.info(L("only_one_version"))
        return
    numbers = [v["version_no"] for v in versions]
    col_a, col_b = st.columns(2)
    with col_a:
        va = st.selectbox(L("version_a"), numbers, index=0)
    with col_b:
        vb = st.selectbox(L("version_b"), numbers, index=len(numbers) - 1)
    version_a = next(v for v in versions if v["version_no"] == va)
    version_b = next(v for v in versions if v["version_no"] == vb)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(L("version_stat", no=va, wc=version_a["word_count"], score=version_a["total_score"]))
        st.text_area(L("version_a"), version_a["essay_text"], height=240, disabled=True, key="va_text")
    with c2:
        st.markdown(L("version_stat", no=vb, wc=version_b["word_count"], score=version_b["total_score"]))
        st.text_area(L("version_b"), version_b["essay_text"], height=240, disabled=True, key="vb_text")
    st.metric(L("word_delta"), f"{version_b['word_count'] - version_a['word_count']:+d}")
    st.metric(L("score_delta"), f"{version_b['total_score'] - version_a['total_score']:+d}")


def _growth_page(service: AppService, user: dict):
    rows = service.store.list_growth_records(user["username"])
    if not rows:
        st.info(L("no_growth_yet"))
        return
    df = pd.DataFrame(rows)
    df[L("col_subject")] = df["subject"].map(
        {SUBJECT_CHINESE: L("subject_short_cn"), SUBJECT_ENGLISH: L("subject_short_en")}
    )
    show = df[["created_at", L("col_subject"), "genre", "topic", "word_count", "total_score"]].rename(
        columns={
            "created_at": L("col_time"),
            "genre": L("col_genre"),
            "topic": L("col_topic"),
            "word_count": L("col_wordcount"),
            "total_score": L("col_score"),
        }
    )
    dataframe(show.to_dict("records"))
    st.metric(L("total_practices"), len(df))
    st.metric(L("avg_words"), int(df["word_count"].mean()))
    st.metric(L("avg_score"), int(df["total_score"].mean()))
    st.line_chart(df.sort_values("created_at").set_index("created_at")[["word_count", "total_score"]])


def membership_page(service: AppService, user: dict):
    st.subheader(L("member_center"))
    settings = service.settings
    status = service.premium_status(user["username"])
    if status:
        st.success(L("already_member", date=status["expires_at"][:10]))
    else:
        st.info(L("free_tier_desc", n=settings.free_ai_daily_quota))

    st.markdown(
        L(
            "plan_table",
            month=settings.premium_price_month,
            year=settings.premium_price_year,
            permonth=settings.premium_price_year // 12,
        )
    )
    plan_label = st.radio(L("choose_plan"), [L("plan_month"), L("plan_year")], horizontal=True)
    plan = "month" if plan_label == L("plan_month") else "year"
    if st.button(L("create_order_btn")):
        order = service.create_payment_order(user["username"], plan)
        st.session_state.pending_order = order
    order = st.session_state.get("pending_order")
    if order:
        st.markdown(L("order_line", order_no=order["order_no"], amount=order["amount"]))
        qr_url = settings.payment_qr_month_url if order["plan"] == "month" else settings.payment_qr_year_url
        if qr_url:
            st.image(qr_url, caption=L("scan_qr"), width=260)
        else:
            st.info(L("contact_admin_qr"))
        st.caption(L("pay_note"))

    st.markdown(f"#### {L('use_activation_code')}")
    code = st.text_input(L("enter_code"))
    if st.button(L("activate_btn")) and code.strip():
        ok, message = service.redeem_code(user["username"], code)
        (st.success if ok else st.error)(message)


# ----------------------------------------------------------------------
# Parent / admin
# ----------------------------------------------------------------------
def parent_view(service: AppService, user: dict):
    st.header(L("parent_home"))
    students = service.store.list_parent_students(user["username"])
    if not students:
        st.info(L("no_bound_students"))
        return
    selected = st.selectbox(L("select_student"), [s["username"] for s in students])
    latest = service.store.latest_submission_for_parent(user["username"], selected)
    if latest:
        st.subheader(latest["title"])
        st.write(latest["essay_text"])
        st.markdown(f"**{L('teacher_feedback_hdr')}**")
        st.write(latest["teacher_feedback"])
    growth = service.store.list_growth_records(selected)
    if growth:
        st.subheader(L("growth_trend"))
        df = pd.DataFrame(growth)
        st.line_chart(df.sort_values("created_at").set_index("created_at")[["word_count", "total_score"]])


def _role_name(role: str) -> str:
    return {
        "student": L("role_student"),
        "teacher": L("role_teacher"),
        "parent": L("role_parent"),
        "admin": L("role_admin"),
    }.get(role, role)


def _admin_dashboard_tab(service: AppService):
    stats = service.dashboard_stats()
    st.markdown(f"#### {L('ops_overview')}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(L("m_users_total"), stats["users_total"], L("m_new_7d", n=stats["new_users_7d"]))
    c2.metric(L("m_submissions"), stats["submissions_total"], L("m_today", n=stats["submissions_today"]))
    c3.metric(L("m_ai_calls"), stats["ai_calls_total"], L("m_today", n=stats["ai_calls_today"]))
    c4.metric(L("m_members"), stats["active_members"])
    c5, c6, c7, c8 = st.columns(4)
    c5.metric(L("m_students"), stats["users_by_role"].get("student", 0))
    c6.metric(L("m_teachers"), stats["users_by_role"].get("teacher", 0))
    c7.metric(L("m_disabled"), stats["disabled_users"])
    c8.metric(L("m_revenue"), stats["paid_revenue"], L("m_pending_orders", n=stats["pending_orders"]))
    st.markdown(f"#### {L('role_composition')}")
    dataframe([{L("col_role"): _role_name(k), L("col_count"): v} for k, v in sorted(stats["users_by_role"].items())])
    st.markdown(f"#### {L('trend_14d')}")
    if stats["daily_submissions"]:
        df = pd.DataFrame(stats["daily_submissions"])
        st.bar_chart(df.set_index("day")["count"])
    else:
        st.caption(L("no_recent_submissions"))


def _admin_users_tab(service: AppService, user: dict):
    st.markdown(f"#### {L('account_list')}")
    users = service.store.list_users(limit=service.settings.max_page_size)
    dataframe(
        [
            {
                L("col_username"): u["username"],
                L("col_realname"): u["real_name"],
                L("col_role"): u["role"],
                L("col_grade"): u["grade"],
                L("col_class"): u["class_name"],
                L("col_status"): L("status_active") if u.get("status", "active") == "active" else L("status_disabled"),
                L("col_registered"): u["created_at"][:10],
            }
            for u in users
        ]
    )

    st.markdown(f"#### {L('manual_create_account')}")
    with st.form("create_user_form"):
        username = st.text_input(L("username"))
        real_name = st.text_input(L("real_name"))
        role = st.selectbox(L("role_label"), ["teacher", "parent", "admin", "student"])
        grade = st.selectbox(L("grade"), ["", *list(GRADE_RUBRICS)])
        class_name = st.text_input(L("class_label"))
        password = st.text_input(L("initial_password"), type="password")
        submitted = st.form_submit_button(L("create_account_btn"))
        if submitted:
            ok, message = service.create_user_by_admin(
                username, password, role, real_name, grade or None, class_name or None
            )
            (st.success if ok else st.error)(message)

    st.markdown(f"#### {L('deactivate_reactivate')}")
    if users:
        target = st.selectbox(
            L("select_account"),
            [u["username"] for u in users],
            format_func=lambda name: next(
                L(
                    "account_option",
                    username=u["username"],
                    name=u["real_name"],
                    role=u["role"],
                    status=L("status_active") if u.get("status", "active") == "active" else L("status_disabled"),
                )
                for u in users
                if u["username"] == name
            ),
            key="admin_target_user",
        )
        col_off, col_on = st.columns(2)
        with col_off:
            if st.button(L("deactivate_btn")):
                ok, message = service.set_user_active(user["username"], target, active=False)
                (st.success if ok else st.error)(message)
        with col_on:
            if st.button(L("reactivate_btn")):
                ok, message = service.set_user_active(user["username"], target, active=True)
                (st.success if ok else st.error)(message)

        st.markdown(f"#### {L('reset_password_hdr')}")
        new_pwd = st.text_input(L("new_password"), type="password", key="admin_reset_pwd")
        if st.button(L("reset_password_btn")) and new_pwd:
            ok, message = service.admin_reset_password(target, new_pwd)
            (st.success if ok else st.error)(message)


def _admin_ai_tab(service: AppService):
    st.markdown(f"#### {L('ai_service_status')}")
    status = service.llm_status()
    if status["configured"]:
        st.success(L("ai_configured", model=status["model"], base_url=status["base_url"]))
    else:
        st.error(L("ai_not_configured"))
    if status["last_success_at"]:
        st.caption(L("ai_last_success", at=status["last_success_at"]))
    if status["last_error"]:
        st.warning(L("ai_last_error", err=status["last_error"]))
    if st.button(L("test_ai_btn")):
        with st.spinner(L("testing_ai")):
            ok, message = service.llm.test_connection()
        (st.success if ok else st.error)(message)


def admin_view(service: AppService, user: dict):
    st.header(L("admin_home"))
    tab_dash, tab_users, tab_ai, tab_links, tab_orders, tab_codes = st.tabs(
        [
            L("tab_dashboard"),
            L("tab_accounts"),
            L("tab_ai_status"),
            L("tab_parent_links"),
            L("tab_orders"),
            L("tab_codes"),
        ]
    )
    with tab_dash:
        _admin_dashboard_tab(service)
    with tab_users:
        _admin_users_tab(service, user)
    with tab_ai:
        _admin_ai_tab(service)
    with tab_links:
        parent = st.text_input(L("parent_username"))
        student = st.text_input(L("student_username"))
        if st.button(L("link_btn")) and parent and student:
            service.store.link_parent_to_student(parent, student)
            st.success(L("linked_ok"))
    with tab_orders:
        pending = service.store.list_pending_orders()
        if not pending:
            st.info(L("no_pending_orders"))
        else:
            dataframe(pending)
            order_no = st.selectbox(L("select_order"), [o["order_no"] for o in pending])
            if st.button(L("confirm_order_btn")):
                ok, message = service.confirm_order(order_no)
                (st.success if ok else st.error)(message)
    with tab_codes:
        plan = st.selectbox(
            L("plan_label"),
            ["month", "year"],
            format_func=lambda p: L("plan_month_short") if p == "month" else L("plan_year_short"),
        )
        if st.button(L("gen_code_btn")):
            code = service.store.create_activation_code(plan, user["username"])
            st.success(L("code_created", code=code))


def show_feedback(title: str, genre: str, essay: str, feedback: dict, subject: str = SUBJECT_CHINESE):
    st.subheader(L("feedback_title"))
    if feedback.get("source") == "llm":
        st.caption(L("by_ai"))
    elif feedback.get("source") == "fallback":
        key = FALLBACK_TEXT_KEYS.get(feedback.get("fallback_reason"))
        st.warning(L(key) if key else L("fallback_generic"))
    st.markdown(f"### {L('teacher_version')}")
    st.write(feedback["teacher_feedback"])
    st.markdown(f"### {L('student_version')}")
    st.success(feedback["student_feedback"])
    st.markdown(f"### {L('strengths')}")
    for item in feedback.get("strengths", []):
        st.markdown(f"- {item}")
    st.markdown(f"### {L('suggestions')}")
    for item in feedback.get("suggestions", []):
        st.markdown(f"- {item}")
    if feedback.get("polished_sentence"):
        st.markdown(f"### {L('polished')}")
        st.info(feedback["polished_sentence"])
    corrections = feedback.get("grammar_corrections") or []
    if corrections:
        st.markdown(f"### {L('grammar_fixes')}")
        for c in corrections[:5]:
            if isinstance(c, dict):
                st.markdown(f"- ~~{c.get('original', '')}~~ → **{c.get('corrected', '')}**（{c.get('note', '')}）")
    step = feedback.get("step_rewrite") or {}
    if isinstance(step, dict) and step:
        st.markdown(f"### {L('step_rewrite_hdr')}")
        for i, (key, value) in enumerate(step.items(), 1):
            st.write(f"{i}. {key}：{value}")
    if subject == SUBJECT_CHINESE:
        st.info(compare_with_model_essay(essay, genre, title))


def main():
    settings = Settings.from_env()
    st.set_page_config(page_title=settings.app_title, page_icon="📝", layout="wide")
    inject_responsive_styles()
    service = build_service()
    st.session_state.setdefault("ui_lang", DEFAULT_LANG)
    st.title(service.settings.app_title)
    st.caption(L("app_caption"))
    auth_sidebar(service)
    user = st.session_state.get("user")
    if not user:
        st.info(L("please_login"))
        return
    if user["role"] == "teacher":
        teacher_view(service, user)
    elif user["role"] == "student":
        student_view(service, user)
    elif user["role"] == "parent":
        parent_view(service, user)
    elif user["role"] == "admin":
        admin_view(service, user)
    else:
        st.warning(L("unknown_role"))
