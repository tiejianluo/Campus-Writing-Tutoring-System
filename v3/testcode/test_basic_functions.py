import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from campus_essay_system import (
    chinese_word_count,
    paragraph_count,
    infer_structure_score,
    infer_expression_score,
    grade_expectation,
    get_rubric_markdown,
    build_prompt,
    fallback_feedback,
    generate_topics,
    compare_with_model_essay,
    GRADE_RUBRICS,
    ESSAY_TEMPLATES,
    DEFAULT_TOPICS
)


class TestBasicFunctions(unittest.TestCase):
    """测试基础功能函数（继承自v1和v2版本的测试并扩展）"""
    
    def test_chinese_word_count(self):
        """测试中文字符计数功能（继承自v1版本）"""
        self.assertEqual(chinese_word_count(""), 0)
        self.assertEqual(chinese_word_count("你好"), 2)
        self.assertEqual(chinese_word_count("Hello 世界"), 2)
        self.assertEqual(chinese_word_count("今天天气真好！"), 6)
        self.assertEqual(chinese_word_count("123中文abc"), 2)
    
    def test_paragraph_count(self):
        """测试段落计数功能（继承自v2版本）"""
        self.assertEqual(paragraph_count(""), 0)
        self.assertEqual(paragraph_count("一行文字"), 1)
        self.assertEqual(paragraph_count("第一段\n第二段"), 2)
        self.assertEqual(paragraph_count("第一段\n\n第三段"), 2)
        self.assertEqual(paragraph_count("第一段\n第二段\n第三段"), 3)
    
    def test_infer_structure_score(self):
        """测试结构评分推断（v3版本新增）"""
        # 基础分60分
        self.assertEqual(infer_structure_score(""), 60)
        
        # 字数奖励
        text_180 = "中" * 180
        self.assertEqual(infer_structure_score(text_180), 70)
        
        text_300 = "中" * 300
        self.assertEqual(infer_structure_score(text_300), 80)
        
        # 段落奖励
        text_with_paragraphs = "第一段\n第二段\n第三段"
        score = infer_structure_score(text_with_paragraphs)
        self.assertTrue(score >= 70)
        
        # 顺序词奖励
        text_with_order = "首先，...然后，...最后。"
        score = infer_structure_score(text_with_order)
        self.assertTrue(score >= 70)
        
        # 满分情况
        perfect_text = "中" * 300 + "\n第二段\n第三段\n首先，然后，最后"
        self.assertEqual(infer_structure_score(perfect_text), 100)
    
    def test_infer_expression_score(self):
        """测试表达评分推断（v3版本新增）"""
        # 基础分60分
        self.assertEqual(infer_expression_score(""), 60)
        
        # 比喻词奖励
        text_with_metaphor = "像...仿佛..."
        score = infer_expression_score(text_with_metaphor)
        self.assertTrue(score >= 70)
        
        # 情感词奖励
        text_with_emotion = "很高兴..."
        score = infer_expression_score(text_with_emotion)
        self.assertTrue(score >= 70)
        
        # 字数奖励
        text_long = "中" * 250
        score = infer_expression_score(text_long)
        self.assertTrue(score >= 70)
        
        # 标点符号奖励
        text_with_punctuation = "！？……"
        score = infer_expression_score(text_with_punctuation)
        self.assertTrue(score >= 70)
        
        # 满分情况
        perfect_text = "像...仿佛...很高兴...中" * 100 + "！？……"
        self.assertEqual(infer_expression_score(perfect_text), 100)
    
    def test_grade_expectation(self):
        """测试年级期望字数（v3版本新增）"""
        for grade in GRADE_RUBRICS.keys():
            expectation = grade_expectation(grade)
            self.assertIn("建议字数：", expectation)
            self.assertIn("—", expectation)
            self.assertIn("字", expectation)
    
    def test_get_rubric_markdown(self):
        """测试获取评分标准的markdown格式（v3版本新增）"""
        for grade in GRADE_RUBRICS.keys():
            markdown = get_rubric_markdown(grade)
            self.assertIsInstance(markdown, str)
            self.assertTrue(len(markdown) > 0)
    
    def test_build_prompt(self):
        """测试构建提示（v3版本新增）"""
        prompt = build_prompt("三年级", "写人", "我的妈妈", "作文内容")
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：写人", prompt)
        self.assertIn("作文题目/主题：我的妈妈", prompt)
        self.assertIn("作文内容", prompt)
    
    def test_fallback_feedback_structure(self):
        """测试回退反馈结构（继承并扩展自v2版本）"""
        feedback = fallback_feedback("三年级", "写人", "我的妈妈", "作文内容")
        self.assertIn("teacher_feedback", feedback)
        self.assertIn("student_feedback", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("suggestions", feedback)
        self.assertIn("polished_sentence", feedback)
        self.assertIn("outline_advice", feedback)
        self.assertIn("step_rewrite", feedback)
    
    def test_generate_topics(self):
        """测试生成题目（v3版本扩展）"""
        topics = generate_topics("三年级", "写人")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        
        # 测试带关键词的生成
        topics_with_keyword = generate_topics("三年级", "写人", "足球")
        self.assertIsInstance(topics_with_keyword, list)
        self.assertTrue(len(topics_with_keyword) > 0)
        
        # 测试高年级特殊题目
        topics_high_grade = generate_topics("六年级", "写人", "成长")
        self.assertIsInstance(topics_high_grade, list)
        self.assertTrue("我眼中的成长" in topics_high_grade)
    
    def test_compare_with_model_essay(self):
        """测试与范文对比（v3版本新增）"""
        comparison = compare_with_model_essay("学生作文", "写人", "我的妈妈")
        self.assertIsInstance(comparison, str)
        self.assertIn("范文对比提示", comparison)
    
    def test_constants_validation(self):
        """测试常量定义的有效性"""
        self.assertIsInstance(GRADE_RUBRICS, dict)
        self.assertIsInstance(ESSAY_TEMPLATES, dict)
        self.assertIsInstance(DEFAULT_TOPICS, dict)
        
        self.assertTrue(len(GRADE_RUBRICS) > 0)
        self.assertTrue(len(ESSAY_TEMPLATES) > 0)
        self.assertTrue(len(DEFAULT_TOPICS) > 0)
    
    def test_grade_rubrics_validation(self):
        """测试年级评分标准结构（v3版本新增）"""
        for grade, config in GRADE_RUBRICS.items():
            self.assertIn("rubric", config)
            self.assertIn("target_words", config)
            self.assertIsInstance(config["rubric"], list)
            self.assertIsInstance(config["target_words"], tuple)
    
    def test_essay_templates_validation(self):
        """测试作文模板结构（v3版本扩展）"""
        for genre, template in ESSAY_TEMPLATES.items():
            self.assertIn("结构", template)
            self.assertIn("万能开头", template)
            self.assertIn("万能结尾", template)
            self.assertIsInstance(template["结构"], list)


if __name__ == '__main__':
    unittest.main()