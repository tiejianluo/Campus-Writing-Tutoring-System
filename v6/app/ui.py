import json

import pandas as pd
import streamlit as st

from .config import Settings
from .content import ESSAY_TEMPLATES, GRADE_RUBRICS
from .content_en import ENGLISH_TEMPLATES, english_genres_for_grade
from .llm import SUBJECT_CHINESE, SUBJECT_ENGLISH, LLMService
from .metrics import compare_with_model_essay, generate_topics, grade_expectation
from .metrics_en import generate_topics_en, grade_expectation_en
from .responsive import inject_responsive_styles, render_records
from .services import AppService, QuotaExceededError
from .storage import SQLiteStore
from .uploads import UploadValidationError, load_uploaded_image, read_uploaded_text

SUBJECT_LABELS = {"语文作文": SUBJECT_CHINESE, "英语写作 English": SUBJECT_ENGLISH}


@st.cache_resource
def build_service() -> AppService:
    settings = Settings.from_env()
    store = SQLiteStore(settings)
    service = AppService(settings, store, LLMService(settings))
    service.initialize()
    return service


def dataframe(rows: list[dict]) -> None:
    render_records(rows)


def require_premium(service: AppService, user: dict, feature_label: str) -> bool:
    if service.is_premium(user["username"]):
        return True
    st.warning(f"「{feature_label}」是会员功能。开通会员即可使用：{service.settings.premium_price_month} 元/月、"
               f"{service.settings.premium_price_year} 元/年。请到「会员中心」开通。")
    return False


def auth_sidebar(service: AppService):
    st.sidebar.title("账号系统")
    st.session_state.setdefault("user", None)
    user = st.session_state.user
    if user:
        parts = [user["real_name"], f"（{user['role']}）"]
        if user.get("grade"):
            parts.append(f" {user['grade']}")
        if user.get("class_name"):
            parts.append(f" {user['class_name']}")
        st.sidebar.success("已登录：" + "".join(parts))
        status = service.premium_status(user["username"])
        if status:
            st.sidebar.info(f"会员有效期至 {status['expires_at'][:10]}")
        else:
            quota = service.ai_quota_left(user["username"])
            st.sidebar.caption(f"今日剩余免费 AI 点评：{quota} 次")
        if st.sidebar.button("退出登录"):
            st.session_state.user = None
            st.rerun()
        return

    login_tab, register_tab = st.sidebar.tabs(["登录", "学生注册"])
    with login_tab:
        username = st.text_input("用户名", key="login_user")
        password = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录"):
            logged_in = service.login(username, password)
            if logged_in:
                st.session_state.user = logged_in
                st.rerun()
            st.error("用户名或密码错误，或尝试过于频繁。")
    with register_tab:
        username = st.text_input("新用户名", key="reg_user")
        real_name = st.text_input("姓名", key="reg_name")
        grade = st.selectbox("年级", list(GRADE_RUBRICS), key="reg_grade")
        invite_code = st.text_input("班级邀请码（老师提供，可选）", key="reg_invite")
        password = st.text_input("设置密码", type="password", key="reg_pwd")
        if st.button("注册学生账号"):
            ok, message = service.register_public_student(username, password, real_name, grade, invite_code or None)
            if ok:
                st.success(message + f" 新用户赠送 {service.settings.premium_trial_days} 天会员体验。")
            else:
                st.error(message)


