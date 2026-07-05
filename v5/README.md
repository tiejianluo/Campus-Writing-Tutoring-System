# 校园作文辅导系统 v5

v5 面向更高并发和长期维护，把根目录单文件原型拆成可测试的模块：

- `app/config.py`：环境变量与 Streamlit secrets 配置。
- `app/storage.py`：存储层，当前使用 SQLite 本地实现，生产可替换为 Postgres/Supabase。
- `app/services.py`：业务动作，如注册、登录、点评保存、作业发布。
- `app/llm.py`：模型调用、fallback、基础限流。
- `app/uploads.py`：文本和图片上传大小/像素限制。
- `app/responsive.py`：桌面、平板、iOS 和 Android 的响应式样式与记录表渲染。
- `app/ui.py`：Streamlit 界面。
- `testcode/`：v5 独立测试目录。

## 运行

```bash
cd v5
pip install -r requirements.txt
streamlit run campus_essay_system.py
```

默认不会创建公开演示账号。需要本地演示时配置：

```bash
export ESSAY_APP_SEED_DEMO_USERS=1
export ESSAY_APP_DEMO_PASSWORD='DemoPass123'
```

## 测试

```bash
python -m unittest discover -s testcode -p 'test_*.py'
```

## 规模化部署建议

- 把 `SQLiteStore` 替换为 Postgres/Supabase 存储实现，保留 `AppService` 和 UI 调用接口。
- 把 `FixedWindowRateLimiter` 替换为 Redis 等共享限流器，避免多副本部署时各进程独立计数。
- 把 LLM 调用迁移到异步任务队列，前端提交后轮询状态，避免 Streamlit worker 长时间阻塞。
- 把上传文件放到对象存储，数据库只保存元数据和结果。
- 使用外部会话/身份服务管理教师、家长、管理员账号。
- 为常用列表接口保留分页、索引和权限条件，避免全表读入 DataFrame。

## 跨设备支持

响应式设计说明见 `RESPONSIVE_DESIGN.md`。v5 支持三类布局：

- Desktop/Laptop：表格扫描和宽屏操作。
- Tablet：中等宽度触控布局。
- iOS/Android Phone：单列布局，记录表自动卡片化。
