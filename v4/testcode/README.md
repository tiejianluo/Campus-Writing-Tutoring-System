# 妙妙作文屋 v4 版本测试文档 🧪

## 🚀 部署方式

### 系统要求
- Python 3.8+
- 跨平台支持（Windows、macOS、Linux）

### 一键运行
在项目根目录下执行：
```python
python testcode\test_suite.py
```

### 功能说明
- 自动检查Python环境和项目依赖（缺少依赖会自动安装）
- 运行完整测试套件
- 自动更新README.md中的测试结果
- 显示测试结果统计和代码覆盖率分析
- 支持运行指定类别的测试：
  - `python testcode\test_suite.py basic` - 运行基础功能测试
  - `python testcode\test_suite.py llm` - 运行LLM功能测试
  - `python testcode\test_suite.py system` - 运行系统集成测试
  - `python testcode\test_suite.py acceptance` - 运行验收测试
  - `python testcode\test_suite.py role` - 运行角色认证测试
  - `python testcode\test_suite.py security` - 运行安全测试
  - `python testcode\test_suite.py performance` - 运行性能测试

## 📊 统计信息

### 测试用例统计

| 测试类型 | 测试文件 | 测试用例数 | 代码行数 |
|----------|----------|------------|----------|
| 单元测试 | test_basic_functions.py | 12 | 145 |
| 单元测试 | test_llm_functions.py | 9 | 115 |
| 系统测试 | test_system_integration.py | 9 | 162 |
| 验收测试 | test_acceptance.py | 13 | 250 |
| 角色认证测试 | test_role_auth.py | 10 | 372 |
| 安全测试 | test_security.py | 7 | 125 |
| 性能测试 | test_performance.py | 4 | 105 |
| **总计** | **7个文件** | **64** | **1742** |

### 代码覆盖率分析

| 类别 | 行数 | 占比 |
|------|------|------|
| 应用功能代码 | 1033 | - |
| 测试代码 | 1742 | - |
| **测试代码覆盖率比例** | - | **1.69:1** |

## 🧪 单元测试设计介绍

### 基础功能测试

#### 1. 文本处理测试
- **设计目标**: 验证文本处理相关功能的准确性和边界情况处理
- **测试用例**:
  - `test_chinese_word_count`: 中文字符计数功能测试
  - `test_chinese_word_count_with_special_chars`: 包含特殊字符的中文字符计数测试
  - `test_chinese_word_count_edge_cases`: 边界情况测试（全角字符、中文标点、混合文本）
  - `test_paragraph_count`: 段落计数功能测试
  - `test_sentence_count`: 句子计数功能测试
- **预期输入**: 各种文本内容
- **预期输出**: 准确的字符数、段落数、句子数

#### 2. 结构分析测试
- **设计目标**: 验证文章结构分析功能的正确性
- **测试用例**:
  - `test_has_beginning_middle_end`: 文章结构完整性检查测试
  - `test_structure_level`: 结构水平评估测试
  - `test_expression_level`: 表达水平评估测试
- **预期输入**: 不同结构的作文内容
- **预期输出**: 结构完整性判断（True/False）、结构水平（较完整/基本完整/待加强）、表达水平（较丰富/一般/待丰富）

#### 3. 得分推断测试
- **设计目标**: 验证得分推断功能的正确性（v3新增）
- **测试用例**:
  - `test_infer_structure_score`: 结构得分推断功能测试
  - `test_infer_expression_score`: 表达得分推断功能测试
- **预期输入**: 作文内容
- **预期输出**: 合理的结构得分和表达得分（60-100分之间）

#### 4. 常量验证测试
- **设计目标**: 验证系统常量定义的有效性和完整性
- **测试用例**:
  - `test_constants_validation`: 常量类型验证（默认主题、作文模板、评分标准等）
  - `test_constants_content_validation`: 常量内容验证（验证各常量包含必要值）
- **预期输入**: 系统常量
- **预期输出**: 验证常量类型正确且包含必要内容

### LLM功能测试

