import unittest
import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elementary_essay_tutor_app_v2 import (
    load_records,
    save_records,
    append_record,
    student_records,
    summarize_growth,
    DATA_PATH
)


class TestDataPersistence(unittest.TestCase):
    """测试数据持久化功能（v2版本扩展测试）"""
    
    def setUp(self):
        """设置测试环境"""
        # 备份原始数据文件
        self.original_data = None
        if DATA_PATH.exists():
            self.original_data = DATA_PATH.read_text(encoding="utf-8")
        else:
            # 创建空文件
            DATA_PATH.write_text("[]", encoding="utf-8")
    
    def tearDown(self):
        """清理测试环境"""
        # 恢复原始数据
        if self.original_data is not None:
            DATA_PATH.write_text(self.original_data, encoding="utf-8")
        elif DATA_PATH.exists():
            DATA_PATH.unlink()
    
    def test_load_empty_records(self):
        """测试加载空记录"""
        # 确保文件为空
        DATA_PATH.write_text("[]", encoding="utf-8")
        
        records = load_records()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 0)
    
    def test_load_invalid_json(self):
        """测试加载无效JSON数据"""
        # 写入无效JSON
        DATA_PATH.write_text("invalid json", encoding="utf-8")
        
        records = load_records()
        self.assertIsInstance(records, list)
        self.assertEqual(len(records), 0)
    
    def test_save_records(self):
        """测试保存记录"""
        test_records = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "student_name": "测试学生1",
                "grade": "三年级",
                "genre": "写人",
                "theme": "我的妈妈",
                "word_count": 200,
                "paragraph_count": 3,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 8, "结构与顺序": 7},
                "structure_score": 7,
                "language_score": 8,
                "summary": "测试摘要1"
            },
            {
                "timestamp": "2024-01-02T14:00:00",
                "student_name": "测试学生2",
                "grade": "四年级",
                "genre": "写事",
                "theme": "一次难忘的活动",
                "word_count": 300,
                "paragraph_count": 4,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 9, "结构与顺序": 8},
                "structure_score": 8,
                "language_score": 9,
                "summary": "测试摘要2"
            }
        ]
        
        # 保存记录
        save_records(test_records)
        
        # 重新加载验证
        loaded_records = load_records()
        self.assertEqual(len(loaded_records), 2)
        self.assertEqual(loaded_records[0]["student_name"], "测试学生1")
        self.assertEqual(loaded_records[1]["student_name"], "测试学生2")
    
    def test_append_record(self):
        """测试追加记录"""
        # 先保存一些记录
        initial_records = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "student_name": "初始学生",
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
                "summary": "初始摘要"
            }
        ]
        save_records(initial_records)
        
        # 追加新记录
        new_record = {
            "timestamp": "2024-01-03T10:00:00",
            "student_name": "新学生",
            "grade": "四年级",
            "genre": "写事",
            "theme": "新主题",
            "word_count": 250,
            "paragraph_count": 3,
            "structure_level": "较完整",
            "expression_level": "较丰富",
            "scores": {"审题与内容": 8},
            "structure_score": 8,
            "language_score": 7,
            "summary": "新摘要"
        }
        append_record(new_record)
        
        # 验证记录数量
        loaded_records = load_records()
        self.assertEqual(len(loaded_records), 2)
        self.assertEqual(loaded_records[1]["student_name"], "新学生")
    
    def test_student_records_query(self):
        """测试按学生查询记录"""
        # 创建测试数据
        test_records = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "student_name": "张三",
                "grade": "三年级",
                "genre": "写人",
                "theme": "我的妈妈",
                "word_count": 200,
                "paragraph_count": 3,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 8},
                "structure_score": 8,
                "language_score": 7,
                "summary": "张三的作文"
            },
            {
                "timestamp": "2024-01-02T14:00:00",
                "student_name": "李四",
                "grade": "四年级",
                "genre": "写事",
                "theme": "一次活动",
                "word_count": 300,
                "paragraph_count": 4,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 9},
                "structure_score": 9,
                "language_score": 8,
                "summary": "李四的作文"
            },
            {
                "timestamp": "2024-01-03T10:00:00",
                "student_name": "张三",
                "grade": "三年级",
                "genre": "写景",
                "theme": "校园一角",
                "word_count": 250,
                "paragraph_count": 3,
                "structure_level": "较完整",
                "expression_level": "较丰富",
                "scores": {"审题与内容": 8},
                "structure_score": 8,
                "language_score": 8,
                "summary": "张三的第二篇作文"
            }
        ]
        save_records(test_records)
        
        # 查询特定学生的记录
        zhang_records = student_records("张三")
        li_records = student_records("李四")
        wang_records = student_records("王五")
        
        self.assertEqual(len(zhang_records), 2)
        self.assertEqual(len(li_records), 1)
        self.assertEqual(len(wang_records), 0)
    
    def test_summarize_growth_empty(self):
        """测试空记录的成长总结"""
        summary = summarize_growth([])
        self.assertEqual(summary["count"], 0)
    
    def test_summarize_growth_single_record(self):
        """测试单条记录的成长总结"""
        records = [
            {
                "word_count": 200,
                "structure_score": 8,
                "language_score": 7,
                "timestamp": "2024-01-01"
            }
        ]
        summary = summarize_growth(records)
        
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["avg_words"], 200.0)
        self.assertEqual(summary["avg_structure"], 8.0)
        self.assertEqual(summary["avg_language"], 7.0)
        self.assertEqual(summary["word_counts"], [200])
        self.assertEqual(summary["structure_scores"], [8])
        self.assertEqual(summary["language_scores"], [7])
        self.assertEqual(summary["dates"], ["2024-01-01"])
    
    def test_summarize_growth_multiple_records(self):
        """测试多条记录的成长总结"""
        records = [
            {
                "word_count": 200,
                "structure_score": 8,
                "language_score": 7,
                "timestamp": "2024-01-01"
            },
            {
                "word_count": 250,
                "structure_score": 8,
                "language_score": 8,
                "timestamp": "2024-01-02"
            },
            {
                "word_count": 300,
                "structure_score": 9,
                "language_score": 8,
                "timestamp": "2024-01-03"
            }
        ]
        summary = summarize_growth(records)
        
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["avg_words"], 250.0)
        self.assertEqual(summary["avg_structure"], 8.33)
        self.assertEqual(summary["avg_language"], 7.67)
        self.assertEqual(summary["word_counts"], [200, 250, 300])
        self.assertEqual(summary["structure_scores"], [8, 8, 9])
        self.assertEqual(summary["language_scores"], [7, 8, 8])
        self.assertEqual(summary["dates"], ["2024-01-01", "2024-01-02", "2024-01-03"])


if __name__ == '__main__':
    unittest.main()