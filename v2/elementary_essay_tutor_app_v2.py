import os
import json
import base64
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import streamlit as st
from PIL import Image

try:
    import pandas as pd
except Exception:
    pd = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

APP_TITLE = "妙妙作文屋·校园版"
APP_SUBTITLE = "看图作文、题目生成、分步改写、成长记录，一站式完成"
DATA_PATH = Path("essay_app_records.json")

GRADE_OPTIONS = ["三年级", "四年级", "五年级", "六年级"]
GENRE_OPTIONS = ["写人", "写事", "写景", "想象作文", "读后感", "日记", "看图作文"]
DEFAULT_TOPICS = [
    "难忘的一天", "我的好朋友", "秋天来了", "校园一角", "我学会了____", "一次有趣的活动",
    "一件让我感动的事", "我的家人", "我的理想", "我最喜欢的小动物"
]

GRADE_RUBRICS = {
    "三年级": {
        "审题与内容": "是否围绕题目写，内容真实具体，能把事情写清楚。",
        "结构与顺序": "是否有开头、经过、结尾，顺序是否清楚。",
        "句子表达": "句子是否通顺，词语是否恰当。",
        "细节描写": "能否写出动作、语言、看到的画面。",
        "书写规范": "标点、错别字、重复表达是否较少。",
    },
    "六年级": {
        "审题与立意": "是否准确回应题目，中心是否明确，有没有自己的思考。",
        "结构与层次": "是否有清晰结构，段落推进是否自然，详略是否得当。",
        "语言与表达": "用词是否准确，句式是否有变化，表达是否有感染力。",
        "细节与描写": "是否能用动作、语言、心理、环境等细节支撑中心。",
        "规范与修改": "标点、病句、重复、错别字控制情况及整体完成度。",
    },
}

GRADE_WORDS = {
    "三年级": (150, 300),
    "四年级": (250, 400),
    "五年级": (350, 550),
    "六年级": (450, 700),
}

TEMPLATES = {
    "写人": {
        "框架": ["开头：介绍人物是谁，与我的关系", "中间：选2-3件事写人物特点", "结尾：表达我的感受"],
        "句式": ["他一……就……", "最让我难忘的是……", "从这件事里，我看到了……"],
    },
    "写事": {
        "框架": ["开头：交代时间、地点、人物", "中间：按照起因—经过—结果写", "结尾：写感受或收获"],
        "句式": ["事情是这样开始的……", "我先……接着……最后……", "这件事让我明白了……"],
    },
    "写景": {
        "框架": ["开头：点明写的是哪里、什么时候的景色", "中间：按方位或时间顺序描写", "结尾：抒发喜爱之情"],
        "句式": ["远远望去……", "走近一看……", "我仿佛走进了……"],
    },
    "想象作文": {
        "框架": ["开头：提出奇妙设定", "中间：写发生了什么新鲜故事", "结尾：点出启发或愿望"],
        "句式": ["假如我能……", "忽然，奇妙的事情发生了……", "原来，想象的世界……"],
    },
    "读后感": {
        "框架": ["开头：写读了什么", "中间：概括主要内容+最打动我的地方", "结尾：联系自己谈感受"],
        "句式": ["读完这篇文章，我最难忘的是……", "它让我想到……", "以后我也要……"],
    },
    "日记": {
        "框架": ["开头：日期、天气、心情", "中间：写当天最重要的一件事", "结尾：写自己的感受"],
        "句式": ["今天，我……", "让我印象最深的是……", "我觉得今天……"],
    },
    "看图作文": {
        "框架": ["开头：交代图上是谁、在哪里", "中间：按看到的顺序描述画面并想象发生的事", "结尾：写感受或启示"],
        "句式": ["画面中……", "我猜他们正在……", "看到这一幕，我觉得……"],
    },
}

SAMPLE_ESSAYS = {
    "写人": "我的奶奶虽然个子不高，却总是很精神。每天早上，她都会早早起床给我做早餐。一次我生病了，奶奶一直守在我身边，给我量体温、喂我喝水。我看到她忙来忙去，心里特别感动。我觉得奶奶是家里最温暖的人。",
    "写事": "上周六，我们班举行了跳绳比赛。刚开始时，我很紧张，手心都出汗了。轮到我上场时，我深吸一口气，努力让自己平静下来。随着哨声响起，我飞快地跳了起来。虽然最后没有拿第一名，但我明白了只要勇敢面对，就有进步。",
    "写景": "秋天的校园真美。操场边的银杏树像撑开的一把把金色小伞，风一吹，叶子轻轻落下来，像一只只蝴蝶在飞。花坛里的菊花开得正热闹，有黄的、白的、紫的，把校园装扮得五彩缤纷。",
    "想象作文": "假如我有一支神奇的画笔，我想先画一双会飞的翅膀。这样我就能飞到大山、海边和森林，看一看世界的样子。我还想画很多书和玩具送给山区的小朋友，让大家都能快乐学习。",
}

