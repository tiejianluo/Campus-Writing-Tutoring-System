# WriteSmart · 写作陪练
**WriteSmart** 是一款专为 K-12 学生设计的 AI 写作伴学系统，让每一个孩子在中英双语写作中，找到表达的勇气与乐趣。
---

<div align="center">

### 面向K12学生的写作伴学系统

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local%20DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-70%20v7%20checks-16A34A?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-v7%20%E8%BF%90%E8%90%A5%E7%89%88-16A34A?style=for-the-badge)

**[English](README.md) / 中文**

[系统概述](#系统概述) - [目标用户](#目标用户) - [运行机制](#运行机制) - [功能特性](#功能特性) - [版本说明](#版本说明) - [本地运行](#本地运行) - [部署](#部署到-streamlit-community-cloud) - [仓库结构](#仓库结构)

</div>

---

## 系统概述

**WriteSmart** 是一款面向 K-12 学段的 AI 写作伴学系统，深度融合人工智能技术与前沿写作教学理念，将枯燥的写作任务转化为一段有温度、有方法的成长旅程。

系统贯穿写作全流程，为每一位学生提供：

- **灵感启航**：通过互动式话题引导与思维导图工具，帮助学生突破“开头难”的困境，找到自己真正想写的话题，让写作从被动完成作业变为主动表达自我。

- **双语自由写作**：全面支持**中文和英文**两种语言的写作练习，尊重各自的语言习惯、句式结构和文化表达方式，让双语学习不再割裂，而是互相滋养。

- **诊断式反馈**：不同于传统打分或笼统评价，AI 提供**“基于标准的建设性反馈”**，从立意构思、篇章结构、语言表达、行文流畅度、用词准确性和书写规范等维度，给出具体可操作的改进建议——既说“哪里好”，也讲“怎么更好”。

- **阶梯式修改**：遵循“先放后收”的写作教学规律，引导学生根据反馈逐步修改、反复打磨，在一次次修改中体会“好文章是改出来的”，真正培养成长型思维。

- **成长档案**：每一篇草稿、每一次修改、每一版反馈，都自动归入个人专属档案。学生可以随时回望自己的进步轨迹，教师和家长也能清晰看到写作能力的纵向发展——哪些方面在提升，哪些环节还需要补一补。

## 核心理念

**WriteSmart 相信：**

每一个孩子都有表达的欲望，只需要被温柔地看见、被正确地引导。AI 不是替代老师，也不仅是批改工具，而是学生身边**一位耐心、专业、从不厌倦的“写作陪练”**——它读懂孩子的作品，也读懂孩子的成长。

## 适用场景

- 课堂写作教学（教师辅助）
- 课后自主练习（学生自驱）
- 双语学校写作课程（中英融合）
- 家庭学习陪伴（家长参与）


本项目基于 Streamlit 实现，并保留七个版本化发布：

- **v1**：轻量级单学生作文辅导工具。
- **v2**：面向课堂的版本，加入作文模板、题目生成、图片提示和本地记录。
- **v3**：完整校园版，支持角色、班级、作业、SQLite 持久化和成长记录。
- **v4**：发布加固版，强化密钥管理、安全测试、性能测试和 Streamlit 部署文档。
- **v5**：模块化重构版（config / storage / services / llm / ui 分层），收紧安全默认值，加入上传限制、限流和分页。
- **v6**：**准上线版**。新增 **K12 小学英语写作**（三—六年级分级题型、双语 AI 精批含逐句语法订正）、修正版**继续改写与版本对比闭环**（版本始终挂在同一篇作文下）、**班级邀请码**注册，以及**免费/会员分层**（免费每天 3 次 AI 点评；会员 26 元/月、288 元/年，扫码下单 + 管理员核销或激活码开通）。附带单元/系统/验收三层测试。
- **v7**：**运营版**。修复人工测试发现的额度问题——免费额度用完后**自动回退到不限次的本地基础点评，不再拦截提交**；每条点评都标注来源与原因（AI 生成 / 额度用完 / 未配置 AI 密钥 / 限流 / AI 出错，错误写入日志）。新增**管理员运营看板**（分角色用户数、提交量、AI 用量、有效会员、收入、近 14 天趋势）、**账号人工开通/注销**（注销后无法登录、数据保留、可重新开通）、密码重置、**AI 状态页（含真实连接测试）**，以及通过 `ESSAY_APP_ADMIN_USER`/`ESSAY_APP_ADMIN_PASSWORD` 自动创建管理员。完整使用说明见 [`v7/README.md`](v7/README.md)。

**代码仓库：** <https://github.com/tiejianluo/Campus-Writing-Tutoring-System>

**测试应用：** <https://campus-essay-system-v7.streamlit.app/>

## 目标用户

| 用户 | 可完成的任务 |
| --- | --- |
| 学生 | 起草作文、获得 AI 反馈、查看范文对比指导、修改作文、查看成长历史。 |
| 教师 | 创建班级、发布作文作业、查看学生提交、跟踪写作进展。 |
| 家长 | 查看学生近期作文和成长趋势，支持家校协同。 |
| 管理员 | 查看总体运营看板，人工开通/注销账号、重置密码，核销订单、生成激活码，检测 AI 服务状态（v7）。 |

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
- **英语写作（v6）**：三—四年级看图写话、自我介绍（30—60 词），五—六年级日记、书信、小故事（60—120 词），提供句型骨架、连接词指导和双语 AI 反馈（含逐句语法拼写订正）。
- 提供 AI 或本地回退反馈，包括优点、建议、句子润色示例、提纲建议和分步修改指导。
- **改写对比闭环（v6）**：点评后可继续改写并保存为同一篇作文的新版本，任意两个版本可左右对比，显示字数与分数变化。
- 提供分年级字数建议和评分标准。
- 支持带关键词的题目生成。
- 支持看图作文观察提示。
- 提供范文对比式写作指导。
- 成长档案记录题目、科目、字数和分数趋势。

### 教师端体验

- 创建班级并自动生成**邀请码（v6）**：学生注册时填码即自动加入正确班级。
- 发布作文作业，包括题目、类型、科目（语文/英语）、说明、年级、班级和截止日期；作业连同布置说明推送到学生端，教师可查看已布置历史。
- 查看本班学生提交（按教师班级隔离），包括作文文本、分数、教师反馈和学生反馈。
- 批量浏览学生作文情况。

### 会员体系（v6，v7 修正语义）

- 免费版：注册、写作、模板、成长档案，每天 3 次 AI 点评（本地基础点评始终不限次；v7 起额度用完自动回退基础点评，作文照常保存，并明确提示原因）。
- 会员（**26 元/月、288 元/年**）：不限次 AI 点评、英语 AI 精批与语法订正、看图作文、继续改写与版本对比。
- 支付流程：会员中心生成订单号并展示收款二维码，管理员确认到账后自动开通；也支持一次性激活码。新注册学生赠送 7 天体验。
- 注意：**AI 点评需要配置 `OPENAI_API_KEY`**，否则所有点评均为本地基础点评。管理员端「AI 状态」页可检测配置与连通性。

### 管理后台（v7）

- **总体运营**：注册用户（按角色）、近 7 天新增、作文提交总数/今日、AI 点评次数、有效会员、已核销收入、待核销订单、近 14 天提交趋势。
- **账号管理**：人工开通教师/家长/管理员/学生账号；注销账号（停用登录、数据保留、可重新开通）；重置密码。管理员不能注销自己。
- **AI 状态**：显示密钥配置、模型、最近成功/失败记录，一键真实调用测试。

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

| 功能 | v1 | v2 | v3 | v4 | v5 | v6 |
| --- | --- | --- | --- | --- | --- | --- |
| 基础作文反馈 | 是 | 是 | 是 | 是 | 是 | 是 |
| 分年级评分标准 | 否 | 是 | 是 | 是 | 是 | 是 |
| 作文模板 | 否 | 是 | 是 | 是 | 是 | 是 |
| 范文对比指导 | 否 | 是 | 是 | 是 | 是 | 是 |
| 分步修改 | 是 | 是 | 是 | 是 | 是 | 是 |
| 本地数据持久化 | 否 | 是 | 是 | 是 | 是 | 是 |
| 成长记录 | 否 | 是 | 是 | 是 | 是 | 是 |
| 看图作文提示 | 否 | 是 | 是 | 是 | 是 | 是 |
| 题目生成 | 否 | 是 | 是 | 是 | 是 | 是 |
| 用户账号 | 否 | 否 | 是 | 是 | 是 | 是 |
| 教师、学生、家长、管理员角色 | 否 | 否 | 是 | 是 | 是 | 是 |
| 班级管理 | 否 | 否 | 是 | 是 | 是 | 是 |
| 作业发布 | 否 | 否 | 是 | 是 | 是 | 是 |
| SQLite 数据库 | 否 | 否 | 是 | 是 | 是 | 是 |
| Streamlit secrets 支持 | 否 | 否 | 是 | 是 | 是 | 是 |
| 安全测试 | 否 | 否 | 是 | 是 | 是 | 是 |
| 性能测试 | 否 | 否 | 是 | 是 | 否 | 否 |
| 模块化分层架构 | 否 | 否 | 否 | 否 | 是 | 是 |
| 上传限制与限流 | 否 | 否 | 否 | 否 | 是 | 是 |
| 公开注册仅限学生 | 否 | 否 | 否 | 否 | 是 | 是 |
| 学生端展示作业要求 | 否 | 否 | 否 | 否 | 否 | 是 |
| 继续改写（版本制）+ 版本对比 | 否 | 否 | 否 | 否 | 否 | 是 |
| K12 英语写作（三—六年级） | 否 | 否 | 否 | 否 | 否 | 是 |
| 班级邀请码 | 否 | 否 | 否 | 否 | 否 | 是 |
| 免费/会员分层（26 元/月、288 元/年） | 否 | 否 | 否 | 否 | 否 | 是 |
| 单元/系统/验收三层测试 | 否 | 否 | 否 | 否 | 否 | 是 |

v7 在 v6 全部功能之上新增：额度用完回退不限次基础点评、点评来源/原因标注与错误日志、管理员运营看板、账号人工开通/注销与密码重置、AI 状态页（真实连接测试）、启动时自动创建管理员。

### 版本摘要

| 版本 | 定位 | 主文件 | 测试数 |
| --- | --- | --- | --- |
| v1 | 面向个人使用的最小作文辅导工具 | `v1/elementary_essay_tutor_app.py` | 38 |
| v2 | 带模板和本地记录的课堂作文助手 | `v2/elementary_essay_tutor_app_v2.py` | 49 |
| v3 | 支持角色、班级、作业和 SQLite 的完整校园系统 | `v3/campus_essay_system.py` | 64 |
| v4 | 面向 GitHub 和 Streamlit 部署的发布加固版 | `v4/campus_essay_system.py` | 64 |
| v5 | 面向扩展的模块化安全加固重构版 | `v5/campus_essay_system.py` | 19 |
| v6 | 准上线版：英语写作、改写闭环、会员体系 | `v6/campus_essay_system.py` | 61 |
| **v7** | **运营版：额度回退修正、运营看板、账号管理** | `v7/campus_essay_system.py` | **70** |
| latest | 根目录部署版本，与 v4 加固校园版保持一致 | `campus_essay_system.py` | 64 |

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

运行 v7 运营版（推荐）：

```bash
cd v7
pip install -r requirements.txt
streamlit run campus_essay_system.py
```

启用 AI 点评并创建管理员（启动前配置）：

```bash
export OPENAI_API_KEY='sk-...'
export ESSAY_APP_ADMIN_USER='admin'
export ESSAY_APP_ADMIN_PASSWORD='一个至少8位的强密码'
```

分角色（学生/老师/家长/管理员）的完整**使用说明**见 [`v7/README.md`](v7/README.md)。

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

v6 新增配置项（均为可选）：

```text
ESSAY_APP_SEED_DEMO_USERS   # 设为 1 创建本地演示账号（默认关闭）
ESSAY_APP_DEMO_PASSWORD     # 演示账号密码
FREE_AI_DAILY_QUOTA         # 免费版每日 AI 点评次数（默认 3）
PREMIUM_PRICE_MONTH         # 月度会员价格，默认 26（元）
PREMIUM_PRICE_YEAR          # 年度会员价格，默认 288（元）
PREMIUM_TRIAL_DAYS          # 新学生试用天数（默认 7）
PAYMENT_QR_MONTH_URL        # 月度订单展示的收款二维码图片
PAYMENT_QR_YEAR_URL         # 年度订单展示的收款二维码图片
```

v7 新增配置项：

```text
ESSAY_APP_ADMIN_USER        # 引导管理员用户名（启动时不存在则自动创建）
ESSAY_APP_ADMIN_PASSWORD    # 引导管理员密码（至少 8 位）
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
   - v7 运营版（推荐）：`v7/campus_essay_system.py`
   - v6 准上线版：`v6/campus_essay_system.py`
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

运行 v7 三层测试套件（单元 + 系统 + 验收）：

```bash
cd v7
python -m unittest discover -s testcode -p 'test_*.py'   # 全部 70 个测试
python -m unittest testcode.test_unit_core               # 单元测试
python -m unittest testcode.test_system_flows            # 系统测试（含管理后台）
python -m unittest testcode.test_acceptance              # 验收测试
```

v6 验收测试与 2026 年 6 月人工测试报告的缺陷编号（A2—A5、B1—B4）逐条对应，
并覆盖安全边界与商业需求（免费额度、26/288 定价）。

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
| v5 | 19 个测试通过 |
| v6 | 61 个测试通过（单元 + 系统 + 验收） |
| v7 | 70 个测试通过（单元 + 系统 + 验收） |
| 根目录最新版本 | 64 个测试通过 |

## 仓库结构

```text
Campus-Writing-Tutoring-System/
|-- campus_essay_system.py          # 根目录部署应用（与 v4 一致）
|-- requirements.txt                # Python 依赖
|-- packages.txt                    # Streamlit Cloud apt 依赖
|-- testcode/                       # 根目录测试套件
|-- To_Do.md                        # 路线图：缺陷修复、上线、会员体系
|-- v1/                             # 最小作文辅导工具
|-- v2/                             # 课堂作文助手
|-- v3/                             # 完整校园系统快照
|-- v4/                             # 发布加固系统快照
|-- v5/                             # 模块化安全加固重构版
|-- v6/                             # 准上线版：英语写作、改写闭环、
|                                   #   班级邀请码、会员体系
`-- v7/                             # 运营版：额度回退修正、运营看板、
                                    #   账号开通/注销、AI 状态诊断
```

## 安全说明

- API key 不存储在源码中。
- 密钥应通过环境变量或 Streamlit secrets 配置。
- 密码在存储前会进行哈希处理（bcrypt；v5/v6 回退方案为加盐 PBKDF2）。
- 登录查询使用参数化 SQL；v6 对登录尝试做了限流。
- 自助注册：v1—v4 允许学生、教师、家长；**v5/v6 仅限学生**（教师和家长由管理员创建，学生凭班级邀请码入班）。
- v5/v6 强制上传大小/像素限制、LLM 调用超时和按用户限流。
- v5/v6 默认不创建演示账号，仅可通过环境变量开启。
- 安全测试会扫描 OpenAI 风格的硬编码密钥。

## 教育价值

本系统旨在支持写作教学，而不是替代教师。它最适合作为形成性辅导工具，为学生提供即时反馈，同时帮助教师和家长了解仍需指导的地方。
