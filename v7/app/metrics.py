import re
from typing import List

from .content import DEFAULT_TOPICS, ESSAY_TEMPLATES, GRADE_RUBRICS


def chinese_word_count(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def paragraph_count(text: str) -> int:
    return len([p.strip() for p in text.splitlines() if p.strip()])


def sentence_count(text: str) -> int:
    if not text:
        return 0
    sentences = [s for s in re.split(r"[。！？.!?]+", text) if s.strip()]
    return max(len(sentences), 1)


def has_beginning_middle_end(text: str) -> bool:
    return paragraph_count(text) >= 3 or sentence_count(text) >= 5


def structure_level(text: str) -> str:
    para_count = paragraph_count(text)
    sent_count = sentence_count(text)
    if para_count >= 3 and sent_count >= 6:
        return "较完整"
    if para_count >= 2 or sent_count >= 4:
        return "基本完整"
    return "待加强"


def expression_level(text: str) -> str:
    wc = chinese_word_count(text)
    if wc >= 200:
        return "较丰富"
    if wc >= 100:
        return "一般"
    return "待丰富"


def infer_structure_score(text: str) -> int:
    wc = chinese_word_count(text)
    score = 60
    if wc >= 180:
        score += 10
    if wc >= 300:
        score += 10
    if paragraph_count(text) >= 3:
        score += 10
    if any(x in text for x in ["首先", "然后", "接着", "最后", "后来", "终于"]):
        score += 10
    return min(score, 100)


def infer_expression_score(text: str) -> int:
    score = 60
    if any(x in text for x in ["像", "仿佛", "好像", "犹如"]):
        score += 10
    if any(x in text for x in ["高兴", "难过", "激动", "紧张", "惊讶", "温暖"]):
        score += 10
    if chinese_word_count(text) >= 250:
        score += 10
    if any(x in text for x in ["！", "？", "……"]):
        score += 10
    return min(score, 100)


def grade_expectation(grade: str) -> str:
    low, high = GRADE_RUBRICS[grade]["target_words"]
    return f"建议字数：{low}-{high} 字"


def get_rubric_markdown(grade: str) -> str:
    return "\n".join([f"- **{k}**：{v}" for k, v in GRADE_RUBRICS[grade]["rubric"]])


def generate_topics(grade: str, genre: str, keyword: str = "") -> List[str]:
    base = DEFAULT_TOPICS.get(genre, []).copy()
    if keyword:
        base = [f"{keyword}：{t}" for t in base[:3]] + [f"围绕“{keyword}”自拟题目"]
    if grade in ["五年级", "六年级"]:
        base += [f"我眼中的{keyword or '成长'}", f"一次关于{keyword or '勇气'}的思考"]
    return base[:6]


def compare_with_model_essay(student_text: str, genre: str, topic: str) -> str:
    tpl = ESSAY_TEMPLATES.get(genre, {})
    return (
        f"范文对比提示：优秀{genre}通常会有更清晰的结构（{' / '.join(tpl.get('结构', []))}）。\n"
        "对照你的作文，可以重点检查：\n"
        "1. 开头是否点题；\n2. 中间是否有足够细节；\n3. 结尾是否表达感受；\n"
        "4. 是否用了表示顺序或描写感受的词语。"
    )

