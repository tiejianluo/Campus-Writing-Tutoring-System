import unittest
import sys
import os
import sqlite3
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from campus_essay_system import (
    get_conn,
    init_db,
    hash_password,
    verify_password,
    login_user,
    register_user,
    save_submission,
    add_new_version,
    query_df,
    create_pdf_report
)


class TestDatabaseFunctions(unittest.TestCase):
    """测试数据库相关功能（v3版本新增）"""
    
    def setUp(self):
        """设置测试环境"""
        # 使用临时数据库文件进行测试
        self.test_db_path = "test_essay_system.db"
        os.environ["ESSAY_APP_DB"] = self.test_db_path
        
        # 初始化数据库
        init_db()
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_get_conn(self):
        """测试数据库连接获取"""
        conn = get_conn()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()
    
    def test_init_db(self):
        """测试数据库初始化"""
        conn = get_conn()
        cur = conn.cursor()
        
        # 检查所有表是否创建
        tables = ["users", "classes", "assignments", "submissions", "essay_versions", "growth_records"]
        for table in tables:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cur.fetchone()
            self.assertIsNotNone(result)
        
        conn.close()
    
    def test_hash_password(self):
        """测试密码哈希功能"""
        password = "test123"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)
    
    def test_verify_password(self):
        """测试密码验证功能"""
        password = "test123"
        hashed = hash_password(password)
        
        # 验证正确密码
        self.assertTrue(verify_password(password, hashed))
        
        # 验证错误密码
        self.assertFalse(verify_password("wrongpassword", hashed))
    
    def test_register_user(self):
        """测试用户注册功能"""
        # 注册新用户
        result = register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        self.assertTrue(result)
        
        # 尝试注册重复用户名
        result = register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        self.assertFalse(result)
    
    def test_login_user(self):
        """测试用户登录功能"""
        # 先注册用户
        register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        
        # 测试正确登录
        user = login_user("testuser", "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["real_name"], "测试学生")
        self.assertEqual(user["grade"], "三年级")
        
        # 测试错误密码
        user = login_user("testuser", "wrongpassword")
        self.assertIsNone(user)
        
        # 测试不存在的用户
        user = login_user("nonexistent", "123456")
        self.assertIsNone(user)
    
    def test_save_submission(self):
        """测试保存作文提交"""
        # 先注册用户
        register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        
        # 准备提交数据
        submission_data = {
            "assignment_id": None,
            "student_username": "testuser",
            "title": "测试作文",
            "genre": "写人",
            "prompt": "测试主题",
            "essay_text": "这是一篇测试作文。",
            "word_count": 10,
            "structure_score": 80,
            "expression_score": 75,
            "total_score": 78,
            "teacher_feedback": "教师点评",
            "student_feedback": "学生鼓励",
            "step_rewrite": {"先补内容": "补充细节"},
            "feedback_json": {"strengths": ["优点1"]}
        }
        
        # 保存提交
        submission_id = save_submission(submission_data)
        self.assertIsInstance(submission_id, int)
        self.assertTrue(submission_id > 0)
    
    def test_add_new_version(self):
        """测试添加新版本"""
        # 先注册用户并保存提交
        register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        
        submission_data = {
            "assignment_id": None,
            "student_username": "testuser",
            "title": "测试作文",
            "genre": "写人",
            "prompt": "测试主题",
            "essay_text": "这是一篇测试作文。",
            "word_count": 10,
            "structure_score": 80,
            "expression_score": 75,
            "total_score": 78,
            "teacher_feedback": "教师点评",
            "student_feedback": "学生鼓励",
            "step_rewrite": {"先补内容": "补充细节"},
            "feedback_json": {"strengths": ["优点1"]}
        }
        
        submission_id = save_submission(submission_data)
        
        # 添加新版本
        add_new_version(submission_id, "这是修改后的作文。", {"strengths": ["改进了"]})
        
        # 验证版本数
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM essay_versions WHERE submission_id=?", (submission_id,))
        count = cur.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 2)
    
    def test_query_df(self):
        """测试数据查询功能"""
        # 先注册用户
        register_user("testuser", "123456", "student", "测试学生", "三年级", "三年级一班")
        
        # 查询用户表
        df = query_df("SELECT * FROM users WHERE username=?", ("testuser",))
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["username"], "testuser")
    
    def test_create_pdf_report(self):
        """测试PDF报告生成"""
        feedback = {
            "teacher_feedback": "这是教师点评。",
            "student_feedback": "这是学生鼓励。",
            "strengths": ["优点1", "优点2"],
            "suggestions": ["建议1", "建议2"]
        }
        
        pdf_bytes = create_pdf_report("测试作文", "测试学生", feedback)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)


if __name__ == '__main__':
    unittest.main()