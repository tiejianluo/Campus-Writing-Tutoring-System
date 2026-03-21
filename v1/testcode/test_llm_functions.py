import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app import (
    get_client,
    build_user_prompt,
    call_llm,
    make_revision_prompt,
    revise_guidance,
    SYSTEM_PROMPT,
    JSON_SCHEMA_HINT,
    RUBRIC
)


class TestLLMFunctions(unittest.TestCase):
    """测试LLM相关功能（v1版本扩展测试）"""
    
    def test_get_client(self):
        """测试获取OpenAI客户端"""
        client = get_client()
        # 如果OpenAI库不可用，应该返回None
        # 这个测试主要确保函数不会抛出异常
        try:
            result = get_client()
            self.assertIsInstance(result, (type(None), object))
        except Exception:
            self.fail("get_client() raised exception unexpectedly")
    
    def test_build_user_prompt_structure(self):
        """测试用户提示构建的结构完整性"""
        prompt = build_user_prompt("三年级", "记叙文", "难忘的一天", 300, "这是一篇测试作文。")
        
        # 验证提示包含所有必要信息
        self.assertIn("学生年级：三年级", prompt)
        self.assertIn("作文类型：记叙文", prompt)
        self.assertIn("主题：难忘的一天", prompt)
        self.assertIn("目标字数：300", prompt)
        self.assertIn("这是一篇测试作文。", prompt)
        
        # 验证包含评分维度
        for rubric_key in RUBRIC.keys():
            self.assertIn(rubric_key, prompt)
        
        # 验证包含JSON格式要求
        self.assertIn("输出 JSON 键必须包含", prompt)
    
    def test_build_user_prompt_different_grades(self):
        """测试不同年级的提示构建"""
        grades = ["三年级", "四年级", "五年级", "六年级"]
        
        for grade in grades:
            prompt = build_user_prompt(grade, "记叙文", "测试主题", 300, "测试作文")
            self.assertIn(f"学生年级：{grade}", prompt)
    
    def test_build_user_prompt_different_genres(self):
        """测试不同作文类型的提示构建"""
        genres = ["记叙文", "写人", "写景", "想象作文", "读后感", "日记", "看图作文"]
        
        for genre in genres:
            prompt = build_user_prompt("三年级", genre, "测试主题", 300, "测试作文")
            self.assertIn(f"作文类型：{genre}", prompt)
    
    def test_call_llm_fallback(self):
        """测试调用LLM的回退功能"""
        feedback = call_llm("三年级", "记叙文", "难忘的一天", 300, "这是一篇测试作文。")
        
        # 验证回退反馈的结构
        self.assertIn("summary", feedback)
        self.assertIn("scores", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("improvements", feedback)
        self.assertIn("sentence_polish", feedback)
        self.assertIn("outline_advice", feedback)
        self.assertIn("encouragement", feedback)
    
    def test_call_llm_short_essay(self):
        """测试短作文的反馈"""
        short_essay = "很短。"
        feedback = call_llm("三年级", "记叙文", "测试主题", 300, short_essay)
        
        self.assertIn("篇幅偏短", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 5)
    
    def test_call_llm_normal_essay(self):
        """测试正常长度作文的反馈"""
        normal_essay = "这是一篇正常长度的作文。今天天气很好，我和同学们一起去公园玩。我们玩了很多游戏，非常开心。"
        feedback = call_llm("三年级", "记叙文", "测试主题", 300, normal_essay)
        
        self.assertIn("完整主题", feedback["summary"])
        self.assertEqual(feedback["scores"]["细节描写"], 6)
    
    def test_make_revision_prompt(self):
        """测试修改提示构建"""
        feedback = {
            "strengths": ["优点1", "优点2", "优点3"],
            "improvements": ["改进1", "改进2", "改进3"]
        }
        essay = "测试作文内容"
        
        prompt = make_revision_prompt(essay, feedback)
        
        # 验证提示包含所有必要信息
        self.assertIn("测试作文内容", prompt)
        self.assertIn("优点1", prompt)
        self.assertIn("改进1", prompt)
        
        # 验证包含引导式修改的要求
        self.assertIn("引导式修改建议", prompt)
        self.assertIn("不要直接重写整篇作文", prompt)
    
    def test_revise_guidance_fallback(self):
        """测试修改指导的回退功能"""
        feedback = {"strengths": [], "improvements": []}
        guidance = revise_guidance("测试作文", feedback)
        
        # 验证回退指导包含三个部分
        self.assertIn("可以先补充", guidance)
        self.assertIn("可以改写", guidance)
        self.assertIn("参考开头", guidance)
    
    def test_system_prompt_constant(self):
        """测试系统提示常量"""
        self.assertIsInstance(SYSTEM_PROMPT, str)
        self.assertTrue(len(SYSTEM_PROMPT) > 0)
        self.assertIn("耐心、温和、擅长启发式教学", SYSTEM_PROMPT)
        self.assertIn("语言简单、鼓励性强", SYSTEM_PROMPT)
    
    def test_json_schema_hint_constant(self):
        """测试JSON模式提示常量"""
        self.assertIsInstance(JSON_SCHEMA_HINT, dict)
        self.assertIn("summary", JSON_SCHEMA_HINT)
        self.assertIn("scores", JSON_SCHEMA_HINT)
        self.assertIn("strengths", JSON_SCHEMA_HINT)
        self.assertIn("improvements", JSON_SCHEMA_HINT)
        self.assertIn("sentence_polish", JSON_SCHEMA_HINT)
        self.assertIn("outline_advice", JSON_SCHEMA_HINT)
        self.assertIn("encouragement", JSON_SCHEMA_HINT)


if __name__ == '__main__':
    unittest.main()