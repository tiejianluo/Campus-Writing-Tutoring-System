# v5 生产部署与大规模服务验证论证

## 结论

v5 已经从单文件原型改为可测试、可替换、可扩展的生产候选版本。它具备进入预生产环境验证的基础，但不能仅凭本地单元测试断言“已经满足大规模服务”。真正的证明应由三层证据组成：

1. 架构证据：代码结构支持横向扩展、替换存储、替换限流器、隔离权限和控制资源消耗。
2. 自动化测试证据：关键安全边界、上传边界、分页查询、限流和服务流程在本地测试中可重复验证。
3. 预生产运行证据：在接近真实配置的环境中完成压测、安全扫描、故障演练、监控告警和容量评估。

当前仓库已经完成第 1 层和第 2 层的基础证明；第 3 层需要在真实部署环境中执行。

## 被验证对象

入口文件：

- `campus_essay_system.py`

核心模块：

- `app/config.py`：集中管理环境配置、分页大小、上传限制、LLM 限流参数。
- `app/storage.py`：存储层封装。当前实现为 `SQLiteStore`，接口可替换为 Postgres/Supabase。
- `app/services.py`：业务服务层，负责注册、登录、作文点评保存等业务动作。
- `app/llm.py`：LLM 调用、fallback、超时和基础限流。
- `app/uploads.py`：文本/图片上传大小、像素和模型图片压缩。
- `app/responsive.py`：桌面、平板、iOS 和 Android 的响应式布局与触控适配。
- `app/ui.py`：Streamlit UI，只调用服务层，不直接写 SQL。
- `testcode/`：v5 独立测试目录。

## 根目录原型的生产风险

根目录 `campus_essay_system.py` 是典型单文件 Streamlit 原型，适合演示和小范围试用，但不适合直接承载大规模访问：

| 风险 | 影响 | v5 改进 |
|---|---|---|
| UI、数据库、LLM、上传、认证混在单文件 | 难测试、难扩容、难替换组件 | 拆成配置、存储、服务、LLM、上传、UI 模块 |
| 本地 SQLite 文件承担所有读写 | 多实例部署时无法共享状态，写入并发受限 | 通过 `SQLiteStore` 隔离存储接口，生产可替换 Postgres/Supabase |
| 多处全表查询和 DataFrame 全量加载 | 数据量增长后响应变慢、内存升高 | 常用列表接口分页，常用过滤列建索引 |
| 同步 LLM 调用阻塞页面 | 高峰期 worker 被占满，用户等待时间不可控 | LLM 层集中封装，带超时、fallback 和限流；生产可替换为异步队列 |
| 上传文件缺少资源边界 | 大文件或超高像素图片可能导致内存压力 | 上传模块限制文本大小、图片字节数、图片像素和模型图片尺寸 |
| 老师/家长权限范围过宽 | 学生作文和成长数据泄露 | 存储层提供教师班级范围查询、家长绑定学生查询 |
| 默认账号和弱密码风险 | 公网部署暴露管理入口 | v5 默认不创建演示账号，公开注册只允许学生账号 |

## 架构论证

### 1. 可替换存储层

`app/storage.py` 将所有数据库读写收敛到 `SQLiteStore`。UI 和业务层不直接依赖 `sqlite3`，而是调用 `AppService` 或 `SQLiteStore` 方法。

这意味着生产迁移时可以新增 `PostgresStore` 或 `SupabaseStore`，保持方法签名一致：

- `authenticate`
- `create_user`
- `list_teacher_submissions`
- `save_submission`
- `list_parent_students`
- `latest_submission_for_parent`

验收标准：

- UI 模块不直接 import `sqlite3`。
- 入口文件保持很薄，只负责调用 UI main。
- 存储层查询使用参数化 SQL。
- 常用列表查询必须分页。

当前测试：

- `test_architecture.py::test_streamlit_entrypoint_is_thin`
- `test_architecture.py::test_ui_module_does_not_import_sqlite`
- `test_storage_security.py::test_schema_has_indexes_for_common_scoped_queries`

### 2. 权限隔离

大规模学校场景中，数据隔离比功能可用更重要。v5 把权限范围写入存储查询，而不是只靠页面隐藏。

教师查询：

- `list_teacher_submissions(teacher_username, limit, offset)` 只返回该教师负责班级内学生提交。
- `get_submission_for_teacher(teacher_username, submission_id)` 验证提交是否属于该教师班级。

家长查询：

- `parent_student_links` 表显式绑定家长和学生。
- `latest_submission_for_parent(parent_username, student_username)` 只有绑定关系存在才返回数据。

当前测试：

