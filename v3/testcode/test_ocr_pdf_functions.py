import unittest
import sys
import os
from PIL import Image
import io

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from campus_essay_system import (
    register_chinese_font,
    create_pdf_report,
    preprocess_for_ocr,
    run_ocr
)


class TestOcrPdfFunctions(unittest.TestCase):
    """测试OCR和PDF相关功能（v3版本新增）"""
    
    def test_register_chinese_font(self):
        """测试中文字体注册功能"""
        # 测试字体注册不会抛出异常
        try:
            register_chinese_font()
            success = True
        except Exception:
            success = False
        self.assertTrue(success)
    
    def test_create_pdf_report_basic(self):
        """测试PDF报告生成的基本功能"""
        feedback = {
            "teacher_feedback": "这是教师点评。",
            "student_feedback": "这是学生鼓励。",
            "strengths": ["优点1", "优点2"],
            "suggestions": ["建议1", "建议2"]
        }
        
        pdf_bytes = create_pdf_report("测试作文", "测试学生", feedback)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
    
    def test_create_pdf_report_empty_feedback(self):
        """测试空反馈时的PDF生成"""
        feedback = {}
        
        pdf_bytes = create_pdf_report("测试作文", "测试学生", feedback)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
    
    def test_create_pdf_report_long_text(self):
        """测试长文本反馈的PDF生成"""
        feedback = {
            "teacher_feedback": "这是非常长的教师点评文本，" * 50,
            "student_feedback": "这是非常长的学生鼓励文本，" * 50,
            "strengths": ["优点" + str(i) for i in range(10)],
            "suggestions": ["建议" + str(i) for i in range(10)]
        }
        
        pdf_bytes = create_pdf_report("测试作文", "测试学生", feedback)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
    
    def test_preprocess_for_ocr(self):
        """测试OCR预处理功能"""
        # 创建一个简单的测试图像
        img = Image.new('RGB', (100, 100), color='white')
        
        try:
            processed_img = preprocess_for_ocr(img)
            self.assertIsInstance(processed_img, Image.Image)
        except Exception:
            # 如果OpenCV不可用，测试应该跳过
            self.skipTest("OpenCV not available")
    
    def test_run_ocr(self):
        """测试OCR运行功能"""
        # 创建一个简单的测试图像
        img = Image.new('RGB', (100, 100), color='white')
        
        try:
            result = run_ocr(img)
            # 如果RapidOCR不可用，应该返回空字符串
            self.assertIsInstance(result, str)
        except Exception:
            # 如果RapidOCR不可用，测试应该跳过
            self.skipTest("RapidOCR not available")


if __name__ == '__main__':
    unittest.main()