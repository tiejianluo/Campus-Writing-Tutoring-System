import pandas as pd
import streamlit as st

from .config import Settings
from .content import ESSAY_TEMPLATES, GRADE_RUBRICS
from .llm import LLMService
from .metrics import (
    chinese_word_count,
    compare_with_model_essay,
    generate_topics,
    grade_expectation,
    infer_expression_score,
    infer_structure_score,
)
from .responsive import inject_responsive_styles, render_records
from .services import AppService
from .storage import SQLiteStore
from .uploads import UploadValidationError, load_uploaded_image, read_uploaded_text


@st.cache_resource
def build_service() -> AppService:
    settings = Settings.from_env()
    store = SQLiteStore(settings)
    service = AppService(settings, store, LLMService(settings))
    service.initialize()
    return service


def dataframe(rows: list[dict]) -> None:
    render_records(rows)


def auth_sidebar(service: AppService):
    st.sidebar.title("账号系统")
    st.session_state.setdefault("user", None)
    user = st.session_state.user
    if user:
        st.sidebar.success(f"已登录：{user['real_name']}（{user['role']}）")
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
            st.error("用户名或密码错误。")
    with register_tab:
        username = st.text_input("新用户名", key="reg_user")
        real_name = st.text_input("姓名", key="reg_name")
        grade = st.selectbox("年级", list(GRADE_RUBRICS), key="reg_grade")
        class_name = st.text_input("班级", key="reg_class")
        password = st.text_input("设置密码", type="password", key="reg_pwd")
        if st.button("注册学生账号"):
            ok, message = service.register_public_student(username, password, real_name, grade, class_name or None)
            if ok:
                st.success(message)
            else:
                st.error(message)


def teacher_view(service: AppService, user: dict):
    st.header("老师端")
    assign_tab, submissions_tab, class_tab = st.tabs(["布置作文题", "班级提交", "班级管理"])
    classes = service.store.list_teacher_classes(user["username"])

    with assign_tab:
        if not classes:
            st.info("请先创建班级。")
        else:
            class_options = [c["class_name"] for c in classes]
            class_name = st.selectbox("选择班级", class_options, key="assign_class")
            grade = next((c["grade"] for c in classes if c["class_name"] == class_name), "三年级")
            genre = st.selectbox("作文类型", list(ESSAY_TEMPLATES), key="assign_genre")
            title = st.text_input("作文题目")
            prompt = st.text_area("布置说明")
            due_date = st.date_input("截止日期")
            if st.button("发布作文题") and title.strip():
                service.create_assignment(user["username"], title, genre, prompt, grade, class_name, str(due_date))
                st.success("作文题已发布。")

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
            service.store.create_class(class_name.strip(), grade, user["username"])
            st.success("已新增班级。")
        dataframe(service.store.list_teacher_classes(user["username"]))


def student_view(service: AppService, user: dict):
    st.header("学生端")
    menu = st.radio("选择功能", ["开始写作文", "看图作文", "历史记录", "成长档案"], horizontal=True)
    grade = user.get("grade") or "三年级"

    if menu == "开始写作文":
        rows = service.store.list_assignments_for_student(grade, user.get("class_name"), limit=service.page_size())
        with st.expander("老师布置的作文题", expanded=True):
            dataframe(rows) if rows else st.info("暂时没有老师布置的作文题。")
        genre = st.selectbox("作文类型", list(ESSAY_TEMPLATES))
        topic = st.selectbox("主题/题目", generate_topics(grade, genre))
        title = st.text_input("自定义题目（可选）") or topic
        st.caption(grade_expectation(grade))
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
            else:
                try:
                    sid, feedback = service.review_and_save_submission(user["username"], grade, genre, title, title, essay)
                except ValueError as exc:
                    st.error(str(exc))
                    return
                show_feedback(title, genre, essay, feedback)
                st.success(f"已保存本次作文，编号：{sid}")

    elif menu == "看图作文":
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

    elif menu == "历史记录":
        dataframe(service.store.list_student_submissions(user["username"], limit=service.page_size()))

    elif menu == "成长档案":
        rows = service.store.list_growth_records(user["username"])
        if not rows:
            st.info("还没有成长记录。")
        else:
            df = pd.DataFrame(rows)
            st.metric("累计练习次数", len(df))
            st.metric("平均字数", int(df["word_count"].mean()))
            st.metric("平均总分", int(df["total_score"].mean()))
            st.line_chart(df.sort_values("created_at").set_index("created_at")[["word_count", "total_score"]])


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


def admin_view(service: AppService):
    st.header("管理员端")
    tab_users, tab_links = st.tabs(["用户", "家长绑定"])
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
                ok = service.create_user_by_admin(username, password, role, real_name, grade or None, class_name or None)
                st.success("已创建。") if ok else st.error("创建失败。")
    with tab_links:
        parent = st.text_input("家长用户名")
        student = st.text_input("学生用户名")
        if st.button("绑定家长与学生") and parent and student:
            service.store.link_parent_to_student(parent, student)
            st.success("已绑定。")


def show_feedback(title: str, genre: str, essay: str, feedback: dict):
    st.subheader("作文点评结果")
    c1, c2, c3 = st.columns(3)
    c1.metric("字数", chinese_word_count(essay))
    c2.metric("结构分", infer_structure_score(essay))
    c3.metric("表达分", infer_expression_score(essay))
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
    st.info(compare_with_model_essay(essay, genre, title))


def main():
    settings = Settings.from_env()
    st.set_page_config(page_title=settings.app_title, page_icon="📝", layout="wide")
    inject_responsive_styles()
    service = build_service()
    st.title(service.settings.app_title)
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
        admin_view(service)
    else:
        st.warning("未知角色。")
