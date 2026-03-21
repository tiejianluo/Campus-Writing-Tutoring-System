# v2版本功能测试说明 🧪

## 🚀 测试运行方式

### 运行所有测试
在v2文件夹下执行：
```bash
python -m unittest testcode/test_suite.py
```

### 运行单个测试文件
```bash
python -m unittest testcode/test_basic_functions.py
python -m unittest testcode/test_llm_functions.py
python -m unittest testcode/test_data_persistence.py
```

### 运行特定测试用例
```bash
python -m unittest testcode.test_data_persistence.TestDataPersistence.test_save_record
```

## 📋 测试文件说明

### test_basic_functions.py
继承自v1版本，测试基础功能函数，包括：
- 中文字符计数
- 回退反馈生成
- 提示构建
- 常量验证

### test_llm_functions.py
继承自v1版本，测试LLM相关功能，包括：
- OpenAI客户端获取
- 用户提示构建
- LLM调用回退机制
- 修改指导生成

### test_data_persistence.py
新增测试文件，测试数据持久化功能，包括：
- 记录加载
- 记录保存
- 记录追加
- JSON文件操作

## 🧪 测试用例设计示例

### 示例1：记录保存测试

**测试目标**：验证学生记录保存功能的正确性

**预期输入**：
```python
student_data = {
    "student_name": "张三",
    "grade": "三年级",
    "essay": "这是一篇测试作文",
    "feedback": {"scores": {"立意与内容": 85}},
    "timestamp": "2024-01-01"
}
```

**预期输出**：
```python
save_record(student_data) 返回 True
记录被保存到 essay_app_records.json 文件中
```

**测试代码**：
```python
def test_save_record(self):
    student_data = {
        "student_name": "张三",
        "grade": "三年级",
        "essay": "这是一篇测试作文",
        "feedback": {"scores": {"立意与内容": 85}},
        "timestamp": "2024-01-01"
    }
    result = save_record(student_data)
    self.assertTrue(result)
    
    # 验证文件存在
    self.assertTrue(os.path.exists("essay_app_records.json"))
    
    # 验证数据已保存
    with open("essay_app_records.json", "r", encoding="utf-8") as f:
        records = json.load(f)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_name"], "张三")
```

### 示例2：记录加载测试

**测试目标**：验证记录加载功能的正确性

**预期输入**：无（从文件加载）

**预期输出**：
```python
load_records() 返回列表
列表中包含之前保存的记录
```

**测试代码**：
```python
def test_load_records(self):
    # 先保存一条记录
    test_record = {
        "student_name": "李四",
        "grade": "四年级",
        "essay": "测试作文",
        "feedback": {"scores": {"立意与内容": 90}},
        "timestamp": "2024-01-02"
    }
    save_record(test_record)
    
    # 加载记录
    records = load_records()
    
    # 验证加载结果
    self.assertIsInstance(records, list)
    self.assertTrue(len(records) >= 1)
    found = False
    for record in records:
        if record["student_name"] == "李四":
            found = True
            break
    self.assertTrue(found)
```

### 示例3：记录追加测试

**测试目标**：验证记录追加功能的正确性

**预期输入**：
```python
record1 = {"student_name": "王五", "grade": "五年级"}
record2 = {"student_name": "赵六", "grade": "六年级"}
```

**预期输出**：
```python
两次调用save_record后，文件中包含2条记录
```

**测试代码**：
```python
def test_record_appending(self):
    # 清空测试文件
    if os.path.exists("essay_app_records.json"):
        os.remove("essay_app_records.json")
    
    # 保存第一条记录
    record1 = {
        "student_name": "王五",
        "grade": "五年级",
        "essay": "作文1",
        "feedback": {"scores": {"立意与内容": 80}},
        "timestamp": "2024-01-03"
    }
    save_record(record1)
    
    # 保存第二条记录
    record2 = {
        "student_name": "赵六",
        "grade": "六年级",
        "essay": "作文2",
        "feedback": {"scores": {"立意与内容": 85}},
        "timestamp": "2024-01-04"
    }
    save_record(record2)
    
    # 验证两条记录都已保存
    records = load_records()
    self.assertEqual(len(records), 2)
    
    names = [r["student_name"] for r in records]
    self.assertIn("王五", names)
    self.assertIn("赵六", names)
```

### 示例4：空文件处理测试

**测试目标**：验证空文件处理的健壮性

**预期输入**：不存在的文件或空文件

**预期输出**：
```python
load_records() 返回空列表
```

**测试代码**：
```python
def test_load_empty_records(self):
    # 确保文件不存在
    if os.path.exists("essay_app_records.json"):
        os.remove("essay_app_records.json")
    
    # 测试加载不存在的文件
    records = load_records()
    self.assertIsInstance(records, list)
    self.assertEqual(len(records), 0)
```

## 📊 测试统计

| 测试文件 | 测试用例数 | 测试覆盖范围 |
|----------|------------|--------------|
| test_basic_functions.py | 10 | 基础功能、字符计数、回退反馈 |
| test_llm_functions.py | 11 | LLM功能、提示构建、系统提示 |
| test_data_persistence.py | 9 | 数据持久化、记录保存、加载 |
| **总计** | **36** | **覆盖所有核心功能** |

## 💡 使用建议

1. **数据隔离**：测试时使用独立的测试数据文件，避免影响生产数据
2. **清理测试数据**：测试完成后清理测试生成的临时文件
3. **边界测试**：测试空文件、异常数据等边界情况
4. **性能测试**：对于大量记录的场景，测试加载和保存的性能

---

**注意**：v2版本的测试继承了v1版本的所有测试用例，并新增了数据持久化相关的测试，确保版本升级后的功能完整性。