# ----------------------------------------------------------------------
# Teacher
# ----------------------------------------------------------------------
def teacher_view(service: AppService, user: dict):
    st.header("老师端")
    assign_tab, submissions_tab, class_tab = st.tabs(["布置作文题", "班级提交", "班级管理"])
    classes = service.store.list_teacher_classes(user["username"])

    with assign_tab:
        if not classes:
            st.info("请先在「班级管理」创建班级。")
        else:
            class_options = [c["class_name"] for c in classes]
            class_name = st.selectbox("选择班级", class_options, key="assign_class")
            grade = next((c["grade"] for c in classes if c["class_name"] == class_name), "三年级")
            subject_label = st.radio("科目", list(SUBJECT_LABELS), horizontal=True, key="assign_subject")
            subject = SUBJECT_LABELS[subject_label]
            genres = list(ESSAY_TEMPLATES) if subject == SUBJECT_CHINESE else english_genres_for_grade(grade)
            genre = st.selectbox("作文类型", genres, key="assign_genre")
            title = st.text_input("作文题目")
            prompt = st.text_area("布置说明（学生端可见）")
            due_date = st.date_input("截止日期")
            if st.button("发布作文题") and title.strip():
                try:
                    service.create_assignment(
                        user["username"], title, genre, prompt, grade, class_name, str(due_date), subject
                    )
                    st.success("作文题已发布。")
                except PermissionError as exc:
                    st.error(str(exc))

        st.markdown("#### 已布置的作文题")
        history = service.store.list_teacher_assignments(user["username"], limit=service.page_size())
        if history:
            dataframe(
                [
                    {
                        "编号": r["id"],
                        "题目": r["title"],
                        "科目": "英语" if r["subject"] == SUBJECT_ENGLISH else "语文",
                        "类型": r["genre"],
                        "班级": r["class_name"],
                        "截止": r["due_date"],
                        "布置说明": r["prompt"],
                    }
                    for r in history
                ]
            )
        else:
            st.caption("还没有布置过作文题。")

    with submissions_tab:
        page = st.number_input("页码", min_value=1, value=1, step=1)
        size = service.page_size()
        rows = service.store.list_teacher_submissions(user["username"], limit=size, offset=(page - 1) * size)
        dataframe(rows)
        if rows:
            sid = st.selectbox("查看提交", [r["id"] for r in rows])
            detail = service.store.get_submission_for_teacher(user["username"], int(sid))
            if detail:
                st.subheader(detail["title"])
                st.write(detail["essay_text"])
                st.markdown("**教师点评**")
                st.write(detail["teacher_feedback"])

    with class_tab:
        grade = st.selectbox("年级", list(GRADE_RUBRICS), key="class_grade")
        class_name = st.text_input("新班级名称")
        if st.button("新增班级") and class_name.strip():
            ok, result = service.create_class(user["username"], class_name, grade)
            if ok:
                st.success(f"已新增班级，邀请码：{result}（发给学生注册时填写即可自动入班）")
            else:
                st.error(result)
        dataframe(service.store.list_teacher_classes(user["username"]))


# ----------------------------------------------------------------------
# Student
# ----------------------------------------------------------------------
def student_view(service: AppService, user: dict):
    st.header("学生端")
    menu = st.radio(
        "选择功能",
        ["开始写作文", "看图作文", "继续改写", "历史版本对比", "成长档案", "会员中心"],
        horizontal=True,
    )
    grade = user.get("grade") or "三年级"

    if menu == "开始写作文":
        _writing_page(service, user, grade)
    elif menu == "看图作文":
        _image_page(service, user, grade)
    elif menu == "继续改写":
        _rewrite_page(service, user)
    elif menu == "历史版本对比":
        _version_page(service, user)
    elif menu == "成长档案":
        _growth_page(service, user)
    elif menu == "会员中心":
        membership_page(service, user)


def _writing_page(service: AppService, user: dict, grade: str):
    rows = service.store.list_assignments_for_student(grade, user.get("class_name"), limit=service.page_size())
    with st.expander("老师布置的作文题", expanded=True):
        if not rows:
            st.info("暂时没有老师布置的作文题，你也可以自己练习。")
        for r in rows:
            subject_tag = "英语" if r["subject"] == SUBJECT_ENGLISH else "语文"
            st.markdown(f"**[{subject_tag}] {r['title']}**（{r['genre']}，截止 {r['due_date']}）")
            if r.get("prompt"):
                st.caption(f"作文要求：{r['prompt']}")

    subject_label = st.radio("科目", list(SUBJECT_LABELS), horizontal=True, key="write_subject")
    subject = SUBJECT_LABELS[subject_label]

    if subject == SUBJECT_CHINESE:
        genre = st.selectbox("作文类型", list(ESSAY_TEMPLATES))
        topic = st.selectbox("主题/题目", generate_topics(grade, genre))
        st.caption(grade_expectation(grade))
        tpl = ESSAY_TEMPLATES[genre]
    else:
        genres = english_genres_for_grade(grade)
        genre = st.selectbox("Writing type 作文类型", genres)
        topic = st.selectbox("Topic 题目", generate_topics_en(grade, genre))
        st.caption(grade_expectation_en(grade))
        tpl = ENGLISH_TEMPLATES[genre]

    title = st.text_input("自定义题目（可选）") or topic
    with st.expander("写作指导 / Writing guide"):
        st.markdown("**推荐结构**")
        for x in tpl["结构"]:
            st.markdown(f"- {x}")
        st.markdown(f"**参考开头**：{tpl['万能开头']}")
        st.markdown(f"**参考结尾**：{tpl['万能结尾']}")
        for pattern in tpl.get("常用句型", []):
            st.markdown(f"- 常用句型：`{pattern}`")

    essay = st.text_area("开始写作文", height=280)
    uploaded_txt = st.file_uploader("或上传 txt 草稿", type=["txt"])
    if uploaded_txt:
        try:
            essay = read_uploaded_text(uploaded_txt, service.settings)
            st.text_area("已读取草稿", essay, height=180)
        except UploadValidationError as exc:
            st.error(str(exc))
    if st.button("生成点评并保存"):
        if not essay.strip():
            st.warning("请先输入作文内容。")
            return
        try:
            sid, feedback = service.review_and_save_submission(
                user["username"], grade, genre, title, title, essay, subject=subject
            )
        except QuotaExceededError as exc:
            st.warning(str(exc))
            return
        except ValueError as exc:
            st.error(str(exc))
            return
        show_feedback(title, genre, essay, feedback, subject)
        st.success(f"已保存本次作文，编号：{sid}。可在「继续改写」中修改并保存新版本。")


