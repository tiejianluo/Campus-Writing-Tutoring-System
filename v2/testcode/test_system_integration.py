import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    count_chinese_chars,
    paragraph_count,
    sentence_count,
    has_beginning_middle_end,
    rubric_for_grade,
    score_keys,
    call_feedback_llm,
    compare_with_sample,
    stepwise_rewrite,
    generate_titles,
    generate_topic_options,
    structure_level,
    expression_level,
    load_records,
    save_records,
    append_record,
    summarize_growth,
    DATA_PATH
)


class TestSystemIntegration(unittest.TestCase):
    """测试系统集成功能（v2版本）"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 保存原始数据文件（如果存在）
        self.had_records_file = DATA_PATH.exists()
        self.original_records = []
        if self.had_records_file:
            self.original_records = load_records()
    
    def tearDown(self):
        """测试后的清理工作"""
        # 恢复原始数据文件
        if self.had_records_file:
            save_records(self.original_records)
        elif DATA_PATH.exists():
            DATA_PATH.unlink()
    
    def test_full_essay_review_flow(self):
        """测试完整的作文点评流程"""
        # 构建作文数据
        grade = "三年级"
        genre = "写人"
        theme = "我的妈妈"
        essay = "我的妈妈很爱我。每天早上，她都会给我做早餐。有一次我生病了，妈妈一直照顾我。我觉得妈妈是世界上最好的人。"
        
        # 调用反馈生成功能
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证反馈结构完整性
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        self.assertIn("teacher_feedback", feedback)
        self.assertIn("encouraging_feedback", feedback)
        
        # 验证评分维度与年级匹配
        keys = score_keys(grade)
        scores = feedback.get("scores", {})
        for key in keys:
            self.assertIn(key, scores)
    
    def test_character_count_and_feedback_integration(self):
        """测试字符计数与反馈生成的集成"""
        essay = "这是一篇测试作文。今天天气很好，我和同学们一起去公园玩。"
        char_count = count_chinese_chars(essay)
        
        feedback = call_feedback_llm("三年级", "写事", "一次活动", essay)
        
        # 验证字符计数结果合理
        self.assertGreater(char_count, 0)
        
        # 验证反馈内容与作文长度相关
        if char_count < 120:
            self.assertIn("内容还不够展开", feedback["summary"])
        else:
            self.assertIn("明确主题", feedback["summary"])
    
    def test_rubric_consistency_across_modules(self):
        """测试评分维度在各模块间的一致性"""
        grades = ["三年级", "六年级"]
        
        for grade in grades:
            rubric = rubric_for_grade(grade)
            keys = score_keys(grade)
            
            # 验证评分维度的键一致
            self.assertEqual(list(rubric.keys()), keys)
            
            # 验证反馈生成使用了正确的评分维度
            feedback = call_feedback_llm(grade, "写人", "测试主题", "测试作文")
            scores = feedback.get("scores", {})
            for key in keys:
                self.assertIn(key, scores)
    
    def test_error_handling_in_integration(self):
        """测试集成过程中的错误处理"""
        # 测试空作文处理
        empty_essay = ""
        feedback = call_feedback_llm("三年级", "写人", "测试主题", empty_essay)
        
        # 验证系统不会崩溃，能返回合理的反馈
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
    
    def test_full_workflow_with_short_essay(self):
        """测试短作文场景的完整工作流"""
        short_essay = "很短。"
        feedback = call_feedback_llm("三年级", "写事", "测试主题", short_essay)
        
        # 验证短作文反馈
        self.assertIn("内容还不够展开", feedback["summary"])
        
        # 测试分步改写功能
        rewrite = stepwise_rewrite("三年级", short_essay, feedback)
        self.assertIn("step1_add", rewrite)
        self.assertIn("step2_rewrite", rewrite)
    
    def test_full_workflow_with_normal_essay(self):
        """测试正常长度作文场景的完整工作流"""
        normal_essay = "这是一篇正常长度的作文。今天天气很好，我和同学们一起去公园玩。我们玩了很多游戏，非常开心。公园里的花儿开得很美，有红色的玫瑰、黄色的菊花，还有紫色的薰衣草。我们在草地上奔跑、追逐，玩得不亦乐乎。不知不觉中，太阳慢慢西沉，我们恋恋不舍地离开了公园。今天真是难忘的一天，我和朋友们度过了美好的时光。"
        
        # 测试反馈生成
        feedback = call_feedback_llm("三年级", "写景", "秋天的公园", normal_essay)
        
        # 测试范文对比（使用同一段文字作为范文）
        compare_result = compare_with_sample("三年级", "写景", normal_essay, normal_essay)
        self.assertIn("common_strengths", compare_result)
        
        # 测试分步改写
        rewrite = stepwise_rewrite("三年级", normal_essay, feedback)
        self.assertIn("step1_add", rewrite)
    
    def test_topic_generation_integration(self):
        """测试主题生成功能的集成"""
        # 测试主题选项生成
        topics = generate_topic_options("三年级", "写人")
        self.assertIsInstance(topics, list)
        self.assertTrue(len(topics) > 0)
        
        # 测试题目生成
        titles = generate_titles("三年级", "写人", "妈妈")
        self.assertIsInstance(titles, list)
        self.assertTrue(len(titles) > 0)
        
        # 验证生成的题目包含关键词
        keyword_found = any("妈妈" in title for title in titles)
        self.assertTrue(keyword_found)
    
    def test_structure_and_expression_evaluation(self):
        """测试结构和表达水平评估功能"""
        essay = "这是第一段。\n这是第二段。\n这是第三段。好像天气很好，于是我们就去公园玩。"
        
        structure = structure_level(essay)
        expression = expression_level(essay)
        
        # 验证评估结果
        self.assertIn(structure, ["较完整", "基本完整", "待加强"])
        self.assertIn(expression, ["较丰富", "一般", "待丰富"])
    
    def test_growth_records_integration(self):
        """测试成长记录功能的集成"""
        # 测试记录保存和加载
        test_record = {
            "timestamp": "2024-01-01T00:00:00",
            "student_name": "测试学生",
            "grade": "三年级",
            "genre": "写人",
            "theme": "测试主题",
            "word_count": 100,
            "structure_level": "基本完整",
            "expression_level": "一般",
            "scores": {"审题与内容": 7, "结构与顺序": 6, "句子表达": 7, "细节描写": 5, "书写规范": 8},
            "structure_score": 6,
            "language_score": 7,
            "summary": "测试摘要"
        }
        
        # 保存记录
        append_record(test_record)
        
        # 加载记录
        records = load_records()
        self.assertTrue(len(records) > 0)
        
        # 测试成长总结
        summary = summarize_growth(records)
        self.assertIn("count", summary)
        self.assertIn("avg_words", summary)
        self.assertIn("avg_structure", summary)
        self.assertIn("avg_language", summary)
    
    def test_module_interaction_consistency(self):
        """测试不同模块间的交互一致性"""
        essay = "这是一篇测试作文。今天天气很好，我和同学们一起去公园玩。"
        
        # 测试字符计数和段落计数的一致性
        char_count = count_chinese_chars(essay)
        para_count = paragraph_count(essay)
        sent_count = sentence_count(essay)
        
        # 测试结构完整性检查
        has_structure = has_beginning_middle_end(essay)
        
        # 测试结构水平评估
        structure = structure_level(essay)
        
        # 验证各模块返回合理结果
        self.assertGreater(char_count, 0)
        self.assertGreaterEqual(para_count, 1)
        self.assertGreaterEqual(sent_count, 1)
        self.assertIsInstance(has_structure, bool)
        self.assertIn(structure, ["较完整", "基本完整", "待加强"])


if __name__ == '__main__':
    unittest.main()
