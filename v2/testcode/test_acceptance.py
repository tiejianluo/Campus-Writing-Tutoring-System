import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    call_feedback_llm,
    compare_with_sample,
    stepwise_rewrite,
    generate_titles,
    generate_topic_options,
    fallback_image_prompts,
    load_records,
    save_records,
    append_record,
    summarize_growth,
    DATA_PATH,
    SAMPLE_ESSAYS
)


class TestAcceptance(unittest.TestCase):
    """验收测试（v2版本）"""
    
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
    
    def test_user_story_grade_3_narrative_essay(self):
        """测试三年级学生写记叙文的用户故事"""
        grade = "三年级"
        genre = "写事"
        theme = "一次难忘的活动"
        essay = "上周六，我们班举行了跳绳比赛。刚开始时，我很紧张，手心都出汗了。轮到我上场时，我深吸一口气，努力让自己平静下来。随着哨声响起，我飞快地跳了起来。虽然最后没有拿第一名，但我明白了只要勇敢面对，就有进步。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证反馈格式和内容
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        
        # 验证评分在合理范围内
        scores = feedback.get("scores", {})
        for score in scores.values():
            self.assertGreaterEqual(score, 1)
            self.assertLessEqual(score, 10)
    
    def test_user_story_grade_5_descriptive_essay(self):
        """测试五年级学生写写景作文的用户故事"""
        grade = "五年级"
        genre = "写景"
        theme = "秋天的校园"
        essay = "秋天的校园真美。操场边的银杏树像撑开的一把把金色小伞，风一吹，叶子轻轻落下来，像一只只蝴蝶在飞。花坛里的菊花开得正热闹，有黄的、白的、紫的，把校园装扮得五彩缤纷。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证反馈格式和内容
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
    
    def test_user_story_short_essay_handling(self):
        """测试短作文处理的用户故事"""
        grade = "三年级"
        genre = "写人"
        theme = "我的好朋友"
        short_essay = "我的好朋友是小明。他很聪明。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, short_essay)
        
        # 验证短作文的反馈内容
        self.assertIn("内容还不够展开", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 6)
    
    def test_user_story_empty_input_handling(self):
        """测试空输入处理的用户故事"""
        grade = "四年级"
        genre = "写事"
        theme = "难忘的一天"
        empty_essay = ""
        
        # 获取反馈（不应崩溃）
        feedback = call_feedback_llm(grade, genre, theme, empty_essay)
        
        # 验证反馈格式正确
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
    
    def test_user_story_complex_essay_with_dialogue(self):
        """测试包含对话的复杂作文的用户故事"""
        grade = "六年级"
        genre = "写事"
        theme = "一次有趣的对话"
        essay = "\"妈妈，今天我们去公园玩好不好？\"我兴奋地问。\"好啊，\"妈妈笑着说，\"但是你要先完成作业。\"我点点头，赶紧跑回房间写作业。写完作业后，我们开开心心地去了公园。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证反馈格式正确
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
    
    def test_acceptance_criteria_output_format(self):
        """测试输出格式验证的验收标准"""
        grade = "四年级"
        genre = "写人"
        theme = "我的老师"
        essay = "我的老师姓王，她很温柔。每次我有问题，她都会耐心地教我。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证反馈为字典格式
        self.assertIsInstance(feedback, dict)
        
        # 验证包含所有必要字段
        required_fields = ["summary", "scores", "strengths", "improvements", "teacher_feedback", "encouraging_feedback", "sentence_polish", "outline_advice", "revision_steps"]
        for field in required_fields:
            self.assertIn(field, feedback)
        
        # 验证各字段类型正确
        self.assertIsInstance(feedback["summary"], str)
        self.assertIsInstance(feedback["scores"], dict)
        self.assertIsInstance(feedback["strengths"], list)
        self.assertIsInstance(feedback["improvements"], list)
        self.assertIsInstance(feedback["teacher_feedback"], str)
        self.assertIsInstance(feedback["encouraging_feedback"], str)
        self.assertIsInstance(feedback["sentence_polish"], list)
        self.assertIsInstance(feedback["outline_advice"], list)
        self.assertIsInstance(feedback["revision_steps"], list)
    
    def test_acceptance_criteria_content_quality(self):
        """测试内容质量验证的验收标准"""
        grade = "五年级"
        genre = "写景"
        theme = "美丽的公园"
        essay = "公园的春天真美。花儿开了，草儿绿了，小鸟在唱歌。我喜欢春天的公园。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 验证内容质量要求
        self.assertGreaterEqual(len(feedback.get("strengths", [])), 3)
        self.assertGreaterEqual(len(feedback.get("improvements", [])), 3)
        self.assertGreaterEqual(len(feedback.get("sentence_polish", [])), 2)
        self.assertGreaterEqual(len(feedback.get("outline_advice", [])), 3)
    
    def test_acceptance_criteria_sample_comparison(self):
        """测试范文对比功能的验收标准"""
        grade = "四年级"
        genre = "写人"
        essay = "我的妈妈很爱我。每天早上，她都会给我做早餐。"
        
        # 获取范文
        sample = SAMPLE_ESSAYS.get(genre, "")
        
        # 进行范文对比
        compare_result = compare_with_sample(grade, genre, essay, sample)
        
        # 验证对比结果格式
        self.assertIsInstance(compare_result, dict)
        self.assertIn("common_strengths", compare_result)
        self.assertIn("missing_parts", compare_result)
        self.assertIn("imitation_points", compare_result)
        
        # 验证内容质量
        self.assertGreaterEqual(len(compare_result.get("common_strengths", [])), 1)
        self.assertGreaterEqual(len(compare_result.get("missing_parts", [])), 1)
        self.assertGreaterEqual(len(compare_result.get("imitation_points", [])), 1)
    
    def test_acceptance_criteria_stepwise_rewrite(self):
        """测试分步改写功能的验收标准"""
        grade = "三年级"
        genre = "写事"
        theme = "一次活动"
        essay = "今天我们去公园玩。我们玩了很多游戏。"
        
        # 获取反馈
        feedback = call_feedback_llm(grade, genre, theme, essay)
        
        # 生成分步改写建议
        rewrite = stepwise_rewrite(grade, essay, feedback)
        
        # 验证分步改写结果格式
        self.assertIsInstance(rewrite, dict)
        self.assertIn("step1_add", rewrite)
        self.assertIn("step2_rewrite", rewrite)
        self.assertIn("step3_opening", rewrite)
        self.assertIn("step4_ending", rewrite)
        
        # 验证内容质量
        self.assertGreaterEqual(len(rewrite.get("step1_add", [])), 1)
        self.assertGreaterEqual(len(rewrite.get("step2_rewrite", [])), 1)
        self.assertIsInstance(rewrite.get("step3_opening"), str)
        self.assertIsInstance(rewrite.get("step4_ending"), str)
    
    def test_acceptance_criteria_topic_generation(self):
        """测试题目生成功能的验收标准"""
        grade = "五年级"
        genre = "想象作文"
        
        # 生成主题选项
        topics = generate_topic_options(grade, genre)
        
        # 验证主题选项
        self.assertIsInstance(topics, list)
        self.assertGreaterEqual(len(topics), 4)
        
        # 生成作文题目
        titles = generate_titles(grade, genre, "未来")
        
        # 验证作文题目
        self.assertIsInstance(titles, list)
        self.assertGreaterEqual(len(titles), 5)
        # 验证包含关键词
        keyword_found = any("未来" in title for title in titles)
        self.assertTrue(keyword_found)
    
    def test_acceptance_criteria_image_prompts(self):
        """测试图片提示功能的验收标准"""
        grade = "四年级"
        
        # 获取回退图片提示
        prompts = fallback_image_prompts(grade)
        
        # 验证图片提示格式
        self.assertIsInstance(prompts, dict)
        self.assertIn("scene", prompts)
        self.assertIn("observe", prompts)
        self.assertIn("questions", prompts)
        self.assertIn("suggested_title", prompts)
        
        # 验证内容质量
        self.assertIsInstance(prompts["scene"], str)
        self.assertIsInstance(prompts["observe"], list)
        self.assertIsInstance(prompts["questions"], list)
        self.assertIsInstance(prompts["suggested_title"], str)
        self.assertEqual(len(prompts["observe"]), 4)
        self.assertEqual(len(prompts["questions"]), 4)
    
    def test_acceptance_criteria_growth_records(self):
        """测试成长记录功能的验收标准"""
        # 创建测试记录
        test_records = [
            {
                "timestamp": "2024-01-01T00:00:00",
                "student_name": "测试学生",
                "grade": "三年级",
                "genre": "写人",
                "theme": "我的妈妈",
                "word_count": 100,
                "structure_level": "基本完整",
                "expression_level": "一般",
                "scores": {"审题与内容": 7, "结构与顺序": 6, "句子表达": 7, "细节描写": 5, "书写规范": 8},
                "structure_score": 6,
                "language_score": 7,
                "summary": "第一次练习"
            },
            {
                "timestamp": "2024-01-02T00:00:00",
                "student_name": "测试学生",
                "grade": "三年级",
                "genre": "写事",
                "theme": "一次活动",
                "word_count": 150,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 8, "结构与顺序": 7, "句子表达": 8, "细节描写": 6, "书写规范": 8},
                "structure_score": 7,
                "language_score": 8,
                "summary": "第二次练习"
            }
        ]
        
        # 保存测试记录
        save_records(test_records)
        
        # 测试成长总结
        summary = summarize_growth(test_records)
        
        # 验证成长总结格式
        self.assertIsInstance(summary, dict)
        self.assertIn("count", summary)
        self.assertIn("avg_words", summary)
        self.assertIn("avg_structure", summary)
        self.assertIn("avg_language", summary)
        
        # 验证计算结果
        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["avg_words"], 125.0)
        self.assertEqual(summary["avg_structure"], 6.5)
        self.assertEqual(summary["avg_language"], 7.5)


if __name__ == '__main__':
    unittest.main()
