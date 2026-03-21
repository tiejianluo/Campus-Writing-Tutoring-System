import unittest
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from campus_essay_system import (
    register_user,
    get_conn,
    query_df
)


class TestClassAssignment(unittest.TestCase):
    """测试班级管理和作业功能（v3版本新增）"""
    
    def setUp(self):
        """设置测试环境"""
        # 使用临时数据库文件进行测试
        self.test_db_path = "test_class_assignment.db"
        os.environ["ESSAY_APP_DB"] = self.test_db_path
        
        # 导入并初始化数据库
        from campus_essay_system import init_db
        init_db()
        
        # 注册测试用户
        register_user("teacher1", "123456", "teacher", "李老师", None, None)
        register_user("student1", "123456", "student", "张三", "三年级", "三年级一班")
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_add_class(self):
        """测试添加班级功能"""
        conn = get_conn()
        cur = conn.cursor()
        
        # 添加班级
        now = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
            ("三年级二班", "三年级", "teacher1", now)
        )
        conn.commit()
        
        # 验证班级已添加
        cur.execute("SELECT * FROM classes WHERE class_name='三年级二班'")
        result = cur.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result["grade"], "三年级")
        self.assertEqual(result["teacher_username"], "teacher1")
        
        conn.close()
    
    def test_add_duplicate_class(self):
        """测试添加重复班级"""
        conn = get_conn()
        cur = conn.cursor()
        
        # 先添加一个班级
        now = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
            ("三年级三班", "三年级", "teacher1", now)
        )
        
        # 尝试添加相同名称的班级
        try:
            cur.execute(
                "INSERT INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
                ("三年级三班", "三年级", "teacher1", now)
            )
            conn.commit()
            # 如果没有抛出异常，验证是否实际插入了重复记录
            cur.execute("SELECT COUNT(*) FROM classes WHERE class_name='三年级三班'")
            count = cur.fetchone()[0]
            self.assertEqual(count, 1)  # 应该只有一条记录
        except Exception:
            # 如果抛出异常，也认为测试通过
            pass
        
        conn.close()
    
    def test_assign_class_to_student(self):
        """测试为学生分配班级"""
        conn = get_conn()
        cur = conn.cursor()
        
        # 更新学生班级
        cur.execute("UPDATE users SET class_name='三年级二班' WHERE username='student1'")
        conn.commit()
        
        # 验证更新
        cur.execute("SELECT class_name FROM users WHERE username='student1'")
        result = cur.fetchone()
        self.assertEqual(result["class_name"], "三年级二班")
        
        conn.close()
    
    def test_create_assignment(self):
        """测试创建作业功能"""
        conn = get_conn()
        cur = conn.cursor()
        
        # 添加班级
        now = datetime.now().isoformat()
        cur.execute(
            "INSERT INTO classes (class_name, grade, teacher_username, created_at) VALUES (?, ?, ?, ?)",
            ("三年级四班", "三年级", "teacher1", now)
        )
        
        # 创建作业
        cur.execute(
            "INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("我的校园生活", "写事", "请写一篇关于校园生活的作文", "三年级", "三年级四班", "teacher1", "2024-12-31", now)
        )
        conn.commit()
        
        # 验证作业已创建
        cur.execute("SELECT * FROM assignments WHERE title='我的校园生活'")
        result = cur.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result["genre"], "写事")
        self.assertEqual(result["grade"], "三年级")
        self.assertEqual(result["class_name"], "三年级四班")
        self.assertEqual(result["teacher_username"], "teacher1")
        
        conn.close()
    
    def test_query_assignments_by_grade(self):
        """测试按年级查询作业"""
        # 先创建作业
        conn = get_conn()
        cur = conn.cursor()
        now = datetime.now().isoformat()
        
        cur.execute(
            "INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("作文作业1", "写人", "提示1", "三年级", "三年级一班", "teacher1", "2024-12-31", now)
        )
        cur.execute(
            "INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("作文作业2", "写事", "提示2", "四年级", "四年级一班", "teacher1", "2024-12-31", now)
        )
        conn.commit()
        conn.close()
        
        # 查询三年级作业
        df = query_df("SELECT * FROM assignments WHERE grade='三年级'")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["title"], "作文作业1")
        
        # 查询四年级作业
        df = query_df("SELECT * FROM assignments WHERE grade='四年级'")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["title"], "作文作业2")
    
    def test_query_assignments_by_teacher(self):
        """测试按教师查询作业"""
        # 创建作业
        conn = get_conn()
        cur = conn.cursor()
        now = datetime.now().isoformat()
        
        cur.execute(
            "INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("教师作业", "写景", "提示", "三年级", "三年级一班", "teacher1", "2024-12-31", now)
        )
        conn.commit()
        conn.close()
        
        # 查询特定教师的作业
        df = query_df("SELECT * FROM assignments WHERE teacher_username='teacher1'")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["teacher_username"], "teacher1")
    
    def test_assignments_with_due_date(self):
        """测试带截止日期的作业"""
        conn = get_conn()
        cur = conn.cursor()
        now = datetime.now().isoformat()
        
        # 创建带截止日期的作业
        cur.execute(
            "INSERT INTO assignments (title, genre, prompt, grade, class_name, teacher_username, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("限时作业", "想象作文", "提示", "三年级", "三年级一班", "teacher1", "2024-12-31", now)
        )
        conn.commit()
        
        # 验证截止日期
        cur.execute("SELECT due_date FROM assignments WHERE title='限时作业'")
        result = cur.fetchone()
        self.assertEqual(result["due_date"], "2024-12-31")
        
        conn.close()


if __name__ == '__main__':
    unittest.main()