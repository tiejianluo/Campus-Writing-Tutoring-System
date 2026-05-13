import os
import json
import textwrap
from typing import Dict, Any, List

import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

APP_TITLE = "妙妙作文屋：小学生作文辅导"
APP_SUBTITLE = "选题—写作—点评—修改，一站式完成"

GRADE_OPTIONS = ["三年级", "四年级", "五年级", "六年级"]
GENRE_OPTIONS = ["记叙文", "写人", "写景", "想象作文", "读后感", "日记", "看图作文"]
THEME_OPTIONS = [
    "难忘的一天", "我的好朋友", "一次有趣的活动", "秋天来了", "我的家人", "我最喜欢的动物",
    "校园一角", "假如我会飞", "我学会了____", "一件让我感动的事", "我的理想", "图片作文"
]

RUBRIC = {
    "立意与内容": "是否切题，内容是否真实、具体、有中心。",
    "结构与条理": "是否有开头、经过、结尾，段落是否清楚。",
    "语言表达": "句子是否通顺，用词是否准确、生动。",
    "细节描写": "是否有动作、语言、心理、景物等细节。",
    "书写规范": "标点、病句、重复表达、错别字等。",
}

SYSTEM_PROMPT = """
你是一位耐心、温和、擅长启发式教学的小学作文老师。
你的学生是中国小学生，请遵循以下要求：
1. 语言简单、鼓励性强，不能打击孩子自信心。
2. 优先指出优点，再给出可操作的改进建议。
3. 给建议时必须具体，避免空泛表述。
4. 所有输出都要适合小学生理解，不使用艰深术语。
5. 不替学生完全重写整篇作文，除非用户明确要求；优先做“引导式修改”。
6. 输出必须是合法 JSON。
""".strip()

JSON_SCHEMA_HINT = {
    "summary": "用1-2句话概括作文亮点和主要问题",
    "scores": {
        "立意与内容": 0,
        "结构与条理": 0,
        "语言表达": 0,
        "细节描写": 0,
        "书写规范": 0,
    },
    "strengths": ["至少3条优点"],
    "improvements": ["至少3条具体改进建议"],
    "sentence_polish": [
        {"original": "原句", "better": "修改建议", "reason": "为什么这样更好"}
    ],
    "outline_advice": ["如果内容不足，给3-5个补写提示"],
    "encouragement": "一句鼓励孩子的话"
}


def get_config_value(name: str, default: str = "") -> str:
    env_value = os.getenv(name)
    if env_value:
        return env_value
    try:
        secret_value = st.secrets.get(name)
    except Exception:
        return default
    return secret_value or default


def get_client():
    if OpenAI is None:
        return None
    api_key = get_config_value("OPENAI_API_KEY")
    base_url = get_config_value("OPENAI_BASE_URL", "https://4.0.wokaai.com/v1/")
    if not api_key:
        return None
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def build_user_prompt(grade: str, genre: str, theme: str, goal_words: int, essay: str) -> str:
    rubric_text = "\n".join([f"- {k}: {v}" for k, v in RUBRIC.items()])
    return textwrap.dedent(f"""
    请作为小学作文老师，分析下面这篇作文，并严格输出 JSON。

    学生年级：{grade}
    作文类型：{genre}
    主题：{theme}
    目标字数：{goal_words}

    评分维度：
    {rubric_text}

    输出 JSON 键必须包含：
    {json.dumps(JSON_SCHEMA_HINT, ensure_ascii=False)}

    评分要求：
    - 每项分数范围 1-10
    - strengths 至少3条
    - improvements 至少3条
    - sentence_polish 给出2-4条
    - outline_advice 给出3-5条

    学生作文如下：
    {essay}
    """).strip()


def fallback_feedback(essay: str) -> Dict[str, Any]:
    lines = [s for s in essay.replace("\n", "").split("。") if s.strip()]
    too_short = len(essay) < 120
    return {
        "summary": "这篇作文已经表达了一个完整主题，但还可以在细节和条理上更清楚一些。" if not too_short else "这篇作文有主题，但篇幅偏短，内容还可以写得更具体。",
        "scores": {
            "立意与内容": 7,
            "结构与条理": 6,
            "语言表达": 7,
            "细节描写": 5 if too_short else 6,
            "书写规范": 8,
        },
        "strengths": [
            "主题比较明确，能看出你想表达的重点。",
            "句子基本通顺，读起来比较自然。",
            "有一定的生活感受，内容不空洞。"
        ],
        "improvements": [
            "可以补充事情发生的时间、地点和人物，让内容更完整。",
            "可以多写动作、语言或心理活动，让画面更生动。",
            "结尾可以再点一下自己的感受，让中心更突出。"
        ],
        "sentence_polish": [
            {
                "original": lines[0] + "。" if lines else "今天发生了一件事。",
                "better": "那天的经历让我一直记到现在。",
                "reason": "这样开头更能吸引读者。"
            },
            {
                "original": lines[1] + "。" if len(lines) > 1 else "我很开心。",
                "better": "我高兴得嘴角一直上扬，心里像开了一朵花。",
                "reason": "加入比喻后，感受更具体。"
            }
        ],
        "outline_advice": [
            "先交代事情发生的时间、地点和人物。",
            "重点写清楚事情经过，可以分两到三步写。",
            "补充一两处动作或语言描写。",
            "结尾写出自己的收获或感受。"
        ],
        "encouragement": "你已经写出了自己的想法，再补充一些细节，这篇作文会更棒！"
    }


