import json
import textwrap
from typing import Any, Dict

from PIL import Image

from .config import Settings
from .content import ESSAY_TEMPLATES, GRADE_RUBRICS
from .content_en import ENGLISH_GRADE_RUBRICS, ENGLISH_TEMPLATES
from .metrics import chinese_word_count, get_rubric_markdown, paragraph_count
from .metrics_en import (
    capitalization_ratio,
    english_word_count,
    get_rubric_markdown_en,
    linking_words_found,
)
from .rate_limit import FixedWindowRateLimiter
from .uploads import image_to_model_data_url

SUBJECT_CHINESE = "chinese"
SUBJECT_ENGLISH = "english"

REQUIRED_FEEDBACK_KEYS = (
    "teacher_feedback",
    "student_feedback",
    "strengths",
    "suggestions",
    "polished_sentence",
    "outline_advice",
    "step_rewrite",
)

STEP_REWRITE_KEYS = ("先补内容", "再改句子", "参考开头", "参考结尾")


def build_prompt(grade: str, genre: str, topic: str, essay: str) -> str:
    rubric = get_rubric_markdown(grade)
    return f"""
你是一名温和、专业、懂小学生写作教学的中文作文老师。
请按照以下要求分析作文。

学生年级：{grade}
作文类型：{genre}
作文题目/主题：{topic}

该年级评价标准：
{rubric}

请输出 JSON，字段包括：
teacher_feedback, student_feedback, strengths, suggestions, polished_sentence, outline_advice, step_rewrite

其中：
- teacher_feedback：教师版点评，专业、具体、分点
- student_feedback：学生鼓励版点评，温暖、具体、易懂
- strengths：3条优点
- suggestions：3条改进建议
- polished_sentence：挑一两句原句润色示范
- outline_advice：给出更清晰的写作提纲
- step_rewrite：对象，固定包含四个键：先补内容、再改句子、参考开头、参考结尾

学生作文：
{essay}
""".strip()


def build_prompt_en(grade: str, genre: str, topic: str, essay: str) -> str:
    rubric = get_rubric_markdown_en(grade)
    return f"""
你是一名有耐心的小学英语老师，正在批改中国{grade}学生的英语作文。
请用"英文示范 + 中文讲解"的双语方式点评，让小学生和家长都能看懂。

Genre: {genre}
Topic: {topic}

该年级英语写作评价标准：
{rubric}

请输出 JSON，字段包括：
teacher_feedback, student_feedback, strengths, suggestions, polished_sentence, outline_advice, step_rewrite, grammar_corrections

其中：
- teacher_feedback：教师版点评（中文为主，引用英文原句说明问题）
- student_feedback：学生鼓励版点评（简单英文一两句 + 中文鼓励）
- strengths：3条优点（中文）
- suggestions：3条改进建议（中文，可附英文示例）
- polished_sentence：挑一两句原句给出更地道的英文改写
- outline_advice：英文提纲建议（beginning-middle-end）
- step_rewrite：对象，固定包含四个键：先补内容、再改句子、参考开头、参考结尾
- grammar_corrections：数组，每项 {{"original": 原句, "corrected": 订正后, "note": 中文说明}}，最多5条

Student essay:
{essay}
""".strip()


