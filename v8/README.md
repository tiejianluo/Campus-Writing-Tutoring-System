# 写作陪练系统 v8（双语界面 + 手写作文识别版）

v8 在 v7（运营版）基础上新增两大能力：

1. **中文 / 英文双语界面**：整套 UI（登录注册、学生端、老师端、家长端、管理员端、
   点评展示、会员中心）都可在侧边栏一键切换中文或英文显示。
2. **手写作文上传与识别**：学生拍下纸上手写的作文照片并上传，系统用视觉大模型
   自动提取文字，学生核对修正后即可获得点评、保存，并进入"继续改写"闭环。

## 相对 v7 的主要变化

### 1. 双语 UI（app/i18n.py）

- 新增 `app/i18n.py` 文案目录：240+ 条界面文案，每条同时提供 `zh` / `en` 两种语言，
  由 `tr(key, lang, **kwargs)` 统一取用；缺失语言时回退中文，杜绝界面出现空文案。
- 侧边栏顶部新增「界面语言 / Language」切换（中文 / English），即时生效，
  切换语言不丢失登录状态和页面选择（菜单等控件用固定 key + 动态显示文字实现）。
- **界面文字与教学内容分离**：作文类型、题目库、写作模板、点评正文属于教学内容，
  保持其本来语言（中文课程为中文、英语课程为英文），不随界面语言切换。

### 2. 手写作文上传（学生端新菜单「手写作文上传 / Upload handwritten essay」）

- 上传 png/jpg 照片（沿用 v5 以来的大小/像素上限校验）→ 点击**识别手写文字** →
  识别结果进入可编辑文本框，学生核对修正后点**生成点评并保存**，
  与键盘输入的作文走完全相同的点评、保存、改写、版本对比、成长档案流程。
- 识别由视觉大模型完成（`LLMService.ocr_essay_image`）：逐字转写、保留段落、
  **不纠正学生的错别字**（错误留给点评环节指出），忽略稿纸格线等干扰。
- 额度语义与 AI 点评一致：**识别与 AI 点评共用每日免费额度**（默认 3 次/天），
  会员不限次；识别失败不扣额度。
- 识别不可用时（未配置密钥 / 额度用完 / 限流 / 服务出错）给出明确原因，
  学生仍可直接在文本框输入作文完成点评——写作主流程永不被阻断。

### 3. 其他

- 默认数据库改为 `essay_campus_system_v8.db`（把 `ESSAY_APP_DB` 指向旧库即可
  无损沿用 v7 数据，表结构无变化）。
- 应用标题更新为「写作陪练 WriteSmart」。
- v7 的全部功能与语义原样保留：额度回退本地点评、点评来源标注、
  管理员运营看板、账号注销/重开、密码重置、AI 状态诊断、引导管理员等。

---

# 使用说明

## 一、安装与启动

```bash
cd v8
pip install -r requirements.txt
streamlit run campus_essay_system.py
```

浏览器打开 `http://localhost:8501`。无需额外 OCR 依赖——手写识别复用视觉大模型。

### 开启 AI 点评与手写识别（重要）

不配置 AI 密钥系统也能运行（本地基础点评），但 **AI 智能点评和手写识别必须配置
密钥**，且模型需支持图片输入（视觉能力）：

```bash
export OPENAI_API_KEY='sk-...'
export OPENAI_BASE_URL='https://api.openai.com/v1'   # 可选，兼容任何 OpenAI 协议服务
export OPENAI_MODEL='gpt-4.1-2025-04-14'             # 可选，需支持视觉输入
```

或写入 `.streamlit/secrets.toml`。配置后用管理员端「AI 状态」页的
**测试 AI 连接**按钮验证。

### 创建管理员账号（同 v7）

```bash
export ESSAY_APP_ADMIN_USER='admin'
export ESSAY_APP_ADMIN_PASSWORD='一个至少8位的强密码'
```

### 其他可选配置（同 v7）

```bash
export FREE_AI_DAILY_QUOTA=3          # 免费版每天 AI 点评+识别总次数（默认 3）
export PREMIUM_PRICE_MONTH=26
export PREMIUM_PRICE_YEAR=288
export PREMIUM_TRIAL_DAYS=7
export PAYMENT_QR_MONTH_URL='https://.../qr_month.png'
export PAYMENT_QR_YEAR_URL='https://.../qr_year.png'
export ESSAY_APP_DB='essay_campus_system_v8.db'
```