SYSTEM_PROMPT = """
你是一位耐心、温和、擅长启发式教学的小学作文老师。
请面向中国小学生输出内容。
要求：
1. 语言简单，鼓励性强。
2. 先说优点，再说可操作的修改建议。
3. 不要直接全篇代写，优先引导学生自己修改。
4. 输出必须是合法 JSON。
""".strip()


def get_client():
    if OpenAI is None:
        return None
    key = "sk-bGelDOkVt64HBKNhMtgxI3v2Au04hsjohTykYSWUef0mape9"
    kwargs = {"api_key": key}
    base = "https://4.0.wokaai.com/v1/"
    if base:
        kwargs["base_url"] = base
    return OpenAI(**kwargs)


def rubric_for_grade(grade: str) -> Dict[str, str]:
    if grade in GRADE_RUBRICS:
        return GRADE_RUBRICS[grade]
    return GRADE_RUBRICS["六年级"] if grade == "六年级" else GRADE_RUBRICS["三年级"]


def score_keys(grade: str) -> List[str]:
    return list(rubric_for_grade(grade).keys())


def count_chinese_chars(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def paragraph_count(text: str) -> int:
    return len([p for p in text.splitlines() if p.strip()]) or 1


def sentence_count(text: str) -> int:
    pieces = []
    for sep in ["。", "！", "？", ".", "!", "?"]:
        text = text.replace(sep, "|")
    pieces = [x for x in text.split("|") if x.strip()]
    return len(pieces) or 1


def has_beginning_middle_end(text: str) -> bool:
    return paragraph_count(text) >= 3 or sentence_count(text) >= 5


def text_to_data_url(img: Image.Image) -> str:
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def default_topics(grade: str, genre: str) -> List[str]:
    genre_map = {
        "写人": ["我的妈妈", "我的老师", "我最敬佩的人", "我的同桌"],
        "写事": ["一次难忘的活动", "我学会了骑自行车", "那次我真开心", "一件让我后悔的事"],
        "写景": ["校园的春天", "雨后的公园", "家乡的秋天", "窗外的风景"],
        "想象作文": ["假如我会飞", "假如我有一台时光机", "未来的学校", "会说话的书包"],
        "读后感": ["读《小王子》有感", "读寓言后的想法", "一本让我喜欢的书"],
        "日记": ["周末的一天", "今天最开心的事", "一次特别的值日"],
        "看图作文": ["图片观察作文", "根据图片编故事", "看图写话"],
    }
    return genre_map.get(genre, DEFAULT_TOPICS)


def generate_topic_options(grade: str, genre: str, interest: str = "") -> List[str]:
    base = default_topics(grade, genre)
    if interest:
        base = [f"{interest}里的故事", f"关于{interest}的一天"] + base
    return base[:8]


def fallback_image_prompts(grade: str) -> Dict[str, Any]:
    return {
        "scene": "这张图片里可能有人物、环境和正在发生的事情，适合做看图作文。",
        "observe": [
            "先说清楚图上有谁，他们在哪里。",
            "仔细看人物的动作、表情和周围环境。",
            "想一想：这件事发生前后可能有什么故事？",
            "最后写出你的感受或明白的道理。"
        ],
        "questions": [
            "谁是画面中的主角？",
            "他们在做什么？",
            "周围环境告诉了你什么信息？",
            "如果给这幅图取一个题目，你会怎么取？"
        ],
        "suggested_title": "看图写话：发生了什么事"
    }


def vision_observation_prompts(image: Image.Image, grade: str) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return fallback_image_prompts(grade)
    model = "gpt-4.1-2025-04-14"
    prompt = textwrap.dedent(f"""
    你是一位小学作文老师。请根据图片，为{grade}学生生成看图作文辅助信息。
    只输出 JSON，键包括：scene, observe, questions, suggested_title。
    observe 给4条观察提示；questions 给4条启发问题；语言适合小学生。
    """).strip()
    try:
        data_url = text_to_data_url(image)
        resp = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}}
                ]}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return fallback_image_prompts(grade)


