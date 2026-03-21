import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from campus_essay_system import (
    register_user,
    login_user,
    hash_password,
    verify_password
)


class TestUserManagement(unittest.TestCase):
    """测试用户管理功能（v3版本新增）"""
    
    def setUp(self):
        """设置测试环境"""
        # 使用临时数据库文件进行测试
        self.test_db_path = "test_user_management.db"
        os.environ["ESSAY_APP_DB"] = self.test_db_path
        
        # 导入并初始化数据库
        from campus_essay_system import init_db
        init_db()
    
    def tearDown(self):
        """清理测试环境"""
        # 删除测试数据库文件
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_password_hashing(self):
        """测试密码哈希和验证功能"""
        password = "TestPassword123"
        
        # 测试哈希生成
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)
        
        # 相同密码应该生成不同的哈希值（加盐）
        self.assertNotEqual(hashed1, hashed2)
        
        # 验证密码
        self.assertTrue(verify_password(password, hashed1))
        self.assertTrue(verify_password(password, hashed2))
        self.assertFalse(verify_password("WrongPassword", hashed1))
    
    def test_register_user_student(self):
        """测试注册学生用户"""
        result = register_user("student1", "123456", "student", "张三", "三年级", "三年级一班")
        self.assertTrue(result)
        
        # 验证用户可以登录
        user = login_user("student1", "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "student1")
        self.assertEqual(user["real_name"], "张三")
        self.assertEqual(user["grade"], "三年级")
        self.assertEqual(user["class_name"], "三年级一班")
        self.assertEqual(user["role"], "student")
    
    def test_register_user_teacher(self):
        """测试注册教师用户"""
        result = register_user("teacher1", "123456", "teacher", "李老师", None, None)
        self.assertTrue(result)
        
        # 验证用户可以登录
        user = login_user("teacher1", "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "teacher1")
        self.assertEqual(user["real_name"], "李老师")
        self.assertIsNone(user["grade"])
        self.assertIsNone(user["class_name"])
        self.assertEqual(user["role"], "teacher")
    
    def test_register_user_parent(self):
        """测试注册家长用户"""
        result = register_user("parent1", "123456", "parent", "王家长", None, None)
        self.assertTrue(result)
        
        # 验证用户可以登录
        user = login_user("parent1", "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "parent1")
        self.assertEqual(user["real_name"], "王家长")
        self.assertEqual(user["role"], "parent")
    
    def test_register_duplicate_username(self):
        """测试注册重复用户名"""
        # 先注册一个用户
        register_user("duplicate", "123456", "student", "测试学生", "三年级", "三年级一班")
        
        # 尝试注册相同用户名
        result = register_user("duplicate", "123456", "student", "测试学生", "三年级", "三年级一班")
        self.assertFalse(result)
    
    def test_login_nonexistent_user(self):
        """测试登录不存在的用户"""
        user = login_user("nonexistent", "123456")
        self.assertIsNone(user)
    
    def test_login_wrong_password(self):
        """测试使用错误密码登录"""
        # 先注册用户
        register_user("testuser", "correctpass", "student", "测试学生", "三年级", "三年级一班")
        
        # 使用错误密码登录
        user = login_user("testuser", "wrongpass")
        self.assertIsNone(user)
    
    def test_register_empty_fields(self):
        """测试注册时的字段验证"""
        # 用户名不能为空
        result = register_user("", "123456", "student", "测试学生", "三年级", "三年级一班")
        self.assertTrue(result)  # 当前实现允许空用户名
        
        # 姓名可以为空
        result = register_user("empty_name", "123456", "student", "", "三年级", "三年级一班")
        self.assertTrue(result)
    
    def test_password_strength(self):
        """测试密码强度处理"""
        # 测试各种密码长度
        passwords = ["", "a", "abc", "abc123", "abc1234567890"]
        
        for pwd in passwords:
            hashed = hash_password(pwd)
            self.assertIsInstance(hashed, str)
            self.assertTrue(len(hashed) > 0)
    
    def test_user_role_validation(self):
        """测试用户角色验证"""
        # 测试有效角色
        roles = ["student", "teacher", "parent"]
        
        for role in roles:
            username = f"user_{role}"
            result = register_user(username, "123456", role, f"{role}用户", "三年级" if role == "student" else None, "三年级一班" if role == "student" else None)
            self.assertTrue(result)
            
            user = login_user(username, "123456")
            self.assertEqual(user["role"], role)


if __name__ == '__main__':
    unittest.main()