## 二、双语界面使用

- 侧边栏最上方「界面语言 / Language」选择 **中文** 或 **English**。
- 所有角色（学生/老师/家长/管理员）的界面文字即时切换；
  作文题库与模板等教学内容保持原语言。

## 三、学生使用手写作文上传

1. 学生端选择「手写作文上传」。
2. 拍照要求：光线充足、字迹完整入镜、尽量正对稿纸；支持 png/jpg。
3. 点击**识别手写文字**，稍候几秒；识别结果出现在文本框中。
4. **核对并修正**识别错误（识别会原样保留你的错别字，点评时老师/AI 会指出）。
5. 选择科目、作文类型和题目，点击**生成点评并保存**。
6. 之后可照常在「继续改写」「历史版本对比」中修改和对比。

识别失败的常见提示：

| 提示 | 含义与处理 |
|---|---|
| 未配置 AI 服务 | 联系管理员配置 `OPENAI_API_KEY`；可先手动输入作文 |
| 今日免费 AI 额度已用完 | 明天再来或开通会员；可先手动输入作文 |
| 请求过于频繁 | 等一分钟再试 |
| AI 识别服务暂时不可用 | 稍后重试；管理员可查「AI 状态」 |

## 四、免费 / 会员权益（v8 口径）

| 功能 | 免费版 | 会员（26 元/月、288 元/年） |
|---|---|---|
| 写作文 + 本地基础点评 | ✅ 不限次 | ✅ 不限次 |
| AI 智能点评 + 手写识别 | 共用每天 3 次额度 | 不限次 |
| 英语 AI 精批（逐句语法订正） | 计入每日额度 | 不限次 |
| 看图作文 AI 提示 | ❌ | ✅ |
| 继续改写 / 版本对比 | ❌ | ✅ |
| 成长档案 / 双语界面 | ✅ | ✅ |

## 五、测试

```bash
cd v8
python -m unittest discover -s testcode -p 'test_*.py'   # 全部（98 个）
python -m unittest testcode.test_unit_core               # 单元测试（v7 继承）
python -m unittest testcode.test_system_flows            # 系统测试（v7 继承）
python -m unittest testcode.test_acceptance              # 验收测试（含 v8 双语与手写验收）
python -m unittest testcode.test_i18n                    # v8 新增：双语文案测试
python -m unittest testcode.test_handwriting_ocr         # v8 新增：手写识别测试
```

- v7 的 70 个测试全部原样保留并通过。
- v8 新增 28 个测试：
  - `test_i18n.py`：每条文案中英齐全、占位符一致、`tr` 回退语义、
    UI 引用的 key 全部存在。
  - `test_handwriting_ocr.py`：OCR 调用路径（无密钥/限流/成功/出错）与
    额度语义（共用每日额度、会员不限次、失败不扣额度）。
  - `test_acceptance.py` 新增 `BilingualUIAcceptance`、`HandwritingEssayAcceptance`
    两组验收用例，对应本次升级的两条需求。

## 六、常见问题

**Q：手写识别为什么把我的错别字也照抄了？**
这是有意设计：识别环节忠实转写，错误由点评环节指出，这样点评才能针对
你真实的书写水平。

**Q：切换英文界面后作文题目还是中文？**
作文类型、题库、模板是教学内容，不属于界面文字；中文课程内容保持中文，
英语课程内容本来就是英文。

**Q：升级 v7 数据库会丢数据吗？**
不会。表结构与 v7 相同，把 `ESSAY_APP_DB` 指向原库即可。

## 模块结构

- `app/i18n.py`：**v8 新增**，双语文案目录与 `tr()`。
- `app/llm.py`：LLM 调用（新增 `ocr_essay_image` 手写转写）。
- `app/services.py`：业务服务（新增 `ocr_extract_essay` 额度语义）。
- `app/ui.py`：Streamlit 界面（全量双语化 + 手写作文页面）。
- `app/config.py` / `app/storage.py` / 其余模块：同 v7。
- `testcode/`：单元 + 系统 + 验收测试（98 个）。