def fallback_feedback(grade: str, genre: str, essay: str) -> Dict[str, Any]:
    keys = score_keys(grade)
    scores = {k: v for k, v in zip(keys, [7, 6, 7, 6, 8])}
    n = count_chinese_chars(essay)
    too_short = n < GRADE_WORDS.get(grade, (200, 400))[0]
    summary = "这篇作文有明确主题，能看出你想表达的重点。" if not too_short else "这篇作文有主题，但内容还不够展开，可以写得更具体。"
    strengths = [
        "能围绕主题写，不容易跑题。",
        "句子基本通顺，读起来比较顺。",
        "能写出自己的想法，有真实感。"
    ]
    improvements = [
        "可以补充时间、地点、人物，让事情更完整。",
        "可以多写动作、语言或心理活动，让画面更生动。",
        "结尾可以写出自己的感受或收获，让中心更清楚。"
    ]
    teacher = "优点是主题明确、语言自然。建议重点补充经过和细节描写，提升内容完整性与表现力。"
    child = "你已经写出了自己的想法，再多写一点细节，这篇作文会更精彩！"
    return {
        "summary": summary,
        "scores": scores,
        "strengths": strengths,
        "improvements": improvements,
        "teacher_feedback": teacher,
        "encouraging_feedback": child,
        "sentence_polish": [
            {"original": "我很开心。", "better": "我高兴得嘴角一直上扬，心里像开了一朵花。", "reason": "把感受写具体，会更生动。"},
            {"original": "事情结束了。", "better": "事情终于结束了，我长长地松了一口气。", "reason": "补充动作，画面会更清楚。"}
        ],
        "outline_advice": [
            "先交代事情发生的时间、地点和人物。",
            "按顺序写清楚起因、经过和结果。",
            "补充一两处细节描写。",
            "最后写感受或收获。"
        ],
        "revision_steps": [
            "先给作文补上事情发生的时间和地点。",
            "把中间最重要的一幕写详细。",
            "结尾写出你的心情变化。"
        ]
    }


def build_feedback_prompt(grade: str, genre: str, theme: str, essay: str) -> str:
    rubric = rubric_for_grade(grade)
    rubric_text = "\n".join([f"- {k}: {v}" for k, v in rubric.items()])
    return textwrap.dedent(f"""
    请以小学作文老师的身份，分析下面这篇作文，并只输出 JSON。
    学生年级：{grade}
    作文类型：{genre}
    主题：{theme}

    评分维度：
    {rubric_text}

    JSON 必须包含以下键：
    summary, scores, strengths, improvements, teacher_feedback, encouraging_feedback,
    sentence_polish, outline_advice, revision_steps

    要求：
    1. scores 的键必须与评分维度完全一致，分值 1-10。
    2. strengths 至少3条，improvements 至少3条。
    3. teacher_feedback 用较正式、清楚的老师口吻。
    4. encouraging_feedback 用鼓励小学生的口吻。
    5. sentence_polish 给2-4条原句优化建议。
    6. revision_steps 给3条分步修改建议。

    学生作文：
    {essay}
    """).strip()


def call_feedback_llm(grade: str, genre: str, theme: str, essay: str) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return fallback_feedback(grade, genre, essay)
    try:
        model = "gpt-4.1-2025-04-14"
        resp = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_feedback_prompt(grade, genre, theme, essay)}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return fallback_feedback(grade, genre, essay)


def build_compare_prompt(grade: str, genre: str, essay: str, sample: str) -> str:
    return textwrap.dedent(f"""
    你是小学作文老师。请把学生作文和范文进行对比，只输出 JSON。
    键包括：common_strengths, missing_parts, imitation_points。
    学生年级：{grade}
    作文类型：{genre}

    学生作文：{essay}
    范文：{sample}
    """).strip()


def fallback_compare(essay: str, sample: str) -> Dict[str, Any]:
    return {
        "common_strengths": ["都有明确主题", "都能围绕一件事或一个对象展开"],
        "missing_parts": ["学生作文的细节描写还不够", "段落层次还可以更清楚", "结尾感受可以更突出"],
        "imitation_points": ["学习范文怎样写动作和表情", "学习范文怎样用一句话点明感受", "学习范文的开头点题方式"]
    }