def fallback_feedback(grade: str, genre: str, topic: str, essay: str) -> Dict[str, Any]:
    wc = chinese_word_count(essay)
    strengths = []
    suggestions = []

    if wc > 0:
        strengths.append("能够围绕题目完成写作。")
    if paragraph_count(essay) >= 2:
        strengths.append("已经有基本的分段意识。")
    if any(x in essay for x in ["高兴", "难过", "激动", "紧张"]):
        strengths.append("能写出人物或自己的感受。")

    if wc < GRADE_RUBRICS[grade]["target_words"][0]:
        suggestions.append("字数还可以再充实一些，多补充细节。")
    if paragraph_count(essay) < 3:
        suggestions.append("建议分成开头、中间、结尾三个部分。")
    if not any(x in essay for x in ["首先", "然后", "最后", "接着", "后来"]):
        suggestions.append("可以加入表示顺序的词语，让事情发展更清楚。")

    while len(strengths) < 3:
        strengths.append("作文态度认真，主题比较明确。")
    while len(suggestions) < 3:
        suggestions.append("可以多写动作、语言、心理活动，让内容更生动。")

    return {
        "teacher_feedback": f"这篇{genre}基本围绕“{topic}”展开，完成度较好。建议继续补充典型细节，并提升段落之间的衔接。",
        "student_feedback": f"你已经把《{topic}》这个主题写出来了，真不错！如果再多写一点经过、感受和细节，这篇作文会更精彩。",
        "strengths": strengths,
        "suggestions": suggestions,
        "polished_sentence": "示例润色：把“我很开心”改成“我高兴得一路小跑，心里像开了一朵花”。",
        "outline_advice": "建议提纲：开头点题——中间写具体经过或观察到的细节——结尾写感受或收获。",
        "step_rewrite": {
            "先补内容": "补上人物动作、语言和心理活动。",
            "再改句子": "把短句补充完整，尽量写清谁在做什么。",
            "参考开头": ESSAY_TEMPLATES.get(genre, {}).get("万能开头", "开头先点明主题。"),
            "参考结尾": ESSAY_TEMPLATES.get(genre, {}).get("万能结尾", "结尾写感受或收获。"),
        },
        "grammar_corrections": [],
        "source": "fallback",
    }


def fallback_feedback_en(grade: str, genre: str, topic: str, essay: str) -> Dict[str, Any]:
    wc = english_word_count(essay)
    low, high = ENGLISH_GRADE_RUBRICS[grade]["target_words"]
    links = linking_words_found(essay)
    strengths = []
    suggestions = []

    if wc > 0:
        strengths.append(f"能用英语围绕 “{topic}” 完成写作，共写了 {wc} 个单词。")
    if links:
        strengths.append(f"会用连接词（{', '.join(links[:3])}），句子顺序清楚。")
    if capitalization_ratio(essay) >= 0.8:
        strengths.append("句首大写做得很好，书写规范。")

    if wc < low:
        suggestions.append(f"再多写几句吧，{grade}建议写到 {low}-{high} 个单词。")
    if not links:
        suggestions.append("试着用上 first / then / finally，让顺序更清楚。")
    if capitalization_ratio(essay) < 0.8:
        suggestions.append("注意每句话开头的字母要大写，句末加上标点。")

    while len(strengths) < 3:
        strengths.append("书写认真，愿意用英语表达自己的想法。")
    while len(suggestions) < 3:
        suggestions.append("可以加一两个形容词（happy, beautiful ...）让句子更生动。")

    tpl = ENGLISH_TEMPLATES.get(genre, {})
    return {
        "teacher_feedback": (
            f"这篇 {genre} 英语作文围绕 “{topic}” 展开，共 {wc} 个单词。"
            "接下来重点检查：句子是否完整（主语+动词）、时态是否一致、单词拼写是否正确。"
        ),
        "student_feedback": f"Good job! 你已经用英语写出了 “{topic}”，继续加油，多写一句就更棒了！",
        "strengths": strengths,
        "suggestions": suggestions,
        "polished_sentence": 'Example: change "I very like it" into "I like it very much."',
        "outline_advice": "Beginning: 点题一句 — Middle: 2-4 句细节 — Ending: 感受一句。",
        "step_rewrite": {
            "先补内容": "多写一两句细节：What do you see? What do they do?",
            "再改句子": "检查每句是否有主语和动词，时态是否一致。",
            "参考开头": tpl.get("万能开头", "Start with one sentence about the topic."),
            "参考结尾": tpl.get("万能结尾", "End with your feeling."),
        },
        "grammar_corrections": [],
        "source": "fallback",
    }


