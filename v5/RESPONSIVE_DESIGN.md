# v5 跨设备支持设计

## 目标设备

v5 按三类运行环境设计响应式体验：

| 类别 | 典型设备 | 设计重点 |
|---|---|---|
| 桌面/笔记本 | Desktop, Laptop | 保持较高信息密度，表格适合扫描和比较 |
| 平板 | iPad, Android Tablet | 中等宽度、触控操作，表格保持可读并控制横向滚动 |
| 手机 | iPhone, Android Phone | 单列布局、触控按钮、表格自动卡片化 |

## 需要修改完善的模块

主要修改 `app/ui.py`，新增 `app/responsive.py`。

### `app/responsive.py`

集中管理跨设备适配：

- CSS 断点：手机 `<=720px`，平板 `721-1024px`，桌面 `>1024px`。
- 触控尺寸：按钮、tab、输入框最小高度 `44px`。
- 表格响应式：桌面为表格，手机端每行变成卡片式记录。
- 文本换行：长用户名、题目、班级名不会撑破容器。
- 安全渲染：移动端记录表使用 HTML escape，避免注入。

### `app/ui.py`

UI 层只调用响应式模块：

- `inject_responsive_styles()` 在页面初始化后立即注入。
- `dataframe()` 改为调用 `render_records()`。
- 反馈指标使用 `st.columns(3)`，手机端通过 CSS 自动堆叠为单列。
- 页面不直接编写 CSS，避免响应式规则分散。

## 验证方式

自动化测试：

```bash
cd v5
python -m unittest discover -s testcode -p 'test_*.py'
```

新增测试：

- `test_responsive.py::test_responsive_css_has_phone_tablet_and_touch_targets`
- `test_responsive.py::test_records_table_html_escapes_user_content`
- `test_responsive.py::test_ui_loads_responsive_styles`

人工验收建议：

1. Desktop/Laptop：浏览器宽度 `1280px`、`1440px`。
2. Tablet：浏览器模拟 `768x1024` 和 `1024x768`。
3. iOS：Safari 或浏览器模拟 `390x844`。
4. Android：Chrome 或浏览器模拟 `360x800`。

关键检查项：

- 登录、注册、作文输入、图片上传、老师查看提交、家长查看学生记录均可操作。
- tab 和 radio 不横向溢出。
- 按钮和输入框触控面积足够。
- 表格在手机端变为卡片式记录。
- 长题目、长班级名、长用户名不会撑破布局。
- 图表和图片不会遮挡正文。

