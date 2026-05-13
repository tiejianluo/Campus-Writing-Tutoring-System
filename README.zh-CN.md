# AI驱动

---

<div align="center">

### 面向小学写作教学系统

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local%作文辅导系统20DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-64%20v4%20checks-16A34A?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Release%20Hardened-F59E0B?style=for-the-badge)

**[English](README.md) / 中文**

[项目概览](#项目概览) - [目标用户](#目标用户) - [运行机制](#运行机制) - [功能特性](#功能特性) - [版本说明](#版本说明) - [本地运行](#本地运行) - [部署](#部署到-streamlit-community-cloud) - [仓库结构](#仓库结构)

</div>

---

## 项目概览

**作文辅导系统** 是一个面向小学写作教学的 AI 写作助手。它支持学生选题、起草作文、获得形成性反馈、按步骤修改，并持续记录写作成长轨迹。

本项目基于 Streamlit 实现，并保留四个版本化发布：

- **v1**：轻量级单学生作文辅导工具。
- **v2**：面向课堂的版本，加入作文模板、题目生成、图片提示和本地记录。
- **v3**：完整校园版，支持角色、班级、作业、SQLite 持久化和成长记录。
- **v4**：发布加固版，强化密钥管理、安全测试、性能测试和 Streamlit 部署文档。

**公开仓库：** <https://github.com/tiejianluo/Campus-Writing-Tutoring-System>

**公开应用：** <https://campus-essay-system.streamlit.app/>

## 目标用户

| 用户 | 可完成的任务 |
| --- | --- |
| 学生 | 起草作文、获得 AI 反馈、查看范文对比指导、修改作文、查看成长历史。 |
| 教师 | 创建班级、发布作文作业、查看学生提交、跟踪写作进展。 |
| 家长 | 查看学生近期作文和成长趋势，支持家校协同。 |
| 管理员 | 在完整校园版本中查看用户和班级数据。 |

## 运行机制

1. 学生选择年级、作文类型和题目，或从教师布置的作业开始。
2. 学生输入或上传作文草稿。
3. 系统分析字数、结构、表达、年级要求和评分标准匹配度。
4. 如果配置了 LLM 密钥，应用调用模型生成 JSON 反馈；如果未配置密钥，则使用本地回退反馈引擎。
5. 系统展示教师版反馈和学生友好版反馈。
6. 应用保存提交记录、历史版本、评分和成长记录。

## 功能特性

### 学生端体验

- 支持记叙文、写人、写景、想象作文、读后感、日记、看图作文等常见小学作文类型。
- 提供 AI 或本地回退反馈，包括优点、建议、句子润色示例、提纲建议和分步修改指导。
- 提供分年级字数建议和评分标准。
- 支持带关键词的题目生成。
- 支持看图作文观察提示。
- 提供范文对比式写作指导。
- 通过字数和分数趋势展示成长记录。

### 教师端体验

- 创建和管理班级。
- 发布作文作业，包括题目、类型、说明、年级、班级和截止日期。
- 查看学生提交，包括作文文本、分数、教师反馈和学生反馈。
- 批量浏览学生作文情况。

### 技术设计

- Streamlit Web 界面。
- v3/v4 校园版使用 SQLite 持久化数据。
- 可选接入 OpenAI 兼容模型。
- 支持 Streamlit secrets 和环境变量配置。
- 未配置外部 AI 密钥时可自动使用本地回退反馈。
- 安全检查覆盖硬编码密钥、密码哈希、角色注册边界和 SQL 注入防护。
- 性能检查覆盖文本指标、本地反馈、题目生成和 SQLite 提交路径。

## 版本说明

### 功能矩阵

| 功能 | v1 | v2 | v3 | v4 |
| --- | --- | --- | --- | --- |
| 基础作文反馈 | 是 | 是 | 是 | 是 |
| 分年级评分标准 | 否 | 是 | 是 | 是 |
| 作文模板 | 否 | 是 | 是 | 是 |
| 范文对比指导 | 否 | 是 | 是 | 是 |
| 分步修改 | 是 | 是 | 是 | 是 |
| 本地数据持久化 | 否 | 是 | 是 | 是 |
| 成长记录 | 否 | 是 | 是 | 是 |
| 看图作文提示 | 否 | 是 | 是 | 是 |
| 题目生成 | 否 | 是 | 是 | 是 |
| 用户账号 | 否 | 否 | 是 | 是 |
| 教师、学生、家长、管理员角色 | 否 | 否 | 是 | 是 |
| 班级管理 | 否 | 否 | 是 | 是 |
| 作业发布 | 否 | 否 | 是 | 是 |
| SQLite 数据库 | 否 | 否 | 是 | 是 |
| Streamlit secrets 支持 | 否 | 否 | 是 | 是 |
| 安全测试 | 否 | 否 | 是 | 是 |
| 性能测试 | 否 | 否 | 是 | 是 |

### 版本摘要

| 版本 | 定位 | 主文件 | 测试数 |
| --- | --- | --- | --- |
| v1 | 面向个人使用的最小作文辅导工具 | `v1/elementary_essay_tutor_app.py` | 38 |
| v2 | 带模板和本地记录的课堂作文助手 | `v2/elementary_essay_tutor_app_v2.py` | 49 |
| v3 | 支持角色、班级、作业和 SQLite 的完整校园系统 | `v3/campus_essay_system.py` | 64 |
| v4 | 面向 GitHub 和 Streamlit 部署的发布加固版 | `v4/campus_essay_system.py` | 64 |
| latest | 根目录部署版本，与加固校园版保持一致 | `campus_essay_system.py` | 64 |

## 本地运行

### 环境要求

- Python 3.8 或更高版本
- 如果使用外部 AI 模型，需要网络访问
- 可选：OpenAI 兼容 API key，用于实时模型反馈

### 安装依赖

在仓库根目录运行：

```bash
pip install -r requirements.txt
```

运行固定版本：

```bash
cd v4
pip install -r requirements.txt
```

### 启动应用

运行根目录最新版本：

```bash
streamlit run campus_essay_system.py
```

运行固定版本：

```bash
cd v3
streamlit run campus_essay_system.py
```

```bash
cd v4
streamlit run campus_essay_system.py
```

然后打开：

```text
http://localhost:8501
```

## 配置

即使没有外部 AI 凭据，应用也会使用本地回退反馈正常运行。如需启用实时模型反馈，可通过环境变量或 Streamlit Community Cloud secrets 配置密钥。

支持的配置项：

```text
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
SUPABASE_URL
SUPABASE_KEY
ESSAY_APP_DB
```

不要提交本地密钥文件。仓库已忽略：

```text
.env
.streamlit/secrets.toml
```

## 部署到 Streamlit Community Cloud

1. 将仓库推送到 GitHub。
2. 打开 <https://share.streamlit.io>。
3. 选择 GitHub 仓库和分支。
4. 设置主文件路径：
   - 根目录最新应用：`campus_essay_system.py`
   - 固定 v3 应用：`v3/campus_essay_system.py`
   - 固定 v4 应用：`v4/campus_essay_system.py`
5. 确认所选应用路径下存在 `requirements.txt` 和 `packages.txt`。
6. 如果使用实时模型或 Supabase 集成，在 Advanced settings 中添加 secrets。
7. 部署后验证登录、作文反馈、看图作文提示、作业创建和成长记录。

Streamlit 官方参考：

- [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [File organization](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

## 测试

运行根目录最新测试套件：

```bash
python testcode/test_suite.py
```

运行固定版本测试套件：

```bash
cd v4
python testcode/test_suite.py
```

运行指定 v4 测试类别：

```bash
python testcode/test_suite.py basic
python testcode/test_suite.py llm
python testcode/test_suite.py system
python testcode/test_suite.py acceptance
python testcode/test_suite.py role
python testcode/test_suite.py security
python testcode/test_suite.py performance
```

当前验证结果：

| 套件 | 结果 |
| --- | --- |
| v1 | 38 个测试通过 |
| v2 | 49 个测试通过 |
| v3 | 64 个测试通过 |
| v4 | 64 个测试通过 |
| 根目录最新版本 | 64 个测试通过 |

## 仓库结构

```text
Campus-Writing-Tutoring-System/
|-- campus_essay_system.py          # 根目录最新校园应用
|-- requirements.txt                # Python 依赖
|-- packages.txt                    # Streamlit Cloud apt 依赖
|-- testcode/                       # 根目录最新测试套件
|-- v1/                             # 最小作文辅导工具
|-- v2/                             # 课堂作文助手
|-- v3/                             # 完整校园系统快照
`-- v4/                             # 发布加固系统快照
```

## 安全说明

- API key 不存储在源码中。
- 密钥应通过环境变量或 Streamlit secrets 配置。
- 密码在存储前会进行哈希处理。
- 登录查询使用参数化 SQL。
- 自助注册仅限学生、教师和家长角色。
- 安全测试会扫描 OpenAI 风格的硬编码密钥。

## 教育价值

本系统旨在支持写作教学，而不是替代教师。它最适合作为形成性辅导工具，为学生提供即时反馈，同时帮助教师和家长了解仍需指导的地方。