#### 1. 反馈生成测试
- **设计目标**: 验证反馈生成相关功能的正确性
- **测试用例**:
  - `test_fallback_feedback`: 回退反馈功能测试
  - `test_fallback_feedback_short_essay`: 短作文的回退反馈测试
  - `test_fallback_feedback_normal_essay`: 正常长度作文的回退反馈测试
- **预期输入**: 年级、作文类型、主题、作文内容
- **预期输出**: 包含完整结构的反馈字典，短作文包含"字数还可以再充实一些"

#### 2. 主题生成测试
- **设计目标**: 验证主题生成功能的正确性（v3改进）
- **测试用例**:
  - `test_generate_topics`: 生成主题功能测试
- **预期输入**: 年级、作文类型、关键词（可选）
- **预期输出**: 包含多个主题的列表，关键词主题包含指定关键词

#### 3. 范文对比测试
- **设计目标**: 验证范文对比功能的正确性（v3改进）
- **测试用例**:
  - `test_compare_with_model_essay`: 与范文对比功能测试
- **预期输入**: 学生作文、作文类型、主题
- **预期输出**: 包含范文对比提示的字符串

#### 4. 图片提示测试
- **设计目标**: 验证图片提示功能的正确性
- **测试用例**:
  - `test_fallback_image_prompts`: 回退图片提示功能测试
- **预期输入**: 年级
- **预期输出**: 包含场景概括、观察提示、启发问题、推荐题目的提示字典

#### 5. 提示构建测试
- **设计目标**: 验证提示构建功能的正确性（v3新增）
- **测试用例**:
  - `test_build_prompt`: 构建提示功能测试
- **预期输入**: 年级、作文类型、主题、作文内容
- **预期输出**: 包含所有必要信息的提示字符串

#### 6. 年级期望测试
- **设计目标**: 验证年级期望功能的正确性（v3新增）
- **测试用例**:
  - `test_grade_expectation`: 年级期望功能测试
- **预期输入**: 年级
- **预期输出**: 包含年级期望的字符串

#### 7. 评分标准测试
- **设计目标**: 验证评分标准markdown功能的正确性（v3新增）
- **测试用例**:
  - `test_get_rubric_markdown`: 获取评分标准markdown功能测试
- **预期输入**: 年级
- **预期输出**: 包含评分标准的markdown字符串

### 角色认证测试（v3新增）

#### 1. 用户登录测试
- **设计目标**: 验证不同角色用户的登录功能
- **测试用例**:
  - `test_login_user_valid_teacher`: 教师用户登录功能测试
  - `test_login_user_valid_student`: 学生用户登录功能测试
  - `test_login_user_valid_parent`: 家长用户登录功能测试
  - `test_login_user_valid_admin`: 管理员用户登录功能测试
  - `test_login_user_invalid_username`: 无效用户名登录测试
  - `test_login_user_invalid_password`: 无效密码登录测试
- **预期输入**: 用户名、密码
- **预期输出**: 成功登录返回用户信息字典，失败登录返回None

#### 2. 用户注册测试
- **设计目标**: 验证不同角色用户的注册功能
- **测试用例**:
  - `test_register_user_student`: 注册学生用户功能测试
  - `test_register_user_teacher`: 注册教师用户功能测试
  - `test_register_user_parent`: 注册家长用户功能测试
  - `test_register_user_duplicate_username`: 注册重复用户名测试
- **预期输入**: 用户名、密码、角色、真实姓名、年级（学生）、班级（学生）
- **预期输出**: 注册成功返回True，注册失败返回False

## 🔄 系统测试设计介绍

### 完整流程测试

#### 1. 完整作文点评流程测试
- **设计目标**: 验证完整的作文点评流程各模块间的交互
- **测试用例**:
  - `test_full_essay_review_flow`: 完整作文点评流程测试（调用反馈生成功能并验证反馈结构完整性）
- **预期输入**: 年级、作文类型、主题、作文内容
- **预期输出**: 返回包含完整结构的反馈字典

