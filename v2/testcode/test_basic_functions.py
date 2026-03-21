import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    count_chinese_chars,
    paragraph_count,
    sentence_count,
    has_beginning_middle_end,
    rubric_for_grade,
    score_keys,
    default_topics,
    generate_topic_options,
    GRADE_OPTIONS,
    GENRE_OPTIONS,
    DEFAULT_TOPICS,
    GRADE_RUBRICS,
    GRADE_WORDS,
    TEMPLATES,
    SAMPLE_ESSAYS
)


class TestBasicFunctions(unittest.TestCase):
    """测试基础功能函数（继承自v1版本的测试并扩展）"""
    
    def test_count_chinese_chars(self):
        """测试中文字符计数功能（v1版本功能）"""
        self.assertEqual(count_chinese_chars(""), 0)
        self.assertEqual(count_chinese_chars("你好"), 2)
        self.assertEqual(count_chinese_chars("Hello 世界"), 2)
        self.assertEqual(count_chinese_chars("今天天气真好！"), 6)
        self.assertEqual(count_chinese_chars("123中文abc"), 2)
    
    def test_paragraph_count(self):
        """测试段落计数功能（v2版本新增）"""
        self.assertEqual(paragraph_count(""), 1)
        self.assertEqual(paragraph_count("一行文字"), 1)
        self.assertEqual(paragraph_count("第一段\n第二段"), 2)
        self.assertEqual(paragraph_count("第一段\n\n第三段"), 2)
        self.assertEqual(paragraph_count("第一段\n第二段\n第三段"), 3)
    
    def test_sentence_count(self):
        """测试句子计数功能（v2版本新增）"""
        self.assertEqual(sentence_count(""), 1)
        self.assertEqual(sentence_count("一句话。"), 1)
        self.assertEqual(sentence_count("一句话。两句话！"), 2)
        self.assertEqual(sentence_count("一句话。两句话！三句话？"), 3)
        self.assertEqual(sentence_count("一句话.两句话!三句话?"), 3)
    
    def test_has_beginning_middle_end(self):
        """测试是否有开头、中间、结尾结构（v2版本新增）"""
        self.assertTrue(has_beginning_middle_end("第一段\n第二段\n第三段"))
        self.assertTrue(has_beginning_middle_end("第一句。第二句。第三句。第四句。第五句。"))
        self.assertFalse(has_beginning_middle_end("只有一段"))
        self.assertFalse(has_beginning_middle_end("第一句。第二句。第三句。"))
    
    def test_rubric_for_grade(self):
        """测试按年级获取评分标准（v2版本新增）"""
        rubric = rubric_for_grade("三年级")
        self.assertIsInstance(rubric, dict)
        self.assertEqual(len(rubric), 5)
        
        rubric = rubric_for_grade("六年级")
        self.assertIsInstance(rubric, dict)
        self.assertEqual(len(rubric), 5)
        
        rubric = rubric_for_grade("四年级")
        self.assertIsInstance(rubric, dict)
        self.assertEqual(len(rubric), 5)
    
    def test_score_keys(self):
        """测试获取评分维度键（v2版本新增）"""
        keys = score_keys("三年级")
        self.assertIsInstance(keys, list)
        self.assertEqual(len(keys), 5)
        
        keys = score_keys("六年级")
        self.assertIsInstance(keys, list)
        self.assertEqual(len(keys), 5)
    
    def test_default_topics(self):
        """测试默认题目生成（v2版本新增）"""
        topics = default_topics("三年级", "写人")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        
        topics = default_topics("六年级", "写事")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
    
    def test_generate_topic_options(self):
        """测试题目选项生成（v2版本新增）"""
        topics = generate_topic_options("三年级", "写人")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) <= 8)
        
        topics_with_interest = generate_topic_options("三年级", "写人", "足球")
        self.assertIsInstance(topics_with_interest, list)
        self.assertTrue("足球里的故事" in topics_with_interest)
        self.assertTrue("关于足球的一天" in topics_with_interest)
    
    def test_constants_validation(self):
        """测试常量定义的有效性"""
        self.assertIsInstance(GRADE_OPTIONS, list)
        self.assertIsInstance(GENRE_OPTIONS, list)
        self.assertIsInstance(DEFAULT_TOPICS, list)
        self.assertIsInstance(GRADE_RUBRICS, dict)
        self.assertIsInstance(GRADE_WORDS, dict)
        self.assertIsInstance(TEMPLATES, dict)
        self.assertIsInstance(SAMPLE_ESSAYS, dict)
        
        self.assertTrue(len(GRADE_OPTIONS) > 0)
        self.assertTrue(len(GENRE_OPTIONS) > 0)
        self.assertTrue(len(DEFAULT_TOPICS) > 0)
        self.assertTrue(len(GRADE_RUBRICS) > 0)
        self.assertTrue(len(GRADE_WORDS) > 0)
        self.assertTrue(len(TEMPLATES) > 0)
        self.assertTrue(len(SAMPLE_ESSAYS) > 0)
    
    def test_grade_words_validation(self):
        """测试年级字数范围设置（v2版本新增）"""
        for grade, (min_words, max_words) in GRADE_WORDS.items():
            self.assertIsInstance(min_words, int)
            self.assertIsInstance(max_words, int)
            self.assertTrue(min_words < max_words)
    
    def test_templates_validation(self):
        """测试作文模板结构（v2版本新增）"""
        for genre, template in TEMPLATES.items():
            self.assertIn("框架", template)
            self.assertIn("句式", template)
            self.assertIsInstance(template["框架"], list)
            self.assertIsInstance(template["句式"], list)


if __name__ == '__main__':
    unittest.main()