def _image_page(service: AppService, user: dict, grade: str):
    if not require_premium(service, user, "看图作文 AI 观察提示"):
        return
    image_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
    if image_file:
        try:
            image = load_uploaded_image(image_file, service.settings)
        except UploadValidationError as exc:
            st.error(str(exc))
            return
        st.image(image, caption="上传的图片", use_container_width=True)
        if st.button("生成观察提示"):
            obs = service.llm.image_prompts(image, grade, user_key=user["username"])
            st.subheader("场景概括")
            st.write(obs.get("scene", ""))
            st.subheader("观察提示")
            for item in obs.get("observe", []):
                st.markdown(f"- {item}")
            st.subheader("启发问题")
            for item in obs.get("questions", []):
                st.markdown(f"- {item}")
            if obs.get("source") == "fallback":
                st.caption("当前为基础提示（AI 暂不可用或已限流）。")


def _rewrite_page(service: AppService, user: dict):
    st.subheader("继续改写")
    if not require_premium(service, user, "继续改写"):
        return
    submissions = service.store.list_student_submissions(user["username"], limit=service.page_size())
    if not submissions:
        st.info("还没有作文记录，请先开始写作文。")
        return
    options = {
        f"#{r['id']} {r['title']}（{r['genre']}，{r['created_at'][:10]}，{r['total_score']}分）": r["id"]
        for r in submissions
    }
    label = st.selectbox("选择要改写的作文", list(options))
    submission_id = options[label]
    original = service.store.get_submission_for_student(user["username"], submission_id)
    if not original:
        st.error("无法加载作文。")
        return

    versions = service.store.list_versions(submission_id)
    st.caption(f"当前已有 {len(versions)} 个版本。")
    st.markdown("#### 原文（最新版本）")
    st.text_area("原文", original["essay_text"], height=160, disabled=True)

    st.markdown("#### 改写指导")
    try:
        steps = json.loads(original["revised_steps"])
    except Exception:
        steps = {}
    if isinstance(steps, dict) and steps:
        for key, value in steps.items():
            st.info(f"**{key}**：{value}")
    else:
        st.caption("暂无改写指导。")

    rewritten = st.text_area("改写后的作文", height=280, placeholder="根据指导建议，在这里写下改写后的作文……")
    if st.button("提交新版本", type="primary"):
        if not rewritten.strip():
            st.warning("请先填写改写后的作文。")
            return
        try:
            version_no, feedback = service.rewrite_submission(user["username"], submission_id, rewritten)
        except QuotaExceededError as exc:
            st.warning(str(exc))
            return
        except (PermissionError, ValueError) as exc:
            st.error(str(exc))
            return
        st.success(f"新版本（v{version_no}）提交成功！可到「历史版本对比」查看变化。")
        show_feedback(original["title"], original["genre"], rewritten, feedback, original.get("subject", SUBJECT_CHINESE))