def call_llm(grade: str, genre: str, theme: str, goal_words: int, essay: str) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return fallback_feedback(essay)

    model = "gpt-4.1-2025-04-14"
    prompt = build_user_prompt(grade, genre, theme, goal_words, essay)
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception:
        return fallback_feedback(essay)


def make_revision_prompt(essay: str, feedback: Dict[str, Any]) -> str:
    strengths = "\n".join([f"- {x}" for x in feedback.get("strengths", [])])
    improvements = "\n".join([f"- {x}" for x in feedback.get("improvements", [])])
    return textwrap.dedent(f"""
    请根据下面的老师点评，帮小学生做“引导式修改建议”。
    不要直接重写整篇作文，而是输出三个部分：
    1. 可以先补充什么内容
    2. 哪几句话可以改得更生动
    3. 一个适合小学生仿写的参考开头（80字以内）

    原作文：
    {essay}

    优点：
    {strengths}

    改进建议：
    {improvements}
    """).strip()


def revise_guidance(essay: str, feedback: Dict[str, Any]) -> str:
    client = get_client()
    if client is None:
        return "\n".join([
            "1. 可以先补充：时间、地点、人物和事情经过。",
            "2. 可以改写：把‘很开心’‘很难过’之类的词，换成动作、表情和心理描写。",
            "3. 参考开头：那天发生的一件事，让我到现在想起来还觉得特别难忘。"
        ])
    try:
        model = "gpt-4.1-2025-04-14"
        response = client.chat.completions.create(
            model=model,
            temperature=0.4,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": make_revision_prompt(essay, feedback)},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return "1. 补充事情经过。\n2. 增加动作和语言描写。\n3. 开头先点题。"


def count_chinese_chars(text: str) -> int:
    return sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="✏️", layout="wide")

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.markdown("这个应用参考了你上传的蓝图：页面 5-7 展示了最小脚手架、适合小学生的交互控件，以及“学生输入—逻辑处理—反馈展示”的三层结构；页面 8 和 11 强调了快速部署和迭代路径。fileciteturn6file0")

    with st.sidebar:
        st.header("写作设置")
        grade = st.selectbox("年级", GRADE_OPTIONS, index=1)
        genre = st.selectbox("作文类型", GENRE_OPTIONS, index=0)
        theme = st.selectbox("作文主题", THEME_OPTIONS, index=0)
        goal_words = st.slider("目标字数", 100, 800, 300, step=50)
        uploaded = st.file_uploader("上传草稿（txt）", type=["txt"])
        st.info("未配置模型 API 时，系统会使用内置示例反馈，便于你先演示流程。")

    left, right = st.columns([1.2, 1.0])

    initial_text = ""
    if uploaded is not None:
        initial_text = uploaded.read().decode("utf-8", errors="ignore")

    with left:
        essay = st.text_area(
            "请写下作文草稿",
            value=initial_text,
            height=360,
            placeholder="例如：今天我和同学们一起去秋游，一路上发生了很多有趣的事情……"
        )
        current_words = count_chinese_chars(essay)
        progress = min(current_words / max(goal_words, 1), 1.0)
        st.progress(progress, text=f"当前字数约 {current_words} / 目标 {goal_words}")

        tips = st.expander("写作小提示", expanded=True)
        with tips:
            st.markdown(
                "- 先写清楚时间、地点、人物\n"
                "- 经过可以分 2-3 个步骤写\n"
                "- 多写动作、语言、心理\n"
                "- 结尾写感受或收获"
            )

        analyze = st.button("开始点评", type="primary", use_container_width=True)

    with right:
        st.subheader("老师反馈")
        result_box = st.container(border=True)

    if analyze:
        if not essay.strip():
            st.warning("请先输入作文内容。")
            return

        feedback = call_llm(grade, genre, theme, goal_words, essay)
        st.session_state["essay_feedback"] = feedback
        st.session_state["essay_text"] = essay

    feedback = st.session_state.get("essay_feedback")
    if feedback:
        with right:
            with result_box:
                st.markdown(f"**总体评价：** {feedback.get('summary', '')}")

                st.markdown("**五维评分**")
                scores = feedback.get("scores", {})
                for k, v in scores.items():
                    st.write(f"{k}: {v}/10")
                    st.progress(min(float(v) / 10.0, 1.0))

                st.markdown("**这篇作文的优点**")
                for x in feedback.get("strengths", []):
                    st.write(f"✅ {x}")

                st.markdown("**接下来可以改进的地方**")
                for x in feedback.get("improvements", []):
                    st.write(f"🛠️ {x}")

                st.markdown("**句子优化示例**")
                for item in feedback.get("sentence_polish", []):
                    st.write(f"原句：{item.get('original', '')}")
                    st.write(f"建议：{item.get('better', '')}")
                    st.caption(f"原因：{item.get('reason', '')}")
                    st.divider()

                st.markdown("**补写提纲建议**")
                for x in feedback.get("outline_advice", []):
                    st.write(f"- {x}")

                st.success(feedback.get("encouragement", "继续加油！"))

        st.subheader("二次修改辅导")
        if st.button("生成修改建议", use_container_width=True):
            guidance = revise_guidance(st.session_state.get("essay_text", essay), feedback)
            st.session_state["revision_guidance"] = guidance

    guidance = st.session_state.get("revision_guidance")
    if guidance:
        st.markdown("### 修改建议")
        st.write(guidance)

    st.markdown("---")
    st.caption("开发提示：可在环境变量中设置 OPENAI_API_KEY、OPENAI_MODEL、OPENAI_BASE_URL 以接入真实模型。")


if __name__ == "__main__":
    main()