#### 2. 模块集成测试
- **设计目标**: 验证不同模块间的集成正确性
- **测试用例**:
  - `test_character_count_and_feedback_integration`: 字符计数与反馈生成的集成测试
  - `test_module_interaction_consistency`: 不同模块间的交互一致性测试（字符计数、段落计数、句子计数、结构完整性检查、结构水平评估、表达水平评估）
- **预期输入**: 作文内容
- **预期输出**: 不同模块的处理结果保持一致性，返回合理的数值和判断结果

#### 3. 异常处理测试
- **设计目标**: 验证系统在异常情况下的处理能力
- **测试用例**:
  - `test_error_handling_in_integration`: 集成过程中的错误处理测试（空作文处理）
- **预期输入**: 空作文
- **预期输出**: 系统不会崩溃，能返回合理的反馈字典

#### 4. 场景测试
- **设计目标**: 验证不同场景下的完整工作流程
- **测试用例**:
  - `test_full_workflow_with_short_essay`: 短作文场景测试（反馈生成）
  - `test_full_workflow_with_normal_essay`: 正常长度作文场景测试（反馈生成→范文对比）
- **预期输入**: 不同长度的作文
- **预期输出**: 系统能根据作文长度提供相应的反馈

#### 5. 主题生成功能测试
- **设计目标**: 验证主题生成功能的集成正确性（v3改进）
- **测试用例**:
  - `test_topic_generation_integration`: 主题生成功能集成测试
- **预期输入**: 年级、作文类型、关键词（可选）
- **预期输出**: 生成包含关键词的主题列表

#### 6. 结构和表达评估测试
- **设计目标**: 验证结构和表达水平评估功能的正确性
- **测试用例**:
  - `test_structure_and_expression_evaluation`: 结构和表达水平评估测试
- **预期输入**: 作文内容
- **预期输出**: 返回合理的结构水平（较完整/基本完整/待加强）和表达水平（较丰富/一般/待丰富）

#### 7. 得分推断功能测试
- **设计目标**: 验证得分推断功能的集成正确性（v3新增）
- **测试用例**:
  - `test_infer_scores_integration`: 得分推断功能的集成测试
- **预期输入**: 作文内容
- **预期输出**: 合理的结构得分和表达得分（60-100分之间）

## 🎯 验收测试设计介绍

### 用户故事测试

#### 1. 不同年级学生写作场景
- **设计目标**: 验证系统对不同年级学生的支持
- **测试用例**:
  - `test_user_story_grade_3_narrative_essay`: 三年级学生写记叙文的用户故事
  - `test_user_story_grade_5_descriptive_essay`: 五年级学生写写景作文的用户故事
- **预期输入**: 不同年级、不同类型的作文内容
- **预期输出**: 反馈内容符合相应年级水平

#### 2. 特殊情况处理
- **设计目标**: 验证系统对特殊输入的处理能力
- **测试用例**:
  - `test_user_story_short_essay_handling`: 短作文处理的用户故事（验证短作文识别）
  - `test_user_story_empty_input_handling`: 空输入处理的用户故事（验证系统稳定性）
- **预期输入**: 短作文（如"我的好朋友是小明。他很聪明。"）或空作文
- **预期输出**: 短作文反馈包含"字数还可以再充实一些"，空作文不导致系统崩溃，返回合理反馈

#### 3. 复杂作文处理
- **设计目标**: 验证系统处理复杂作文的能力
- **测试用例**:
  - `test_user_story_complex_essay_with_dialogue`: 包含对话的复杂作文的用户故事
- **预期输入**: 包含对话的作文内容
- **预期输出**: 系统能正确处理包含对话的作文并提供有效的反馈

### 验收标准测试

#### 1. 输出格式验证
- **设计目标**: 验证系统输出格式符合预期
- **测试用例**:
  - `test_acceptance_criteria_output_format`: 输出格式验证
- **预期输入**: 作文内容
- **预期输出**: 反馈为字典格式，包含teacher_feedback、student_feedback、strengths、suggestions、polished_sentence、outline_advice、step_rewrite等所有必要字段，各字段类型正确