def _version_page(service: AppService, user: dict):
    st.subheader("历史版本对比")
    if not require_premium(service, user, "历史版本对比"):
        return
    submissions = service.store.list_student_submissions(user["username"], limit=service.page_size())
    if not submissions:
        st.info("还没有作文记录。")
        return
    options = {f"#{r['id']} {r['title']}（{r['created_at'][:10]}）": r["id"] for r in submissions}
    label = st.selectbox("选择作文", list(options))
    versions = service.store.list_versions(options[label])
    if len(versions) < 2:
        st.info("这篇作文只有一个版本，先到「继续改写」提交新版本，再回来对比。")
        return
    numbers = [v["version_no"] for v in versions]
    col_a, col_b = st.columns(2)
    with col_a:
        va = st.selectbox("版本 A", numbers, index=0)
    with col_b:
        vb = st.selectbox("版本 B", numbers, index=len(numbers) - 1)
    version_a = next(v for v in versions if v["version_no"] == va)
    version_b = next(v for v in versions if v["version_no"] == vb)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**版本 {va}**（{version_a['word_count']} 字，{version_a['total_score']} 分）")
        st.text_area("版本A", version_a["essay_text"], height=240, disabled=True, key="va_text")
    with c2:
        st.markdown(f"**版本 {vb}**（{version_b['word_count']} 字，{version_b['total_score']} 分）")
        st.text_area("版本B", version_b["essay_text"], height=240, disabled=True, key="vb_text")
    st.metric("字数变化", f"{version_b['word_count'] - version_a['word_count']:+d}")
    st.metric("总分变化", f"{version_b['total_score'] - version_a['total_score']:+d}")


def _growth_page(service: AppService, user: dict):
    rows = service.store.list_growth_records(user["username"])
    if not rows:
        st.info("还没有成长记录。")
        return
    df = pd.DataFrame(rows)
    df["科目"] = df["subject"].map({SUBJECT_CHINESE: "语文", SUBJECT_ENGLISH: "英语"})
    show = df[["created_at", "科目", "genre", "topic", "word_count", "total_score"]].rename(
        columns={"created_at": "时间", "genre": "类型", "topic": "题目", "word_count": "字数/词数", "total_score": "总分"}
    )
    dataframe(show.to_dict("records"))
    st.metric("累计练习次数", len(df))
    st.metric("平均字数/词数", int(df["word_count"].mean()))
    st.metric("平均总分", int(df["total_score"].mean()))
    st.line_chart(df.sort_values("created_at").set_index("created_at")[["word_count", "total_score"]])


def membership_page(service: AppService, user: dict):
    st.subheader("会员中心")
    settings = service.settings
    status = service.premium_status(user["username"])
    if status:
        st.success(f"你已是会员，有效期至 {status['expires_at'][:10]}。")
    else:
        st.info(f"当前为免费版：每天 {settings.free_ai_daily_quota} 次 AI 点评；"
                "会员可享不限次 AI 点评、英语 AI 精批、看图作文、继续改写与版本对比。")

    st.markdown(
        f"""
| 套餐 | 价格 |
|---|---|
| 月度会员 | **{settings.premium_price_month} 元 / 月** |
| 年度会员 | **{settings.premium_price_year} 元 / 年**（约 {settings.premium_price_year // 12} 元/月） |
"""
    )
    plan_label = st.radio("选择套餐", ["月度会员", "年度会员"], horizontal=True)
    plan = "month" if plan_label == "月度会员" else "year"
    if st.button("生成付款订单"):
        order = service.create_payment_order(user["username"], plan)
        st.session_state.pending_order = order
    order = st.session_state.get("pending_order")
    if order:
        st.markdown(f"#### 订单号：`{order['order_no']}`（{order['amount']} 元）")
        qr_url = settings.payment_qr_month_url if order["plan"] == "month" else settings.payment_qr_year_url
        if qr_url:
            st.image(qr_url, caption="请扫码支付，并在转账备注中填写订单号", width=260)
        else:
            st.info("请联系管理员获取收款二维码，支付时备注订单号。")
        st.caption("请在家长指导下完成支付。管理员确认到账后会员自动开通。")

    st.markdown("#### 使用激活码")
    code = st.text_input("输入激活码")
    if st.button("激活会员") and code.strip():
        ok, message = service.redeem_code(user["username"], code)
        (st.success if ok else st.error)(message)


