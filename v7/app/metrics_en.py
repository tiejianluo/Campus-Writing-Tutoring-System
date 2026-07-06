"""Local heuristic scoring for elementary English writing (LLM fallback)."""

import re
from typing import List

from .content_en import (
    ENGLISH_EXPRESSION_WORDS,
    ENGLISH_GRADE_RUBRICS,
    ENGLISH_LINKING_WORDS,
    ENGLISH_TOPICS,
)


def english_word_count(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text))


def english_sentence_count(text: str) -> int:
    if not text:
        return 0
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    return max(len(sentences), 1)


def capitalization_ratio(text: str) -> float:
    """Share of sentences that start with a capital letter."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if not sentences:
        return 0.0
    good = sum(1 for s in sentences if s[0].isupper())
    return good / len(sentences)


def linking_words_found(text: str) -> List[str]:
    words = set(re.findall(r"[a-z]+", text.lower()))
    return [w for w in ENGLISH_LINKING_WORDS if w in words]


def vocabulary_variety(text: str) -> float:
    words = re.findall(r"[a-z]+", text.lower())
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def infer_structure_score_en(text: str, grade: str) -> int:
    rubric = ENGLISH_GRADE_RUBRICS.get(grade, ENGLISH_GRADE_RUBRICS["三年级"])
    low, high = rubric["target_words"]
    wc = english_word_count(text)
    score = 60
    if wc >= low:
        score += 10
    if wc >= high:
        score += 5
    if english_sentence_count(text) >= 4:
        score += 10
    links = linking_words_found(text)
    if len(links) >= 3:
        score += 15
    elif len(links) >= 1:
        score += 8
    return min(score, 100)


def infer_expression_score_en(text: str, grade: str) -> int:
    score = 60
    lower_words = set(re.findall(r"[a-z]+", text.lower()))
    hits = [w for w in ENGLISH_EXPRESSION_WORDS if w in lower_words]
    if len(hits) >= 2:
        score += 15
    elif len(hits) >= 1:
        score += 8
    if capitalization_ratio(text) >= 0.8:
        score += 10
    if vocabulary_variety(text) >= 0.6:
        score += 10
    if any(p in text for p in ["!", "?"]):
        score += 5
    return min(score, 100)


def grade_expectation_en(grade: str) -> str:
    low, high = ENGLISH_GRADE_RUBRICS[grade]["target_words"]
    return f"Suggested length: {low}-{high} words（建议 {low}-{high} 个单词）"


def get_rubric_markdown_en(grade: str) -> str:
    return "\n".join([f"- **{k}**：{v}" for k, v in ENGLISH_GRADE_RUBRICS[grade]["rubric"]])


def generate_topics_en(grade: str, genre: str) -> List[str]:
    return ENGLISH_TOPICS.get(genre, ["My Happy Day"])[:6]