def compare_with_sample(grade: str, genre: str, essay: str, sample: str) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return fallback_compare(essay, sample)
    try:
        model = "gpt-4.1-2025-04-14"
        resp = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_compare_prompt(grade, genre, essay, sample)}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return fallback_compare(essay, sample)


def stepwise_rewrite_prompt(grade: str, essay: str, feedback: Dict[str, Any]) -> str:
    return textwrap.dedent(f"""
    你是一位小学作文老师。请根据作文和点评，输出分步改写建议。
    只输出 JSON，键包括：step1_add, step2_rewrite, step3_opening, step4_ending。
    学生年级：{grade}
    作文：{essay}
    点评：{json.dumps(feedback, ensure_ascii=False)}
    """).strip()


def fallback_stepwise() -> Dict[str, Any]:
    return {
        "step1_add": ["补充事情发生的时间和地点", "写清楚谁做了什么"],
        "step2_rewrite": ["把“很开心”改成动作和表情描写", "把“很难忘”改成具体原因"],
        "step3_opening": "那天发生的一件事，让我到现在想起来还印象很深。",
        "step4_ending": "通过这件事，我明白了只要认真去做，就一定会有收获。"
    }


def stepwise_rewrite(grade: str, essay: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
    client = get_client()
    if client is None:
        return fallback_stepwise()
    try:
        model = "gpt-4.1-2025-04-14"
        resp = client.chat.completions.create(
            model=model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": stepwise_rewrite_prompt(grade, essay, feedback)}
            ]
        )
        return json.loads(resp.choices[0].message.content)
    except Exception:
        return fallback_stepwise()


def generate_titles(grade: str, genre: str, keyword: str) -> List[str]:
    base = generate_topic_options(grade, genre, keyword)
    if keyword:
        return [f"{keyword}里的小故事", f"我和{keyword}", f"一次关于{keyword}的经历"] + base[:5]
    return base


def structure_level(text: str) -> str:
    pc = paragraph_count(text)
    sc = sentence_count(text)
    if pc >= 3 and sc >= 6:
        return "较完整"
    if sc >= 4:
        return "基本完整"
    return "待加强"


def expression_level(text: str) -> str:
    markers = ["好像", "仿佛", "像", "忽然", "于是", "不仅", "还", "心里", "说", "笑"]
    score = sum(1 for m in markers if m in text)
    if score >= 5:
        return "较丰富"
    if score >= 2:
        return "一般"
    return "待丰富"


def load_records() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_records(records: List[Dict[str, Any]]):
    DATA_PATH.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def append_record(record: Dict[str, Any]):
    records = load_records()
    records.append(record)
    save_records(records)


def student_records(student: str) -> List[Dict[str, Any]]:
    return [r for r in load_records() if r.get("student_name") == student]


