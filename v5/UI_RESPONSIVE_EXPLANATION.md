# `responsive.py` 与 `ui.py` 工作原理和正确性论证

本文解释 v5 中两个前端相关模块的职责、工作流程和正确性依据：

- `app/responsive.py`
- `app/ui.py`

## 总体关系

`app/ui.py` 是 Streamlit 界面层，负责页面组织、用户交互和角色视图分发。

`app/responsive.py` 是跨设备适配层，负责桌面、笔记本、平板、iOS 手机和 Android 手机的响应式样式，以及移动端友好的记录表渲染。

二者的关系是：

```text
campus_essay_system.py
  -> app.ui.main()
       -> inject_responsive_styles()
       -> auth_sidebar()
       -> teacher_view() / student_view() / parent_view() / admin_view()
       -> render_records()
```

这种结构把“业务页面”和“响应式展示规则”拆开，避免 CSS 和移动端适配逻辑散落在多个页面函数里。

## `responsive.py`

文件位置：

```text
v5/app/responsive.py
```

### 职责

`responsive.py` 只负责展示适配，不处理登录、数据库、LLM、作文保存等业务逻辑。

它主要做三件事：

1. 定义响应式断点和触控尺寸。
2. 向 Streamlit 页面注入响应式 CSS。
3. 把列表数据渲染成桌面端表格、手机端卡片式记录。

### 核心常量

```python
PHONE_MAX_WIDTH = 720
TABLET_MAX_WIDTH = 1024
TOUCH_TARGET_PX = 44
```

含义：

- `PHONE_MAX_WIDTH = 720`：宽度小于或等于 720px 时按手机布局处理。
- `TABLET_MAX_WIDTH = 1024`：宽度在 721px 到 1024px 之间时按平板布局处理。
- `TOUCH_TARGET_PX = 44`：按钮、输入框、tab 等触控控件的最小高度。

这三项覆盖三类设备：

| 类型 | 宽度范围 | 目标设备 |
|---|---:|---|
| 手机 | `<= 720px` | iPhone、Android Phone |
| 平板 | `721px - 1024px` | iPad、Android Tablet |
| 桌面/笔记本 | `> 1024px` | Desktop、Laptop |

### CSS 注入原理

`RESPONSIVE_CSS` 是一段完整的 CSS 字符串，通过 `inject_responsive_styles()` 注入页面：

```python
def inject_responsive_styles() -> None:
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)
```

这里使用 `unsafe_allow_html=True` 是为了让 Streamlit 接受 `<style>...</style>`。这本身有风险，但当前只注入内部固定 CSS，不拼接用户输入，因此 CSS 注入部分是可控的。

### 桌面/笔记本布局

默认样式服务于 Desktop/Laptop：

- `.block-container` 最大宽度为 `1180px`，避免宽屏下内容过散。
- `.v5-table` 使用标准表格布局，适合老师、管理员在大屏上扫描多行记录。
- `overflow-wrap: anywhere` 让长用户名、长班级名、长作文题不会撑破表格。

### 平板布局

平板断点：

```css
@media (min-width: 721px) and (max-width: 1024px)
```

主要调整：

- 页面最大宽度收窄为 `940px`。
- 左右 padding 设为 `1rem`。
- 表格字体略小。

这个设计保留表格形态，因为平板横竖屏都还有一定宽度；同时照顾触控操作，不让内容贴边。

### 手机布局

手机断点：

```css
@media (max-width: 720px)
```

主要调整：

- 页面左右 padding 缩小。
- 标题字号减小。
- Streamlit columns 强制变成单列。
- 表格从传统表格变成卡片式记录。

移动端表格变卡片的关键逻辑：

```css
.v5-table thead {
  display: none;
}

.v5-table tr {
  background: var(--v5-surface);
  border: 1px solid var(--v5-border);
  border-radius: 8px;
}

.v5-table td {
  display: grid;
  grid-template-columns: minmax(6.5rem, 42%) 1fr;
}

.v5-table td::before {
  content: attr(data-label);
}
```

含义：

- 手机端隐藏表头。
- 每一行变成一个独立卡片。
- 每个单元格用 `data-label` 显示字段名。
- 用户在手机上不需要横向拖动大表格。

### `records_table_html()`

该函数把字典列表转换为 HTML 表格：

```python
def records_table_html(rows, columns=None) -> str:
```

输入示例：

```python
[
    {"学生": "小明", "作文": "春游日记"},
    {"学生": "小红", "作文": "我的妈妈"},
]
```

输出结构：

```html
<div class="v5-records">
  <table class="v5-table">
    <thead>...</thead>
    <tbody>
      <tr>
        <td data-label="学生">小明</td>
        <td data-label="作文">春游日记</td>
      </tr>
    </tbody>
  </table>
</div>
```