- `test_storage_security.py::test_teacher_submission_query_is_scoped_to_owned_classes`
- `test_storage_security.py::test_parent_query_requires_explicit_link`

### 3. 资源边界

大规模服务不能让单个请求无限消耗内存、CPU 或外部模型额度。v5 在配置层和上传层设定边界：

- `max_text_upload_bytes`
- `max_image_upload_bytes`
- `max_image_pixels`
- `max_model_image_side`
- `max_essay_chars`
- `llm_requests_per_minute`

当前测试：

- `test_uploads_llm.py::test_text_upload_size_limit`
- `test_uploads_llm.py::test_image_upload_pixel_limit_and_compression`
- `test_uploads_llm.py::test_rate_limiter_blocks_after_limit`
- `test_metrics_services.py::test_service_rejects_overlong_essay`

### 4. LLM 服务可控

v5 将模型调用集中到 `LLMService`：

- 没有 API key 时使用本地 fallback。
- 模型调用异常时使用 fallback。
- 每次调用设置 timeout。
- 通过 `FixedWindowRateLimiter` 限制基础调用频率。

生产建议：

- 单机限流器只能用于本地或单副本部署。
- 多副本部署应替换为 Redis 限流。
- 大规模场景应使用任务队列，将作文点评改为异步处理。

当前测试：

- `test_uploads_llm.py::test_llm_fallback_without_key_and_prompt_content`
- `test_uploads_llm.py::test_rate_limiter_blocks_after_limit`

### 5. 最小化依赖

v5 运行时依赖保持最小集合：

```txt
streamlit>=1.32,<2
pandas>=2,<3
pillow>=10,<12
openai>=1,<2
bcrypt>=4,<5
```

当前测试：

- `test_architecture.py::test_requirements_are_runtime_minimal`

生产补充：

- CI 中应加入依赖漏洞扫描，例如 `pip-audit -r requirements.txt`。
- 生产应使用锁文件或构建镜像固定解析后的完整依赖树。

## 当前自动化验证结果

本地已执行：

```bash
cd /home/ad/c2luo/tjl/Campus-Writing-Tutoring-System/v5
python -m unittest discover -s testcode -p 'test_*.py'
```

结果：

```text
Ran 19 tests in 0.730s
OK
```

这些测试证明：

- 模块边界符合 v5 架构目标。
- 默认不会创建公开演示账号。
- 演示账号必须显式开启并使用自定义密码。
- 公开注册只允许学生账号，弱密码被拒绝。
- 教师只能查询自己班级提交。
- 家长只能查询绑定学生。
- 上传边界可拦截异常输入。
- LLM 无 key 或异常时可 fallback。
- 数据库有常用查询索引。
- 作文保存会同步写入提交、版本和成长记录。
- 桌面、平板和手机断点样式存在，移动端记录表安全转义并卡片化。

## 预生产验证计划

### 1. 环境一致性

目标：预生产环境必须接近生产。

检查项：

- Python 版本与生产一致。
- 使用与生产一致的数据库类型。
- 使用与生产一致的密钥注入方式。
- 禁止开启 `ESSAY_APP_SEED_DEMO_USERS`。
- 设置真实的上传大小、LLM 限流和页面分页参数。
- 数据库连接池、备份、迁移和回滚方式明确。

验收标准：

- 部署启动无本地 demo 数据。
- 环境变量不出现在日志和页面。
- `OPENAI_BASE_URL` 使用批准的端点。

### 2. 安全验证

必须执行：

```bash
python -m unittest discover -s testcode -p 'test_*.py'
pip-audit -r requirements.txt
```

人工或自动化检查：

- 没有硬编码 API key。
- `.env`、`.streamlit/secrets.toml` 不提交仓库。
- 管理员、教师、家长账号不能公开自注册。
- 老师 A 无法读取老师 B 班级学生作文。
- 家长 A 无法读取未绑定学生作文。
- 大文件上传、超高像素图片、非图片内容均被拒绝。
- 登录失败不泄露用户名是否存在。

上线门槛：

- 高危和严重依赖漏洞为 0。
- 权限越权测试全部失败即拦截。
- 生产日志不包含作文全文、密码、API key。

### 3. 性能与容量验证

必须明确容量目标，示例：

| 指标 | 目标 |
|---|---|
| 同时在线用户 | 1000 |
| 普通页面 p95 延迟 | < 500ms |
| 列表查询 p95 延迟 | < 800ms |
| 作文提交同步保存 p95 延迟 | < 1000ms，不含 LLM |
| LLM 任务排队后可接受完成时间 | < 60s |
| 错误率 | < 0.5% |

建议压测场景：

