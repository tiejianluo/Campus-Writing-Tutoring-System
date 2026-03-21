import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app import (
    count_chinese_chars,
    fallback_feedback,
    build_user_prompt,
    make_revision_prompt,
    revise_guidance,
    GRADE_OPTIONS,
    GENRE_OPTIONS,
    THEME_OPTIONS,
    RUBRIC,
    JSON_SCHEMA_HINT
)


class TestBasicFunctions(unittest.TestCase):
    """测试基础功能函数"""
    
    def test_count_chinese_chars(self):
        """测试中文字符计数功能"""
        self.assertEqual(count_chinese_chars(""), 0)
        self.assertEqual(count_chinese_chars("你好"), 2)
        self.assertEqual(count_chinese_chars("Hello 世界"), 2)
        self.assertEqual(count_chinese_chars("今天天气真好！"), 6)
        self.assertEqual(count_chinese_chars("123中文abc"), 2)
    
    def test_count_chinese_chars_with_special_chars(self):
        """测试包含特殊字符的中文字符计数"""
        text = "这是一篇作文！包含标点符号，数字123，字母abc。"
        self.assertEqual(count_chinese_chars(text), 13)
    
    def test_fallback_feedback_structure(self):
        """测试回退反馈的结构完整性"""
        feedback = fallback_feedback("这是一篇简单的作文。")
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        self.assertIn("sentence_polish", feedback)
        self.assertIn("outline_advice", feedback)
        self.assertIn("encouragement", feedback)
    
    def test_fallback_feedback_short_essay(self):
        """测试短作文的回退反馈"""
        short_essay = "很短。"
        feedback = fallback_feedback(short_essay)
        self.assertIn("篇幅偏短", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 5)
    
    def test_fallback_feedback_normal_essay(self):
        """测试正常长度作文的回退反馈"""
        normal_essay = "这是一篇正常长度的作文。今天天气很好，我和同学们一起去公园玩。我们玩了很多游戏，非常开心。"
        feedback = fallback_feedback(normal_essay)
        self.assertIn("完整主题", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 6)
    
    def test_build_user_prompt_structure(self):
        """测试用户提示构建的结构"""
        prompt = build_user_prompt("三年级", "记叙文", "难忘的一天", 300, "作文内容")
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：记叙文", prompt)
        self.assertIn("主题：难忘的一天", prompt)
        self.assertIn("目标字数：300", prompt)
        self.assertIn("作文内容", prompt)
    
    def test_make_revision_prompt(self):
        """测试修改提示构建"""
        feedback = {
            "strengths": ["优点1", "优点2"],
            "improvements": ["改进1", "改进2"]
        }
        essay = "测试作文"
        prompt = make_revision_prompt(essay, feedback)
        self.assertIn("测试作文", prompt)
        self.assertIn("优点1", prompt)
        self.assertIn("改进1", prompt)
    
    def test_revise_guidance_fallback(self):
        """测试修改指导的回退功能"""
        feedback = {"strengths": [], "improvements": []}
        guidance = revise_guidance("测试作文", feedback)
        self.assertIn("可以先补充", guidance)
        self.assertIn("可以改写", guidance)
        self.assertIn("参考开头", guidance)
    
    def test_constants_validation(self):
        """测试常量定义的有效性"""
        self.assertIsInstance(GRADE_OPTIONS, list)
        self.assertIsInstance(GENRE_OPTIONS, list)
        self.assertIsInstance(THEME_OPTIONS, list)
        self.assertIsInstance(RUBRIC, dict)
        self.assertIsInstance(JSON_SCHEMA_HINT, dict)
        
        self.assertTrue(len(GRADE_OPTIONS) > 0)
        self.assertTrue(len(GENRE_OPTIONS) > 0)
        self.assertTrue(len(THEME_OPTIONS) > 0)
        self.assertTrue(len(RUBRIC) > 0)


if __name__ == '__main__':
    unittest.main()