桌面端 CSS 显示为普通表格；手机端 CSS 使用 `data-label` 把每一行转换为卡片。

### 安全性

`records_table_html()` 对字段名和值都使用了 `html.escape`：

```python
escape(str(col))
escape(str(value))
```

因此，即使用户输入：

```html
<script>alert(1)</script>
```

页面也会显示为普通文本：

```html
&lt;script&gt;alert(1)&lt;/script&gt;
```

这保证了虽然 `st.markdown(..., unsafe_allow_html=True)` 被用于渲染表格，但用户内容不会作为 HTML 或 JavaScript 执行。

### 正确性论证

`responsive.py` 的正确性来自以下几点：

1. 设备覆盖完整：默认样式覆盖桌面/笔记本，平板断点覆盖 721px 到 1024px，手机断点覆盖小于等于 720px。
2. 触控可用：按钮、输入框、tab 设置 `44px` 最小高度，适合 iOS 和 Android 触控。
3. 移动端可读：表格在手机端自动卡片化，避免横向滚动和字段含义丢失。
4. 长文本安全：`overflow-wrap: anywhere` 让长文本自动换行。
5. HTML 安全：所有表格字段名和值都经过 `escape`。
6. 空数据安全：无数据时 `render_records()` 显示提示，不访问不存在的 `rows[0]`。
7. 自动化测试覆盖：`test_responsive.py` 验证断点、触控尺寸、HTML 转义和 UI 接入。

## `ui.py`

文件位置：

```text
v5/app/ui.py
```

### 职责

`ui.py` 是 Streamlit 页面层，负责：

- 初始化应用服务。
- 管理登录状态。
- 根据角色展示不同页面。
- 收集用户输入。
- 调用服务层完成业务动作。
- 调用响应式模块渲染列表。

它不直接负责：

- SQL 查询细节。
- 密码哈希。
- LLM 调用细节。
- 上传文件底层校验。
- 权限查询逻辑。

这些职责分别放在：

- `storage.py`
- `security.py`
- `llm.py`
- `uploads.py`
- `services.py`

### 服务初始化

```python
@st.cache_resource
def build_service() -> AppService:
    settings = Settings.from_env()
    store = SQLiteStore(settings)
    service = AppService(settings, store, LLMService(settings))
    service.initialize()
    return service
```

工作流程：

1. 从环境变量或 Streamlit secrets 读取配置。
2. 创建存储层 `SQLiteStore`。
3. 创建 LLM 服务 `LLMService`。
4. 创建业务服务 `AppService`。
5. 初始化数据库结构。
6. 通过 `st.cache_resource` 缓存服务实例。

正确性依据：

- 避免每次页面刷新重复初始化数据库。
- UI 只依赖 `AppService`，方便未来替换 `SQLiteStore` 为 Postgres/Supabase。

### 统一记录渲染

```python
def dataframe(rows: list[dict]) -> None:
    render_records(rows)
```

虽然函数名叫 `dataframe`，现在实际调用的是 `render_records()`。

这样所有列表页面都共享响应式表格能力，包括：

- 老师查看提交。
- 班级列表。
- 学生作业列表。
- 学生历史记录。
- 管理员用户列表。

正确性依据：

- 响应式逻辑集中在 `responsive.py`。
- UI 页面不用重复处理移动端表格。
- 后续改表格样式只改一个模块。

### 登录与注册

`auth_sidebar(service)` 负责登录和学生注册。

关键逻辑：

```python
st.session_state.setdefault("user", None)
```

作用：

- 初始化登录状态。
- 登录成功后把用户写入 `st.session_state.user`。
- 退出时清空并 `st.rerun()`。

登录：

```python
logged_in = service.login(username, password)
```

注册：

```python
service.register_public_student(...)
```

正确性依据：

- UI 不直接查数据库。
- 登录认证和注册规则都由服务层处理。
- 公开注册只开放学生账号，教师、家长、管理员由管理员创建。

### 老师端

`teacher_view(service, user)` 包含：

1. 布置作文题。
2. 查看班级提交。
3. 班级管理。

老师提交查询：

```python
rows = service.store.list_teacher_submissions(user["username"], limit=size, offset=(page - 1) * size)
```

查看单个提交：

```python
detail = service.store.get_submission_for_teacher(user["username"], int(sid))
```

正确性依据：

- 查询里带 `teacher_username`，不是前端全量取出后过滤。
- 老师只能看到自己负责班级的提交。
- 列表有分页参数 `limit` 和 `offset`，避免一次加载全部数据。

