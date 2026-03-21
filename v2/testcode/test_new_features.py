import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    fallback_feedback,
    build_feedback_prompt,
    call_feedback_llm,
    compare_with_sample,
    fallback_compare,
    stepwise_rewrite,
    fallback_stepwise,
    structure_level,
    expression_level,
    load_records,
    save_records,
    append_record,
    student_records,
    summarize_growth
)


class TestNewFeatures(unittest.TestCase):
    """测试v2版本新增的功能"""
    
    def test_fallback_feedback_structure(self):
        """测试回退反馈的结构完整性（v2版本扩展）"""
        feedback = fallback_feedback("三年级", "写人", "这是一篇简单的作文。")
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        self.assertIn("teacher_feedback", feedback)
        self.assertIn("encouraging_feedback", feedback)
        self.assertIn("sentence_polish", feedback)
        self.assertIn("outline_advice", feedback)
        self.assertIn("revision_steps", feedback)
    
    def test_fallback_feedback_short_essay(self):
        """测试短作文的回退反馈（v2版本扩展）"""
        short_essay = "很短。"
        feedback = fallback_feedback("三年级", "写人", short_essay)
        self.assertIn("内容还不够展开", feedback["summary"])
    
    def test_build_feedback_prompt(self):
        """测试反馈提示构建（v2版本新增）"""
        prompt = build_feedback_prompt("三年级", "写人", "我的妈妈", "这是一篇作文。")
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：写人", prompt)
        self.assertIn("主题：我的妈妈", prompt)
        self.assertIn("这是一篇作文。", prompt)
    
    def test_call_feedback_llm_fallback(self):
        """测试调用LLM反馈的回退功能（v2版本新增）"""
        feedback = call_feedback_llm("三年级", "写人", "我的妈妈", "这是一篇作文。")
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
    
    def test_fallback_compare_structure(self):
        """测试范文对比的回退结构（v2版本新增）"""
        compare = fallback_compare("学生作文", "范文")
        self.assertIn("common_strengths", compare)
        self.assertIn("missing_parts", compare)
        self.assertIn("imitation_points", compare)
    
    def test_compare_with_sample_fallback(self):
        """测试与范文对比的回退功能（v2版本新增）"""
        compare = compare_with_sample("三年级", "写人", "学生作文", "范文")
        self.assertIn("common_strengths", compare)
        self.assertIn("missing_parts", compare)
        self.assertIn("imitation_points", compare)
    
    def test_fallback_stepwise_structure(self):
        """测试分步改写的回退结构（v2版本新增）"""
        stepwise = fallback_stepwise()
        self.assertIn("step1_add", stepwise)
        self.assertIn("step2_rewrite", stepwise)
        self.assertIn("step3_opening", stepwise)
        self.assertIn("step4_ending", stepwise)
    
    def test_stepwise_rewrite_fallback(self):
        """测试分步改写的回退功能（v2版本新增）"""
        feedback = {"summary": "测试"}
        stepwise = stepwise_rewrite("三年级", "测试作文", feedback)
        self.assertIn("step1_add", stepwise)
        self.assertIn("step2_rewrite", stepwise)
        self.assertIn("step3_opening", stepwise)
        self.assertIn("step4_ending", stepwise)
    
    def test_structure_level(self):
        """测试结构水平评估（v2版本新增）"""
        self.assertEqual(structure_level("很短"), "待加强")
        self.assertEqual(structure_level("第一句。第二句。第三句。第四句。"), "基本完整")
        self.assertEqual(structure_level("第一段\n第二段\n第三段\n第四句。第五句。第六句。"), "较完整")
    
    def test_expression_level(self):
        """测试表达水平评估（v2版本新增）"""
        self.assertEqual(expression_level("简单的文字"), "待丰富")
        self.assertEqual(expression_level("好像很开心"), "一般")
        self.assertEqual(expression_level("好像很开心，仿佛在笑，心里很高兴"), "较丰富")
    
    def test_data_persistence(self):
        """测试数据持久化功能（v2版本新增）"""
        # 测试加载记录
        records = load_records()
        self.assertIsInstance(records, list)
        
        # 测试保存记录
        test_record = {
            "timestamp": "2024-01-01T12:00:00",
            "student_name": "测试学生",
            "grade": "三年级",
            "genre": "写人",
            "theme": "测试主题",
            "word_count": 100,
            "paragraph_count": 2,
            "structure_level": "基本完整",
            "expression_level": "一般",
            "scores": {"审题与内容": 7},
            "structure_score": 7,
            "language_score": 6,
            "summary": "测试摘要"
        }
        
        # 保存记录
        original_length = len(records)
        append_record(test_record)
        
        # 重新加载并验证
        new_records = load_records()
        self.assertEqual(len(new_records), original_length + 1)
        
        # 清理测试数据
        save_records(records)
    
    def test_student_records(self):
        """测试获取学生记录（v2版本新增）"""
        records = student_records("不存在的学生")
        self.assertIsInstance(records, list)
    
    def test_summarize_growth(self):
        """测试成长总结功能（v2版本新增）"""
        # 测试空记录
        summary = summarize_growth([])
        self.assertEqual(summary["count"], 0)
        
        # 测试有记录的情况
        test_records = [
            {
                "word_count": 200,
                "structure_score": 8,
                "language_score": 7,
                "timestamp": "2024-01-01"
            },
            {
                "word_count": 300,
                "structure_score": 9,
                "language_score": 8,
                "timestamp": "2024-01-02"
            }
        ]
        summary = summarize_growth(test_records)
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["avg_words"], 250.0)
        self.assertEqual(summary["avg_structure"], 8.5)
        self.assertEqual(summary["avg_language"], 7.5)


if __name__ == '__main__':
    unittest.main()