def summarize_growth(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"count": 0}
    word_counts = [r.get("word_count", 0) for r in records]
    structure_scores = [r.get("structure_score", 0) for r in records]
    language_scores = [r.get("language_score", 0) for r in records]
    return {
        "count": len(records),
        "avg_words": round(sum(word_counts) / len(word_counts), 1),
        "avg_structure": round(sum(structure_scores) / len(structure_scores), 2),
        "avg_language": round(sum(language_scores) / len(language_scores), 2),
        "word_counts": word_counts,
        "structure_scores": structure_scores,
        "language_scores": language_scores,
        "dates": [r.get("timestamp", "")[:10] for r in records],
    }


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="✏️", layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    with st.sidebar:
        st.header("学生信息")
        student_name = st.text_input("学生姓名", value="小明")
        grade = st.selectbox("年级", GRADE_OPTIONS, index=0)
        genre = st.selectbox("作文类型", GENRE_OPTIONS, index=0)
        interest = st.text_input("兴趣关键词（可选）", value="")
        topic_choices = generate_topic_options(grade, genre, interest)
        theme = st.selectbox("作文主题", topic_choices, index=0)
        min_w, max_w = GRADE_WORDS.get(grade, (200, 400))
        target_words = st.slider("目标字数", min_w, max_w, int((min_w + max_w) / 2), step=25)
        st.info("未配置大模型 API 时，应用会用内置逻辑和示例反馈继续运行。")

    tabs = st.tabs([
        "写作文",
        "看图作文",
        "题目生成",
        "模板库",
        "范文对比",
        "分步改写",
        "成长档案",
        "家长/老师视图",
    ])

    if "last_feedback" not in st.session_state:
        st.session_state.last_feedback = None
    if "last_essay" not in st.session_state:
        st.session_state.last_essay = ""
    if "last_theme" not in st.session_state:
        st.session_state.last_theme = theme

    # 写作文
    with tabs[0]:
        st.subheader("作文创作与点评")
        col1, col2 = st.columns([1.1, 1])
        with col1:
            st.markdown("### 本年级评分标准")
            rubric = rubric_for_grade(grade)
            for k, v in rubric.items():
                st.markdown(f"- **{k}**：{v}")
            essay = st.text_area("请输入作文", height=320, placeholder="请在这里写作文……")
            st.caption(f"当前字数：{count_chinese_chars(essay)} / 目标 {target_words}")
            run = st.button("开始点评", type="primary")
        with col2:
            st.markdown("### 本类型模板")
            tpl = TEMPLATES.get(genre, {})
            if tpl:
                st.markdown("**写作框架**")
                for x in tpl.get("框架", []):
                    st.write(f"- {x}")
                st.markdown("**可借鉴句式**")
                for x in tpl.get("句式", []):
                    st.write(f"- {x}")

        if run and essay.strip():
            feedback = call_feedback_llm(grade, genre, theme, essay)
            st.session_state.last_feedback = feedback
            st.session_state.last_essay = essay
            st.session_state.last_theme = theme

            keys = score_keys(grade)
            scores = feedback.get("scores", {})
            cols = st.columns(len(keys))
            for i, k in enumerate(keys):
                cols[i].metric(k, scores.get(k, 0))

            st.markdown("### 总评")
            st.write(feedback.get("summary", ""))

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 学生鼓励版")
                st.success(feedback.get("encouraging_feedback", ""))
                st.markdown("### 优点")
                for x in feedback.get("strengths", []):
                    st.write(f"- {x}")
            with c2:
                st.markdown("### 教师点评版")
                st.info(feedback.get("teacher_feedback", ""))
                st.markdown("### 改进建议")
                for x in feedback.get("improvements", []):
                    st.write(f"- {x}")

            st.markdown("### 句子润色")
            for item in feedback.get("sentence_polish", []):
                if isinstance(item, dict):
                    st.write(f"原句：{item.get('original','')}")
                    st.write(f"建议：{item.get('better','')}")
                    st.caption(f"原因：{item.get('reason','')}")
                    st.divider()

            st.markdown("### 补写提纲")
            for x in feedback.get("outline_advice", []):
                st.write(f"- {x}")

            record = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "student_name": student_name,
                "grade": grade,
                "genre": genre,
                "theme": theme,
                "word_count": count_chinese_chars(essay),
                "paragraph_count": paragraph_count(essay),
                "structure_level": structure_level(essay),
                "expression_level": expression_level(essay),
                "scores": scores,
                "structure_score": scores.get(keys[1], 0) if len(keys) > 1 else 0,
                "language_score": scores.get(keys[2], 0) if len(keys) > 2 else 0,
                "summary": feedback.get("summary", ""),
            }
            append_record(record)
            st.success("本次练习已写入成长档案。")

    # 看图作文
    with tabs[1]:
        st.subheader("看图作文：上传图片，生成观察提示")
        img_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"], key="img_upload")
        if img_file:
            image = Image.open(img_file).convert("RGB")
            st.image(image, caption="上传的图片", use_container_width=True)
            if st.button("生成观察提示"):
                obs = vision_observation_prompts(image, grade)
                st.markdown("### 场景概括")
                st.write(obs.get("scene", ""))
                st.markdown("### 观察提示")
                for x in obs.get("observe", []):
                    st.write(f"- {x}")
                st.markdown("### 启发问题")
                for x in obs.get("questions", []):
                    st.write(f"- {x}")
                st.markdown("### 推荐题目")
                st.write(obs.get("suggested_title", ""))

    # 题目生成
    with tabs[2]:
        st.subheader("题目生成")
        keyword = st.text_input("输入一个关键词，比如：春天、足球、奶奶、校园")
        if st.button("生成作文题目"):
            for t in generate_titles(grade, genre, keyword):
                st.write(f"- {t}")

    # 模板库
    with tabs[3]:
        st.subheader("作文模板库")
        for g, tpl in TEMPLATES.items():
            with st.expander(g):
                st.markdown("**写作框架**")
                for x in tpl.get("框架", []):
                    st.write(f"- {x}")
                st.markdown("**可借鉴句式**")
                for x in tpl.get("句式", []):
                    st.write(f"- {x}")

    # 范文对比
    with tabs[4]:
        st.subheader("范文对比")
        sample = SAMPLE_ESSAYS.get(genre, next(iter(SAMPLE_ESSAYS.values())))
        st.markdown("### 范文示例")
        st.info(sample)
        compare_text = st.text_area("粘贴学生作文进行对比", value=st.session_state.last_essay, height=220, key="compare_essay")
        if st.button("开始范文对比") and compare_text.strip():
            comp = compare_with_sample(grade, genre, compare_text, sample)
            st.markdown("### 共同优点")
            for x in comp.get("common_strengths", []):
                st.write(f"- {x}")
            st.markdown("### 还缺什么")
            for x in comp.get("missing_parts", []):
                st.write(f"- {x}")
            st.markdown("### 可以模仿什么")
            for x in comp.get("imitation_points", []):
                st.write(f"- {x}")

    # 分步改写
    with tabs[5]:
        st.subheader("分步改写")
        base_essay = st.text_area("待修改作文", value=st.session_state.last_essay, height=240, key="rewrite_text")
        if st.button("生成分步改写建议") and base_essay.strip():
            feedback = st.session_state.last_feedback or fallback_feedback(grade, genre, base_essay)
            rewrite = stepwise_rewrite(grade, base_essay, feedback)
            st.markdown("### 第一步：先补内容")
            for x in rewrite.get("step1_add", []):
                st.write(f"- {x}")
            st.markdown("### 第二步：改句子")
            for x in rewrite.get("step2_rewrite", []):
                st.write(f"- {x}")
            st.markdown("### 第三步：参考开头")
            st.info(rewrite.get("step3_opening", ""))
            st.markdown("### 第四步：参考结尾")
            st.success(rewrite.get("step4_ending", ""))

    # 成长档案
    with tabs[6]:
        st.subheader("学生成长档案")
        records = student_records(student_name)
        summary = summarize_growth(records)
        if summary.get("count", 0) == 0:
            st.warning("还没有练习记录。先在“写作文”里完成一次点评吧。")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("练习次数", summary["count"])
            c2.metric("平均字数", summary["avg_words"])
            c3.metric("平均结构分", summary["avg_structure"])
            c4.metric("平均表达分", summary["avg_language"])

            st.markdown("### 发展趋势")
            chart_data = {
                "字数": summary["word_counts"],
                "结构分": summary["structure_scores"],
                "表达分": summary["language_scores"],
            }
            st.line_chart(chart_data)

            st.markdown("### 历次记录")
            if pd is not None:
                df = pd.DataFrame(records)
                show_cols = [c for c in ["timestamp", "grade", "genre", "theme", "word_count", "structure_level", "expression_level", "summary"] if c in df.columns]
                st.dataframe(df[show_cols], use_container_width=True)
            else:
                st.json(records)

    # 家长/老师视图
    with tabs[7]:
        st.subheader("家长 / 老师视图")
        records = student_records(student_name)
        if not records:
            st.info("暂无记录。")
        else:
            latest = records[-1]
            st.markdown("### 最近一次练习")
            st.write(f"时间：{latest.get('timestamp','')}")
            st.write(f"主题：{latest.get('theme','')}")
            st.write(f"字数：{latest.get('word_count',0)}")
            st.write(f"结构水平：{latest.get('structure_level','')}")
            st.write(f"表达水平：{latest.get('expression_level','')}")
            st.write(f"教师摘要：{latest.get('summary','')}")
            st.markdown("### 建议关注")
            if latest.get("word_count", 0) < target_words:
                st.write("- 可继续鼓励孩子把事情写完整，尤其是经过部分。")
            if latest.get("structure_score", 0) < 7:
                st.write("- 重点训练开头、经过、结尾的结构意识。")
            if latest.get("language_score", 0) < 7:
                st.write("- 多做句子扩写和细节描写练习。")
            st.markdown("### 使用建议")
            st.write("- 家长版：先肯定优点，再挑一条建议陪孩子修改。")
            st.write("- 老师版：可结合本周作文主题布置二次修改任务。")


if __name__ == "__main__":
    main()