### 学生端

`student_view(service, user)` 包含：

1. 开始写作文。
2. 看图作文。
3. 历史记录。
4. 成长档案。

作文题查询：

```python
service.store.list_assignments_for_student(grade, user.get("class_name"), limit=service.page_size())
```

文本上传：

```python
essay = read_uploaded_text(uploaded_txt, service.settings)
```

图片上传：

```python
image = load_uploaded_image(image_file, service.settings)
```

作文保存：

```python
service.review_and_save_submission(...)
```

正确性依据：

- 作业按学生年级和班级查询。
- 上传文件先经过大小、格式、像素校验。
- 作文长度限制和评分保存由服务层处理。
- LLM 调用失败时由 `LLMService` fallback，不让页面崩溃。

### 家长端

`parent_view(service, user)` 负责家长查看绑定学生最近作文。

关键调用：

```python
students = service.store.list_parent_students(user["username"])
latest = service.store.latest_submission_for_parent(user["username"], selected)
```

正确性依据：

- 家长只能看到 `parent_student_links` 中显式绑定的学生。
- 最新作文查询也再次验证绑定关系。
- 权限控制在存储层，不依赖 UI 隐藏。

### 管理员端

`admin_view(service)` 包含：

- 查看用户。
- 创建账号。
- 绑定家长和学生。

正确性依据：

- 教师、家长、管理员不走公开注册。
- 管理员创建用户时调用 `service.create_user_by_admin()`。
- 家长绑定关系由 `service.store.link_parent_to_student()` 建立。

### 点评展示

`show_feedback()` 展示作文点评结果。

关键响应式处理：

```python
c1, c2, c3 = st.columns(3)
```

桌面端显示为三列：

- 字数
- 结构分
- 表达分

手机端在 `responsive.py` 中通过 CSS 强制 columns 变为单列，避免三列挤压。

### 主入口

```python
def main():
    settings = Settings.from_env()
    st.set_page_config(...)
    inject_responsive_styles()
    service = build_service()
    ...
```

初始化顺序：

1. 读取配置。
2. 设置页面配置。
3. 注入响应式样式。
4. 构建服务。
5. 登录鉴权。
6. 根据角色分发页面。

正确性依据：

- `st.set_page_config()` 在主要页面渲染前执行。
- 响应式样式在页面内容前注入。
- 所有角色页面都共享同一个服务实例。
- 角色分发明确：teacher、student、parent、admin。

## 两个文件协同后的正确性

### 1. 跨设备正确性

`ui.py` 负责产生页面结构，`responsive.py` 负责不同屏幕宽度下如何展示。

证明点：

- 桌面/笔记本：表格保持表格，信息密度高。
- 平板：容器宽度收敛，表格仍可读。
- 手机：表格卡片化，列布局单列化，控件触控高度足够。

### 2. 安全正确性

虽然响应式表格使用了 HTML 渲染，但：

- 用户内容经过 `html.escape`。
- UI 不直接拼接用户 HTML。
- 权限查询由存储层完成。
- 上传内容先经过 `uploads.py` 校验。

### 3. 分层正确性

`ui.py` 不直接写 SQL，也不直接实现密码、LLM、上传校验。

这意味着：

- UI 变化不会破坏数据库逻辑。
- 数据库替换不会大规模改 UI。
- 业务规则可以独立测试。
- 响应式规则可以独立测试。

### 4. 可测试性

相关测试：

```text
test_responsive.py
test_architecture.py
test_storage_security.py
test_uploads_llm.py
test_metrics_services.py
```

当前验证命令：

```bash
cd /home/ad/c2luo/tjl/Campus-Writing-Tutoring-System/v5
python -m unittest discover -s testcode -p 'test_*.py'
```

当前结果：

```text
Ran 19 tests
OK
```

## 边界和后续改进

当前实现已经支持 Desktop、Laptop、Tablet、iOS 和 Android 的基础响应式体验，但完整上线前还需要真实浏览器验收：

- Desktop/Laptop：`1280px`、`1440px`
- Tablet：`768x1024`、`1024x768`
- iOS：`390x844`
- Android：`360x800`

重点检查：

- tab/radio 是否溢出。
- 作文输入是否舒适。
- 上传控件是否可操作。
- 表格卡片是否可读。
- 长文本是否换行。
- 图表是否遮挡正文。
- Safari 和 Android Chrome 是否表现一致。

如果后续继续增强，可以考虑：

- 为移动端添加底部导航。
- 将老师端高密度表格拆成筛选 + 详情页。
- 用 Playwright 做真实浏览器截图回归测试。
- 为 iOS Safari 单独验证文件上传和软键盘交互。
