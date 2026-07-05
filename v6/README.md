# 校园作文辅导系统 v6（上线版）

v6 在 v5 模块化架构上合入 B 版（Campus-Essay-System-Improved）的"继续改写"功能，
修复其全部已知缺陷，并新增 K12 小学英语写作与免费/付费会员体系。

## 相对 v5 / B 版的主要变化

- **继续改写（修正版语义）**：改写只追加 `essay_versions` 新版本并刷新原
  submission 的最新状态，不再产生重复 submission，版本计数与对比一致。
- **作业下发闭环**：老师布置的作文题（含布置说明）按年级+班级推送到学生端；
  老师端可查看已布置历史。
- **K12 英语写作**：三—六年级分级题型（看图写话、My Day、Diary、Letter、Story 等）、
  英文模板与句型、启发式评分（词数/句首大写/连接词/词汇多样性）、
  LLM 双语精批 + 逐句语法订正（grammar_corrections）。
- **班级邀请码**：建班自动生成邀请码，学生注册填码自动入班，替代自由文本班级名。
- **会员体系**：免费版每天 3 次 AI 点评；会员（26 元/月、288 元/年）不限次 AI 点评、
  英语精批、看图作文、继续改写、版本对比。支付走"扫码 + 订单号备注 + 管理员核销"，
  也支持一次性激活码；新注册赠 7 天体验。
- **LLM 反馈 schema 归一化**：缺字段自动用本地引擎补齐，杜绝 B 版"原始转义 JSON
  泄漏到界面"和 KeyError；点评标注来源（AI / 基础点评）。
- **管理员创建账号同样强制用户名/密码校验**；登录按用户名限流。

## 模块

- `app/config.py`：环境变量/secrets 配置（含定价、免费额度、收款码 URL）。
- `app/content.py` / `app/content_en.py`：语文与英语的年级 rubric、模板、题库。
- `app/metrics.py` / `app/metrics_en.py`：中英文本地评分引擎。
- `app/llm.py`：LLM 调用、双语提示词、限流、回退与 schema 归一化。
- `app/storage.py`：SQLite 存储（生产可替换 Postgres/Supabase），含订阅/订单/激活码/AI 用量表。
- `app/services.py`：业务服务（注册、作业、点评、改写、会员、额度）。
- `app/ui.py`：Streamlit 界面。
- `testcode/`：单元测试 + 系统测试 + 验收测试。

## 运行

```bash
cd v6
pip install -r requirements.txt
streamlit run campus_essay_system.py
```

演示账号（默认关闭）：

```bash
export ESSAY_APP_SEED_DEMO_USERS=1
export ESSAY_APP_DEMO_PASSWORD='DemoPass123'
```

收款二维码（会员支付页展示）：

```bash
export PAYMENT_QR_MONTH_URL='https://.../qr_month.png'
export PAYMENT_QR_YEAR_URL='https://.../qr_year.png'
```

## 测试

```bash
python -m unittest discover -s testcode -p 'test_*.py'   # 全部
python -m unittest testcode.test_unit_core               # 单元测试
python -m unittest testcode.test_system_flows            # 系统测试
python -m unittest testcode.test_acceptance              # 验收测试
```