1. 登录和会话创建。
2. 学生查看作业列表。
3. 学生提交作文，不调用真实 LLM，验证本地保存吞吐。
4. 老师查看班级提交分页。
5. 家长查看绑定学生最近作文。
6. 上传边界测试。
7. LLM 队列或 fallback 测试。

推荐压测脚本方向：

```bash
# 示例：可用 Locust/k6 编写真实 HTTP 用户行为
locust -f loadtest/locustfile.py --host https://staging.example.com
```

上线门槛：

- 目标并发下 p95 延迟达标。
- 数据库 CPU、连接数、慢查询可控。
- 应用内存无持续增长。
- LLM 限流或队列不会压垮 Web 进程。

### 4. 数据库验证

SQLite 适合本地和演示，不是大规模多副本生产的最终方案。大规模生产建议替换为 Postgres/Supabase。

验证项：

- 所有列表查询都有 `LIMIT/OFFSET` 或游标分页。
- 常用过滤列有索引。
- 权限条件位于 SQL 查询层，而不是只在 UI 层过滤。
- 写入操作具备事务边界。
- 备份和恢复演练可完成。

上线门槛：

- 预生产数据量至少达到预估生产 1-3 个月规模。
- 关键查询执行计划命中索引。
- 备份恢复演练成功。

### 5. 可观测性验证

生产必须能回答三个问题：

- 系统是否可用？
- 哪个依赖慢或失败？
- 是否出现权限、上传、模型调用异常？

建议指标：

- 请求量、错误率、p50/p95/p99 延迟。
- 登录成功/失败次数。
- 作文提交数、保存失败数。
- LLM 调用数、fallback 数、超时数、限流数。
- 上传拒绝数和拒绝原因。
- 数据库连接数、慢查询、锁等待。
- 进程 CPU、内存、重启次数。

上线门槛：

- 有健康检查。
- 有错误日志聚合。
- 有关键告警：错误率、延迟、DB 连接、LLM 失败率、磁盘空间。

### 6. 故障演练

必须验证依赖失败时系统不会整体崩溃：

| 故障 | 预期行为 |
|---|---|
| OpenAI/API 失败 | 使用 fallback 反馈，页面不中断 |
| 数据库短暂失败 | 返回友好错误，日志记录，不能丢半条数据 |
| 上传恶意大文件 | 请求被拒绝，进程内存稳定 |
| 某个 Streamlit 实例重启 | 用户可重新登录，数据不丢失 |
| 限流触发 | 返回 fallback 或提示稍后再试 |

上线门槛：

- 故障期间无数据越权。
- 恢复后可继续提交和查询。
- 告警能在故障发生时触发。

## 生产架构建议

推荐大规模部署形态：

```text
Browser
  |
  v
Load Balancer / Reverse Proxy
  |
  v
Streamlit App Replicas
  |
  +--> Postgres/Supabase Store
  +--> Redis Rate Limit / Cache
  +--> Object Storage for uploads
  +--> Queue Worker for LLM review
  +--> Observability stack
```

v5 当前代码中的替换点：

- `SQLiteStore` -> `PostgresStore`
- `FixedWindowRateLimiter` -> `RedisRateLimiter`
- `LLMService.essay_feedback` 同步调用 -> `enqueue_review_job`
- 本地上传处理 -> 对象存储元数据记录

## 上线判定清单

只有全部满足，才可以认为 v5 达到生产上线标准：

- [ ] 单元/集成测试全部通过。
- [ ] 依赖漏洞扫描无高危和严重漏洞。
- [ ] 预生产环境禁用演示账号。
- [ ] 生产数据库替换 SQLite 或明确接受 SQLite 的单机容量限制。
- [ ] 老师、家长权限隔离通过自动化和人工验收。
- [ ] 上传限制通过攻击样本验证。
- [ ] LLM 超时、fallback、限流通过演练。
- [ ] 压测达到目标并发、延迟和错误率。
- [ ] 数据库执行计划命中索引。
- [ ] 备份恢复演练成功。
- [ ] 关键监控和告警上线。
- [ ] 日志不记录密码、密钥和不必要的学生作文全文。

## 最终判断

v5 的代码结构已经解决了根目录原型中最影响生产化的几个问题：模块化、权限隔离、分页查询、上传边界、LLM fallback、最小化依赖和独立测试。它可以作为生产候选版本进入预生产验证。

但“大规模服务能力”不是由代码结构单独证明的。必须结合真实部署形态、数据库类型、并发压测、故障演练和监控数据共同证明。完成本文档中的预生产验证计划并满足上线判定清单后，才能严谨地说明 v5 具备生产部署和大规模服务支撑能力。
