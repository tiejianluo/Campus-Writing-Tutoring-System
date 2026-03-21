# v1版本功能测试说明 🧪

## 🚀 测试运行方式

### 运行所有测试
在v1文件夹下执行：
```bash
python -m unittest testcode/test_suite.py
```

### 运行单个测试文件
```bash
python -m unittest testcode/test_basic_functions.py
python -m unittest testcode/test_llm_functions.py
```

### 运行特定测试用例
```bash
python -m unittest testcode.test_basic_functions.TestBasicFunctions.test_count_chinese_chars
```

## 📋 测试文件说明

### test_basic_functions.py
测试基础功能函数，包括：
- 中文字符计数
- 回退反馈生成
- 提示构建
- 常量验证

### test_llm_functions.py
测试LLM相关功能，包括：
- OpenAI客户端获取
- 用户提示构建
- LLM调用回退机制
- 修改指导生成

## 🧪 测试用例设计示例

### 示例1：中文字符计数测试

**测试目标**：验证中文字符计数功能的准确性

**预期输入**：
```python
text = "Hello 世界！123中文abc"
```

**预期输出**：
```python
count_chinese_chars(text) == 2
```

**测试代码**：
```python
def test_count_chinese_chars(self):
    self.assertEqual(count_chinese_chars("Hello 世界！123中文abc"), 2)
```

### 示例2：回退反馈测试

**测试目标**：验证短作文的回退反馈生成

**预期输入**：
```python
essay = "很短。"
```

**预期输出**：
```python
feedback = fallback_feedback(essay)
feedback["summary"]  # 包含"篇幅偏短"
feedback["scores"]["细节描写"] == 5
```

**测试代码**：
```python
def test_fallback_feedback_short_essay(self):
    short_essay = "很短。"
    feedback = fallback_feedback(short_essay)
    self.assertIn("篇幅偏短", feedback["summary"])
    self.assertEqual(feedback["scores"]["细节描写"], 5)
```

### 示例3：提示构建测试

**测试目标**：验证用户提示构建的完整性

**预期输入**：
```python
grade = "三年级"
genre = "记叙文"
theme = "难忘的一天"
goal_words = 300
essay = "测试作文内容"
```

**预期输出**：
```python
prompt = build_user_prompt(grade, genre, theme, goal_words, essay)
prompt包含"学生年级：三年级"
prompt包含"作文类型：记叙文"
prompt包含"主题：难忘的一天"
prompt包含"测试作文内容"
```

**测试代码**：
```python
def test_build_user_prompt_structure(self):
    prompt = build_user_prompt("三年级", "记叙文", "难忘的一天", 300, "测试作文内容")
    self.assertIn("学生年级：三年级", prompt)
    self.assertIn("作文类型：记叙文", prompt)
    self.assertIn("主题：难忘的一天", prompt)
    self.assertIn("测试作文内容", prompt)
```

### 示例4：常量验证测试

**测试目标**：验证常量定义的有效性

**预期输入**：无

**预期输出**：
```python
GRADE_OPTIONS是列表且长度大于0
GENRE_OPTIONS是列表且长度大于0
RUBRIC是字典且包含所有评分维度
```

**测试代码**：
```python
def test_constants_validation(self):
    self.assertIsInstance(GRADE_OPTIONS, list)
    self.assertTrue(len(GRADE_OPTIONS) > 0)
    self.assertIsInstance(RUBRIC, dict)
    self.assertTrue(len(RUBRIC) > 0)
```

## 📊 测试统计

| 测试文件 | 测试用例数 | 测试覆盖范围 |
|----------|------------|--------------|
| test_basic_functions.py | 10 | 基础功能、字符计数、回退反馈 |
| test_llm_functions.py | 11 | LLM功能、提示构建、系统提示 |
| **总计** | **21** | **覆盖所有核心功能** |

## 💡 使用建议

1. **开发时测试**：每次修改代码后运行测试，确保功能正常
2. **集成测试**：使用`test_suite.py`运行所有测试
3. **CI/CD集成**：将测试集成到持续集成流程中
4. **测试扩展**：根据新功能添加相应的测试用例

---

**注意**：测试用例设计遵循单元测试原则，每个测试用例独立测试一个功能点，确保测试的准确性和可靠性。