def fallback_image_prompts(grade: str) -> Dict[str, Any]:
    return {
        "scene": "这张图片里可能有人物、环境和正在发生的事情，适合做看图作文。",
        "observe": [
            "先说清楚图上有谁，他们在哪里。",
            "仔细看人物的动作、表情和周围环境。",
            "想一想：这件事发生前后可能有什么故事？",
            "最后写出你的感受或明白的道理。",
        ],
        "questions": [
            "谁是画面中的主角？",
            "他们在做什么？",
            "周围环境告诉了你什么信息？",
            "如果给这幅图取一个题目，你会怎么取？",
        ],
        "suggested_title": "看图作文",
        "source": "fallback",
    }


def normalize_feedback(raw: Any, fallback: Dict[str, Any]) -> Dict[str, Any]:
    """Fill missing/odd-shaped LLM fields so callers can rely on the schema.

    Guards against the deployed-B bug where step_rewrite came back as a list
    (or with unexpected keys) and the raw escaped JSON leaked into the UI.
    """
    if not isinstance(raw, dict):
        return fallback
    result = dict(raw)
    for key in REQUIRED_FEEDBACK_KEYS:
        if key not in result or result[key] in (None, "", []):
            result[key] = fallback[key]
    for key in ("strengths", "suggestions"):
        if isinstance(result[key], str):
            result[key] = [result[key]]
        elif not isinstance(result[key], list):
            result[key] = fallback[key]
    step = result["step_rewrite"]
    if isinstance(step, list):
        step = {k: str(v) for k, v in zip(STEP_REWRITE_KEYS, step)}
    if not isinstance(step, dict):
        step = fallback["step_rewrite"]
    result["step_rewrite"] = {k: str(step.get(k) or fallback["step_rewrite"][k]) for k in STEP_REWRITE_KEYS}
    corrections = result.get("grammar_corrections", [])
    result["grammar_corrections"] = corrections if isinstance(corrections, list) else []
    result["source"] = "llm"
    return result


class LLMService:
    def __init__(self, settings: Settings, limiter: FixedWindowRateLimiter | None = None):
        self.settings = settings
        self.limiter = limiter or FixedWindowRateLimiter(settings.llm_requests_per_minute)

    def essay_feedback(
        self,
        grade: str,
        genre: str,
        topic: str,
        essay: str,
        user_key: str = "anonymous",
        subject: str = SUBJECT_CHINESE,
    ) -> Dict[str, Any]:
        if subject == SUBJECT_ENGLISH:
            fallback = fallback_feedback_en(grade, genre, topic, essay)
            prompt = build_prompt_en(grade, genre, topic, essay)
            system = "你是小学英语写作辅导老师，只输出合法JSON。"
        else:
            fallback = fallback_feedback(grade, genre, topic, essay)
            prompt = build_prompt(grade, genre, topic, essay)
            system = "你是小学作文辅导老师，只输出合法JSON。"

        if not self.settings.openai_api_key or not self.limiter.allow(user_key):
            return fallback
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)
            resp = client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=0.4,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                timeout=30,
            )
            return normalize_feedback(json.loads(resp.choices[0].message.content), fallback)
        except Exception:
            return fallback

    def image_prompts(self, image: Image.Image, grade: str, user_key: str = "anonymous") -> Dict[str, Any]:
        if not self.settings.openai_api_key or not self.limiter.allow(f"image:{user_key}"):
            return fallback_image_prompts(grade)
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)
            prompt = textwrap.dedent(
                f"""
                你是一位小学作文老师。请根据图片，为{grade}学生生成看图作文辅助信息。
                输出 JSON，包含 scene、observe、questions、suggested_title。
                语言适合小学生。
                """
            ).strip()
            resp = client.chat.completions.create(
                model=self.settings.openai_model,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "你是小学作文辅导老师，只输出合法JSON。"},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_to_model_data_url(image, self.settings)}},
                        ],
                    },
                ],
                timeout=30,
            )
            data = json.loads(resp.choices[0].message.content)
            if isinstance(data, dict):
                data.setdefault("suggested_title", "看图作文")
                data["source"] = "llm"
                return data
            return fallback_image_prompts(grade)
        except Exception:
            return fallback_image_prompts(grade)