#### 2. 内容质量验证
- **设计目标**: 验证反馈内容的质量和完整性
- **测试用例**:
  - `test_acceptance_criteria_content_quality`: 内容质量验证（优点、改进建议、句子优化、补写提纲建议的数量）
- **预期输入**: 作文内容
- **预期输出**: 反馈包含至少3条优点、3条改进建议、2条句子优化、3条补写提纲建议

#### 3. 范文对比功能验证
- **设计目标**: 验证范文对比功能的正确性（v3改进）
- **测试用例**:
  - `test_acceptance_criteria_sample_comparison`: 范文对比功能的验收标准
- **预期输入**: 学生作文、作文类型、主题
- **预期输出**: 对比结果包含范文对比提示的字符串

#### 4. 主题生成功能验证
- **设计目标**: 验证主题生成功能的正确性（v3改进）
- **测试用例**:
  - `test_acceptance_criteria_topic_generation`: 主题生成功能的验收标准
- **预期输入**: 年级、作文类型、兴趣关键词（可选）
- **预期输出**: 生成至少3个主题选项，包含指定的关键词

#### 5. 图片提示功能验证
- **设计目标**: 验证图片提示功能的正确性
- **测试用例**:
  - `test_acceptance_criteria_image_prompts`: 图片提示功能的验收标准
- **预期输入**: 年级
- **预期输出**: 图片提示包含scene（场景概括）、observe（4条观察提示）、questions（4条启发问题）、suggested_title（推荐题目）

#### 6. 提示构建功能验证
- **设计目标**: 验证提示构建功能的正确性（v3新增）
- **测试用例**:
  - `test_acceptance_criteria_build_prompt`: 构建提示功能的验收标准
- **预期输入**: 年级、作文类型、主题、作文内容
- **预期输出**: 提示包含所有必要信息（年级、作文类型、主题、作文内容）

#### 7. 年级期望功能验证
- **设计目标**: 验证年级期望功能的正确性（v3新增）
- **测试用例**:
  - `test_acceptance_criteria_grade_expectation`: 年级期望功能的验收标准
- **预期输入**: 年级
- **预期输出**: 返回包含年级期望的字符串

#### 8. 评分标准功能验证
- **设计目标**: 验证评分标准markdown功能的正确性（v3新增）
- **测试用例**:
  - `test_acceptance_criteria_get_rubric_markdown`: 获取评分标准markdown功能的验收标准
- **预期输入**: 年级
- **预期输出**: 返回包含评分标准的markdown字符串

## 🔐 安全测试设计介绍

### 凭据与配置安全

#### 1. 硬编码密钥扫描
- **设计目标**: 防止 API key 或类似凭据进入源码仓库
- **测试用例**:
  - `test_source_does_not_contain_hardcoded_api_keys`: 扫描所有 Python 源码中的 OpenAI 风格硬编码密钥
- **预期输入**: 项目 Python 源码
- **预期输出**: 不存在疑似硬编码密钥

#### 2. 本地密钥文件保护
- **设计目标**: 防止本地 `.env` 和 Streamlit secrets 文件被提交
- **测试用例**:
  - `test_local_secret_files_are_gitignored`: 验证 `.gitignore` 包含 `.env` 和 `.streamlit/secrets.toml`
- **预期输入**: `.gitignore`
- **预期输出**: 本地密钥文件路径被忽略

#### 3. 部署配置读取
- **设计目标**: 验证云端部署可通过环境变量或 Streamlit secrets 注入密钥
- **测试用例**:
  - `test_openai_config_prefers_environment_variables`: 验证环境变量优先生效
  - `test_llm_feedback_falls_back_without_api_key`: 验证缺少 API key 时使用本地回退点评
- **预期输入**: 环境变量和作文文本
- **预期输出**: 配置读取正确，未配置外部模型时系统仍可用

### 认证与输入安全

