# v3版本功能测试说明 🧪

## 🚀 测试运行方式

### 运行所有测试
在v3文件夹下执行：
```bash
python -m unittest testcode/test_suite.py
```

### 运行单个测试文件
```bash
python -m unittest testcode/test_basic_functions.py
python -m unittest testcode/test_llm_functions.py
python -m unittest testcode/test_data_persistence.py
python -m unittest testcode/test_ocr_pdf_functions.py
python -m unittest testcode/test_user_management.py
python -m unittest testcode/test_class_assignment.py
```

### 运行特定测试用例
```bash
python -m unittest testcode.test_user_management.TestUserManagement.test_register_user
```

## 📋 测试文件说明

### test_basic_functions.py
继承自v2版本，测试基础功能函数，包括：
- 中文字符计数
- 回退反馈生成
- 提示构建
- 常量验证

### test_llm_functions.py
继承自v2版本，测试LLM相关功能，包括：
- OpenAI客户端获取
- 用户提示构建
- LLM调用回退机制
- 修改指导生成

### test_data_persistence.py
继承自v2版本，测试数据持久化功能，包括：
- 记录加载
- 记录保存
- 记录追加
- JSON文件操作

### test_ocr_pdf_functions.py
新增测试文件，测试OCR和PDF生成功能，包括：
- OCR文字识别
- PDF评语单生成
- 文件操作

### test_user_management.py
新增测试文件，测试用户管理功能，包括：
- 用户注册
- 用户登录
- 密码哈希
- 权限验证

### test_class_assignment.py
新增测试文件，测试班级管理和作业功能，包括：
- 班级创建
- 作业布置
- 作业提交
- 作业评分

## 🧪 测试用例设计示例

### 示例1：用户注册测试

**测试目标**：验证用户注册功能的正确性

**预期输入**：
```python
username = "teacher1"
password = "123456"
role = "teacher"
```

**预期输出**：
```python
register_user(username, password, role) 返回 True
用户被保存到数据库中
密码被加密存储
```

**测试代码**：
```python
def test_register_user(self):
    username = "teacher1"
    password = "123456"
    role = "teacher"
    
    # 注册用户
    result = register_user(username, password, role)
    self.assertTrue(result)
    
    # 验证用户已保存
    with sqlite3.connect("essay_campus_system.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        self.assertIsNotNone(user)
        self.assertEqual(user[2], role)
        self.assertNotEqual(user[3], password)  # 密码已加密
```

### 示例2：用户登录测试

**测试目标**：验证用户登录功能的正确性

**预期输入**：
```python
username = "student1"
password = "123456"
```

**预期输出**：
```python
login_user(username, password) 返回用户信息字典
密码验证成功
```

**测试代码**：
```python
def test_login_user(self):
    # 先注册用户
    register_user("student1", "123456", "student")
    
    # 测试登录
    user = login_user("student1", "123456")
    self.assertIsNotNone(user)
    self.assertEqual(user["username"], "student1")
    self.assertEqual(user["role"], "student")
    
    # 测试错误密码
    user = login_user("student1", "wrong_password")
    self.assertIsNone(user)
```

### 示例3：班级创建测试

**测试目标**：验证班级创建功能的正确性

**预期输入**：
```python
class_name = "三年级1班"
teacher_id = 1
```

**预期输出**：
```python
create_class(class_name, teacher_id) 返回班级ID
班级信息被保存到数据库中
```

**测试代码**：
```python
def test_create_class(self):
    class_name = "三年级1班"
    teacher_id = 1
    
    # 创建班级
    class_id = create_class(class_name, teacher_id)
    self.assertIsInstance(class_id, int)
    self.assertGreater(class_id, 0)
    
    # 验证班级已保存
    with sqlite3.connect("essay_campus_system.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes WHERE class_name = ?", (class_name,))
        class_info = cursor.fetchone()
        
        self.assertIsNotNone(class_info)
        self.assertEqual(class_info[2], teacher_id)
```