# ----------------------------------------------------------------------
# Parent / admin
# ----------------------------------------------------------------------
def parent_view(service: AppService, user: dict):
    st.header("家长端")
    students = service.store.list_parent_students(user["username"])
    if not students:
        st.info("暂无已绑定学生，请联系管理员绑定。")
        return
    selected = st.selectbox("选择学生", [s["username"] for s in students])
    latest = service.store.latest_submission_for_parent(user["username"], selected)
    if latest:
        st.subheader(latest["title"])
        st.write(latest["essay_text"])
        st.markdown("**教师点评**")
        st.write(latest["teacher_feedback"])
    growth = service.store.list_growth_records(selected)
    if growth:
        st.subheader("成长趋势")
        df = pd.DataFrame(growth)
        st.line_chart(df.sort_values("created_at").set_index("created_at")[["word_count", "total_score"]])


def admin_view(service: AppService, user: dict):
    st.header("管理员端")
    tab_users, tab_links, tab_orders, tab_codes = st.tabs(["用户", "家长绑定", "订单核销", "激活码"])
    with tab_users:
        dataframe(service.store.list_users(limit=service.settings.max_page_size))
        with st.form("create_user_form"):
            username = st.text_input("用户名")
            real_name = st.text_input("姓名")
            role = st.selectbox("角色", ["teacher", "parent", "admin", "student"])
            grade = st.selectbox("年级", ["", *list(GRADE_RUBRICS)])
            class_name = st.text_input("班级")
            password = st.text_input("初始密码", type="password")
            submitted = st.form_submit_button("创建账号")
            if submitted:
                ok, message = service.create_user_by_admin(
                    username, password, role, real_name, grade or None, class_name or None
                )
                (st.success if ok else st.error)(message)
    with tab_links:
        parent = st.text_input("家长用户名")
        student = st.text_input("学生用户名")
        if st.button("绑定家长与学生") and parent and student:
            service.store.link_parent_to_student(parent, student)
            st.success("已绑定。")
    with tab_orders:
        pending = service.store.list_pending_orders()
        if not pending:
            st.info("暂无待核销订单。")
        else:
            dataframe(pending)
            order_no = st.selectbox("选择订单", [o["order_no"] for o in pending])
            if st.button("确认到账并开通会员"):
                ok, message = service.confirm_order(order_no)
                (st.success if ok else st.error)(message)
    with tab_codes:
        plan = st.selectbox("套餐", ["month", "year"], format_func=lambda p: "月度" if p == "month" else "年度")
        if st.button("生成激活码"):
            code = service.store.create_activation_code(plan, user["username"])
            st.success(f"激活码：`{code}`（一次性，请线下发给用户）")


def show_feedback(title: str, genre: str, essay: str, feedback: dict, subject: str = SUBJECT_CHINESE):
    st.subheader("作文点评结果")
    if feedback.get("source") == "fallback":
        st.caption("本次为基础点评（AI 暂不可用、已限流或免费额度用完）。升级会员可享不限次 AI 智能点评。")
    st.markdown("### 教师点评版")
    st.write(feedback["teacher_feedback"])
    st.markdown("### 学生鼓励版")
    st.success(feedback["student_feedback"])
    st.markdown("### 优点")
    for item in feedback.get("strengths", []):
        st.markdown(f"- {item}")
    st.markdown("### 改进建议")
    for item in feedback.get("suggestions", []):
        st.markdown(f"- {item}")
    if feedback.get("polished_sentence"):
        st.markdown("### 佳句润色")
        st.info(feedback["polished_sentence"])
    corrections = feedback.get("grammar_corrections") or []
    if corrections:
        st.markdown("### 语法与拼写订正")
        for c in corrections[:5]:
            if isinstance(c, dict):
                st.markdown(f"- ~~{c.get('original', '')}~~ → **{c.get('corrected', '')}**（{c.get('note', '')}）")
    step = feedback.get("step_rewrite") or {}
    if isinstance(step, dict) and step:
        st.markdown("### 分步改写")
        for i, (key, value) in enumerate(step.items(), 1):
            st.write(f"{i}. {key}：{value}")
    if subject == SUBJECT_CHINESE:
        st.info(compare_with_model_essay(essay, genre, title))


def main():
    settings = Settings.from_env()
    st.set_page_config(page_title=settings.app_title, page_icon="📝", layout="wide")
    inject_responsive_styles()
    service = build_service()
    st.title(service.settings.app_title)
    st.caption("语文作文 + K12 小学英语写作 · AI 点评 · 继续改写 · 成长档案")
    auth_sidebar(service)
    user = st.session_state.get("user")
    if not user:
        st.info("请先登录或注册学生账号。")
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
        st.warning("未知角色。")