#### 1. 密码哈希测试
- **设计目标**: 确认密码不会以明文存储
- **测试用例**:
  - `test_password_hash_does_not_store_plaintext`: 验证哈希值不等于明文，且正确/错误密码校验结果符合预期
- **预期输入**: 用户密码
- **预期输出**: 哈希校验安全且准确

#### 2. 登录注入防护
- **设计目标**: 确认登录查询使用参数化 SQL
- **测试用例**:
  - `test_login_rejects_sql_injection_username`: 使用 SQL 注入式用户名尝试登录
- **预期输入**: 恶意用户名
- **预期输出**: 登录失败，正常用户名仍可登录

#### 3. 角色注册边界
- **设计目标**: 防止普通注册入口创建管理员账号
- **测试用例**:
  - `test_register_user_blocks_admin_self_registration`: 尝试通过注册函数创建 admin 用户
- **预期输入**: admin 角色注册请求
- **预期输出**: 注册失败，账号不可登录

## ⚡ 性能测试设计介绍

### 核心本地路径性能

#### 1. 文本指标批量处理
- **设计目标**: 保证字数、段落、句子和评分推断在大文本上仍能快速响应
- **测试用例**:
  - `test_text_metrics_bulk_processing_under_budget`: 对大文本重复执行核心指标计算
- **预期输入**: 多段长作文文本
- **预期输出**: 在本地交互预算内完成

#### 2. 回退反馈批量生成
- **设计目标**: 保证未配置外部模型时，本地反馈路径可支撑课堂批量使用
- **测试用例**:
  - `test_fallback_feedback_bulk_generation_under_budget`: 批量生成本地回退反馈
- **预期输入**: 作文文本
- **预期输出**: 快速返回完整反馈字典

#### 3. 题目生成批量处理
- **设计目标**: 保证个性化题目建议生成不成为页面交互瓶颈
- **测试用例**:
  - `test_topic_generation_bulk_under_budget`: 批量生成带关键词的题目建议
- **预期输入**: 年级、作文类型、关键词
- **预期输出**: 快速返回多个题目选项

#### 4. SQLite 写入回路
- **设计目标**: 验证本地保存作文、版本和成长记录的基本写入性能
- **测试用例**:
  - `test_submission_roundtrip_under_budget`: 在临时数据库中批量保存作文提交
- **预期输入**: 多条作文提交数据
- **预期输出**: 所有提交成功落库且耗时低于预算

## 📊 测试结果可视化

### 测试结果统计

| 测试类型 | 测试文件 | 测试用例数 | 通过数 | 失败数 | 错误数 | 通过率 |
|----------|----------|------------|--------|--------|--------|--------|
| 单元测试 | test_basic_functions.py | 12 | 12 | 0 | 0 | 100.0% |
| 单元测试 | test_llm_functions.py | 9 | 9 | 0 | 0 | 100.0% |
| 系统测试 | test_system_integration.py | 9 | 9 | 0 | 0 | 100.0% |
| 验收测试 | test_acceptance.py | 13 | 13 | 0 | 0 | 100.0% |
| 角色认证测试 | test_role_auth.py | 10 | 10 | 0 | 0 | 100.0% |
| 安全测试 | test_security.py | 7 | 7 | 0 | 0 | 100.0% |
| 性能测试 | test_performance.py | 4 | 4 | 0 | 0 | 100.0% |
| **总计** | **-** | **64** | **64** | **0** | **0** | **100.0%** |

### 测试时间统计

| 测试文件 | 测试时间 | 平均每个测试用例时间 |
|----------|----------|----------------------|
| test_basic_functions.py | 0.002秒 | 0.000秒 |
| test_llm_functions.py | 0.000秒 | 0.000秒 |
| test_system_integration.py | 0.000秒 | 0.000秒 |
| test_acceptance.py | 0.000秒 | 0.000秒 |
| test_role_auth.py | 4.450秒 | 0.445秒 |
| test_security.py | 0.007秒 | 0.001秒 |
| test_performance.py | 0.216秒 | 0.054秒 |
| **总计** | **4.675秒** | **0.073秒** |