### 示例4：作业布置测试

**测试目标**：验证作业布置功能的正确性

**预期输入**：
```python
class_id = 1
assignment_title = "我的周末"
description = "写一篇关于周末生活的作文"
due_date = "2024-01-31"
```

**预期输出**：
```python
assign_homework(class_id, assignment_title, description, due_date) 返回作业ID
作业信息被保存到数据库中
```

**测试代码**：
```python
def test_assign_homework(self):
    class_id = 1
    assignment_title = "我的周末"
    description = "写一篇关于周末生活的作文"
    due_date = "2024-01-31"
    
    # 布置作业
    assignment_id = assign_homework(class_id, assignment_title, description, due_date)
    self.assertIsInstance(assignment_id, int)
    self.assertGreater(assignment_id, 0)
    
    # 验证作业已保存
    with sqlite3.connect("essay_campus_system.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assignments WHERE assignment_title = ?", (assignment_title,))
        assignment = cursor.fetchone()
        
        self.assertIsNotNone(assignment)
        self.assertEqual(assignment[2], class_id)
        self.assertEqual(assignment[4], due_date)
```

### 示例5：OCR识别测试

**测试目标**：验证OCR文字识别功能

**预期输入**：
```python
image_path = "test_image.png"  # 包含文字的测试图片
```

**预期输出**：
```python
extract_text_from_image(image_path) 返回识别的文本
```

**测试代码**：
```python
def test_ocr_text_extraction(self):
    # 使用测试图片
    image_path = "test_image.png"
    
    # 确保测试图片存在
    if os.path.exists(image_path):
        # 测试OCR识别
        text = extract_text_from_image(image_path)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)
    else:
        # 如果测试图片不存在，跳过测试
        self.skipTest("测试图片不存在")
```

### 示例6：PDF生成测试

**测试目标**：验证PDF评语单生成功能

**预期输入**：
```python
student_name = "张三"
grade = "三年级"
essay = "测试作文内容"
feedback = {"scores": {"立意与内容": 85}}
output_path = "test_output.pdf"
```

**预期输出**：
```python
generate_pdf_report(student_name, grade, essay, feedback, output_path) 返回 True
PDF文件被生成
```

**测试代码**：
```python
def test_pdf_report_generation(self):
    student_name = "张三"
    grade = "三年级"
    essay = "测试作文内容"
    feedback = {"scores": {"立意与内容": 85}}
    output_path = "test_output.pdf"
    
    # 生成PDF
    result = generate_pdf_report(student_name, grade, essay, feedback, output_path)
    self.assertTrue(result)
    
    # 验证PDF文件存在
    self.assertTrue(os.path.exists(output_path))
    
    # 清理测试文件
    os.remove(output_path)
```

## 📊 测试统计

| 测试文件 | 测试用例数 | 测试覆盖范围 |
|----------|------------|--------------|
| test_basic_functions.py | 10 | 基础功能、字符计数、回退反馈 |
| test_llm_functions.py | 11 | LLM功能、提示构建、系统提示 |
| test_data_persistence.py | 9 | 数据持久化、记录保存、加载 |
| test_ocr_pdf_functions.py | 6 | OCR识别、PDF生成 |
| test_user_management.py | 10 | 用户注册、登录、权限 |
| test_class_assignment.py | 8 | 班级管理、作业布置、提交 |
| **总计** | **55** | **覆盖所有核心功能** |

## 💡 使用建议

1. **数据库隔离**：测试时使用独立的测试数据库，避免影响生产数据
2. **资源清理**：测试完成后清理生成的临时文件和测试数据
3. **边界测试**：测试空输入、异常数据等边界情况
4. **性能测试**：对于大量用户和班级的场景，测试系统性能
5. **安全测试**：测试用户权限验证和密码安全性

---

**注意**：v3版本的测试继承了v2版本的所有测试用例，并新增了OCR、用户管理和班级作业相关的测试，确保版本升级后的功能完整性和系统稳定性。