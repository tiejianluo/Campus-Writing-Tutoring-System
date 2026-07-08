"""v8 双语 UI 文案模块 / Bilingual UI copy for v8.

所有用户可见的界面文字集中在 TEXTS 中，按 key -> {"zh": ..., "en": ...} 组织。
课程内容（作文类型、题目、模板、点评正文）属于教学内容而非界面文字，
保持其原有语言（中文课程为中文、英语课程为英文）。
"""

from typing import Any, Dict

LANG_ZH = "zh"
LANG_EN = "en"
LANGS = (LANG_ZH, LANG_EN)
DEFAULT_LANG = LANG_ZH

# 侧边栏语言切换器的显示名（各自用母语显示，不翻译）。
LANG_LABELS = {LANG_ZH: "中文", LANG_EN: "English"}

TEXTS: Dict[str, Dict[str, str]] = {
    # ------------------------------------------------------------------
    # 全局 / Global
    # ------------------------------------------------------------------
    "app_caption": {
        "zh": "语文作文 + K12 小学英语写作 · AI 点评 · 手写作文识别 · 继续改写 · 成长档案",
        "en": "Chinese & K-12 English writing · AI feedback · Handwriting OCR · Revision loop · Growth portfolio",
    },
    "please_login": {
        "zh": "请先登录或注册学生账号。",
        "en": "Please log in or register a student account first.",
    },
    "unknown_role": {"zh": "未知角色。", "en": "Unknown role."},
    "no_data": {"zh": "暂无数据。", "en": "No data yet."},
    "language_label": {"zh": "界面语言 / Language", "en": "Language / 界面语言"},

    # ------------------------------------------------------------------
    # 账号 / Auth sidebar
    # ------------------------------------------------------------------
    "account_system": {"zh": "账号系统", "en": "Account"},
    "logged_in": {"zh": "已登录：{who}", "en": "Signed in: {who}"},
    "member_until": {"zh": "会员有效期至 {date}", "en": "Premium until {date}"},
    "quota_left": {
        "zh": "今日剩余免费 AI 点评：{n} 次（本地基础点评不限次）",
        "en": "Free AI reviews left today: {n} (local basic feedback is always unlimited)",
    },
    "logout": {"zh": "退出登录", "en": "Log out"},
    "tab_login": {"zh": "登录", "en": "Log in"},
    "tab_register": {"zh": "学生注册", "en": "Student sign-up"},
    "username": {"zh": "用户名", "en": "Username"},
    "password": {"zh": "密码", "en": "Password"},
    "login_btn": {"zh": "登录", "en": "Log in"},
    "login_failed": {
        "zh": "用户名或密码错误、账号已被注销，或尝试过于频繁。",
        "en": "Wrong username/password, account deactivated, or too many attempts.",
    },
    "new_username": {"zh": "新用户名", "en": "New username"},
    "real_name": {"zh": "姓名", "en": "Full name"},
    "grade": {"zh": "年级", "en": "Grade"},
    "invite_code_opt": {
        "zh": "班级邀请码（老师提供，可选）",
        "en": "Class invite code (from your teacher, optional)",
    },
    "set_password": {"zh": "设置密码", "en": "Choose a password"},
    "register_btn": {"zh": "注册学生账号", "en": "Create student account"},
    "trial_bonus": {
        "zh": " 新用户赠送 {days} 天会员体验。",
        "en": " New users get a {days}-day premium trial.",
    },

    # ------------------------------------------------------------------
    # 会员门槛 / Premium gate
    # ------------------------------------------------------------------
    "premium_required": {
        "zh": "「{feature}」是会员功能。开通会员即可使用：{month} 元/月、{year} 元/年。请到「会员中心」开通。",
        "en": "\"{feature}\" is a premium feature. Subscribe for {month} CNY/month or {year} CNY/year in the Member Center.",
    },

    # ------------------------------------------------------------------
    # 科目 / Subjects
    # ------------------------------------------------------------------
    "subject_chinese": {"zh": "语文作文", "en": "Chinese essay"},
    "subject_english": {"zh": "英语写作 English", "en": "English writing"},
    "subject_short_cn": {"zh": "语文", "en": "Chinese"},
    "subject_short_en": {"zh": "英语", "en": "English"},
    "subject_label": {"zh": "科目", "en": "Subject"},

    # ------------------------------------------------------------------
    # 老师端 / Teacher
    # ------------------------------------------------------------------
    "teacher_home": {"zh": "老师端", "en": "Teacher workspace"},
    "tab_assign": {"zh": "布置作文题", "en": "Assign writing task"},
    "tab_class_submissions": {"zh": "班级提交", "en": "Class submissions"},
    "tab_class_manage": {"zh": "班级管理", "en": "Class management"},
    "create_class_first": {
        "zh": "请先在「班级管理」创建班级。",
        "en": "Create a class in \"Class management\" first.",
    },
    "select_class": {"zh": "选择班级", "en": "Select class"},
    "essay_genre": {"zh": "作文类型", "en": "Writing type"},
    "essay_title_input": {"zh": "作文题目", "en": "Essay title"},
    "assignment_prompt": {
        "zh": "布置说明（学生端可见）",
        "en": "Instructions (visible to students)",
    },
    "due_date": {"zh": "截止日期", "en": "Due date"},
    "publish_btn": {"zh": "发布作文题", "en": "Publish task"},
    "publish_ok": {"zh": "作文题已发布。", "en": "Task published."},
    "published_history": {"zh": "已布置的作文题", "en": "Published tasks"},
    "col_id": {"zh": "编号", "en": "ID"},
    "col_title": {"zh": "题目", "en": "Title"},
    "col_subject": {"zh": "科目", "en": "Subject"},
    "col_genre": {"zh": "类型", "en": "Type"},
    "col_class": {"zh": "班级", "en": "Class"},
    "col_due": {"zh": "截止", "en": "Due"},
    "col_prompt": {"zh": "布置说明", "en": "Instructions"},
    "no_published_yet": {
        "zh": "还没有布置过作文题。",
        "en": "No writing tasks published yet.",
    },
    "page_number": {"zh": "页码", "en": "Page"},
    "view_submission": {"zh": "查看提交", "en": "View submission"},
    "teacher_feedback_hdr": {"zh": "教师点评", "en": "Teacher feedback"},
    "new_class_name": {"zh": "新班级名称", "en": "New class name"},
    "add_class_btn": {"zh": "新增班级", "en": "Create class"},
    "class_created": {
        "zh": "已新增班级，邀请码：{code}（发给学生注册时填写即可自动入班）",
        "en": "Class created. Invite code: {code} (students enter it at sign-up to join automatically)",
    },

    # ------------------------------------------------------------------
    # 学生端 / Student
    # ------------------------------------------------------------------
    "student_home": {"zh": "学生端", "en": "Student workspace"},
    "choose_feature": {"zh": "选择功能", "en": "Choose a feature"},
    "menu_write": {"zh": "开始写作文", "en": "Start writing"},
    "menu_handwriting": {"zh": "手写作文上传", "en": "Upload handwritten essay"},
    "menu_picture": {"zh": "看图作文", "en": "Picture writing"},
    "menu_rewrite": {"zh": "继续改写", "en": "Keep revising"},
    "menu_versions": {"zh": "历史版本对比", "en": "Compare versions"},
    "menu_growth": {"zh": "成长档案", "en": "Growth portfolio"},
    "menu_membership": {"zh": "会员中心", "en": "Member center"},
    "assignments_expander": {"zh": "老师布置的作文题", "en": "Tasks from your teacher"},
    "no_assignments": {
        "zh": "暂时没有老师布置的作文题，你也可以自己练习。",
        "en": "No tasks from your teacher yet — feel free to practice on your own.",
    },
    "assignment_line": {
        "zh": "**[{subject}] {title}**（{genre}，截止 {due}）",
        "en": "**[{subject}] {title}** ({genre}, due {due})",
    },
    "assignment_requirement": {"zh": "作文要求：{prompt}", "en": "Requirements: {prompt}"},
    "topic_label": {"zh": "主题/题目", "en": "Topic"},
    "topic_label_en_subject": {"zh": "Topic 题目", "en": "Topic"},
    "genre_label_en_subject": {"zh": "Writing type 作文类型", "en": "Writing type"},
    "custom_title_opt": {"zh": "自定义题目（可选）", "en": "Custom title (optional)"},
    "writing_guide": {"zh": "写作指导 / Writing guide", "en": "Writing guide"},
    "recommended_structure": {"zh": "推荐结构", "en": "Suggested structure"},
    "ref_opening": {"zh": "参考开头", "en": "Sample opening"},
    "ref_ending": {"zh": "参考结尾", "en": "Sample ending"},
    "common_pattern": {"zh": "常用句型", "en": "Useful sentence pattern"},
    "essay_area": {"zh": "开始写作文", "en": "Write your essay here"},
    "upload_txt": {"zh": "或上传 txt 草稿", "en": "Or upload a .txt draft"},
    "draft_loaded": {"zh": "已读取草稿", "en": "Draft loaded"},
    "review_save_btn": {"zh": "生成点评并保存", "en": "Get feedback & save"},
    "need_content": {"zh": "请先输入作文内容。", "en": "Please write your essay first."},
    "saved_ok": {
        "zh": "已保存本次作文，编号：{sid}。可在「继续改写」中修改并保存新版本。",
        "en": "Essay saved (ID {sid}). You can revise it later in \"Keep revising\".",
    },

    # ------------------------------------------------------------------
    # 手写作文上传（v8 新增）/ Handwritten essay upload (new in v8)
    # ------------------------------------------------------------------
    "handwriting_title": {"zh": "手写作文上传", "en": "Upload a handwritten essay"},
    "handwriting_intro": {
        "zh": "拍下你在纸上写的作文并上传，系统会自动识别文字；确认识别结果后即可获得点评并保存。",
        "en": "Take a photo of your handwritten essay and upload it. The system extracts the text; confirm it, then get feedback and save.",
    },
    "handwriting_upload": {
        "zh": "上传手写作文照片（png / jpg）",
        "en": "Upload a photo of your handwritten essay (png / jpg)",
    },
    "handwriting_image_caption": {"zh": "手写作文图片", "en": "Handwritten essay photo"},
    "handwriting_extract_btn": {"zh": "识别手写文字", "en": "Extract text"},
    "handwriting_extracting": {"zh": "正在识别手写文字……", "en": "Extracting handwritten text..."},
    "handwriting_extracted": {
        "zh": "识别结果（请核对并修改识别错误的地方）",
        "en": "Extracted text (please check and fix any recognition errors)",
    },
    "handwriting_ok": {
        "zh": "识别完成，共 {n} 个字符。请核对后生成点评。",
        "en": "Extraction done ({n} characters). Please check the text, then get feedback.",
    },
    "handwriting_empty": {
        "zh": "没有识别到文字，请换一张更清晰的照片，或直接在下方输入作文。",
        "en": "No text was recognized. Try a clearer photo, or type your essay below.",
    },
    "handwriting_manual_hint": {
        "zh": "识别不可用时，你也可以直接在文本框中输入作文内容。",
        "en": "If extraction is unavailable, you can also type the essay into the text box.",
    },
    "ocr_no_api_key": {
        "zh": "系统尚未配置 AI 服务（OPENAI_API_KEY），暂时无法识别手写文字。请联系管理员，或直接输入作文内容。",
        "en": "The AI service (OPENAI_API_KEY) is not configured, so handwriting recognition is unavailable. Contact the admin, or type the essay instead.",
    },
    "ocr_quota": {
        "zh": "今日免费 AI 额度已用完，手写识别暂不可用。明天再来或开通会员，也可以直接输入作文内容。",
        "en": "Your free daily AI quota is used up, so handwriting recognition is unavailable today. Come back tomorrow, upgrade to premium, or type the essay instead.",
    },
    "ocr_rate_limited": {
        "zh": "请求过于频繁已被限流，请稍等一分钟再试。",
        "en": "Too many requests. Please wait a minute and try again.",
    },
    "ocr_api_error": {
        "zh": "AI 识别服务暂时不可用，请稍后重试，或直接输入作文内容。",
        "en": "The AI recognition service is temporarily unavailable. Try again later, or type the essay instead.",
    },

    # ------------------------------------------------------------------
    # 看图作文 / Picture writing
    # ------------------------------------------------------------------
    "picture_feature": {"zh": "看图作文 AI 观察提示", "en": "Picture-writing AI prompts"},
    "upload_image": {"zh": "上传图片", "en": "Upload an image"},
    "uploaded_image": {"zh": "上传的图片", "en": "Uploaded image"},
    "gen_observation_btn": {"zh": "生成观察提示", "en": "Generate observation prompts"},
    "scene_summary": {"zh": "场景概括", "en": "Scene summary"},
    "observation_hints": {"zh": "观察提示", "en": "Observation hints"},
    "inspiring_questions": {"zh": "启发问题", "en": "Guiding questions"},
    "basic_prompts_notice": {
        "zh": "当前为基础提示（AI 暂不可用）。",
        "en": "Showing basic prompts (AI unavailable right now).",
    },

    # ------------------------------------------------------------------
    # 继续改写 / Rewrite
    # ------------------------------------------------------------------
    "rewrite_title": {"zh": "继续改写", "en": "Keep revising"},
    "rewrite_feature": {"zh": "继续改写", "en": "Keep revising"},
    "no_essays_yet": {
        "zh": "还没有作文记录，请先开始写作文。",
        "en": "No essays yet — start writing first.",
    },
    "select_essay_rewrite": {"zh": "选择要改写的作文", "en": "Choose an essay to revise"},
    "essay_option": {
        "zh": "#{id} {title}（{genre}，{date}，{score}分）",
        "en": "#{id} {title} ({genre}, {date}, score {score})",
    },
    "cannot_load_essay": {"zh": "无法加载作文。", "en": "Could not load the essay."},
    "versions_so_far": {"zh": "当前已有 {n} 个版本。", "en": "{n} version(s) so far."},
    "original_latest": {"zh": "原文（最新版本）", "en": "Current text (latest version)"},
    "original_text": {"zh": "原文", "en": "Original text"},
    "rewrite_guide": {"zh": "改写指导", "en": "Revision guide"},
    "no_rewrite_guide": {"zh": "暂无改写指导。", "en": "No revision guide available."},
    "rewritten_area": {"zh": "改写后的作文", "en": "Your revised essay"},
    "rewrite_placeholder": {
        "zh": "根据指导建议，在这里写下改写后的作文……",
        "en": "Following the guide, write your revised essay here...",
    },
    "submit_version_btn": {"zh": "提交新版本", "en": "Submit new version"},
    "fill_rewrite_first": {
        "zh": "请先填写改写后的作文。",
        "en": "Please write the revised essay first.",
    },
    "version_saved": {
        "zh": "新版本（v{n}）提交成功！可到「历史版本对比」查看变化。",
        "en": "New version (v{n}) saved! See the changes in \"Compare versions\".",
    },

    # ------------------------------------------------------------------
    # 版本对比 / Version compare
    # ------------------------------------------------------------------
    "versions_title": {"zh": "历史版本对比", "en": "Compare versions"},
    "versions_feature": {"zh": "历史版本对比", "en": "Compare versions"},
    "no_records_yet": {"zh": "还没有作文记录。", "en": "No essays yet."},
    "select_essay": {"zh": "选择作文", "en": "Choose an essay"},
    "essay_option_short": {
        "zh": "#{id} {title}（{date}）",
        "en": "#{id} {title} ({date})",
    },
    "only_one_version": {
        "zh": "这篇作文只有一个版本，先到「继续改写」提交新版本，再回来对比。",
        "en": "This essay has only one version. Submit a revision in \"Keep revising\" first.",
    },
    "version_a": {"zh": "版本 A", "en": "Version A"},
    "version_b": {"zh": "版本 B", "en": "Version B"},
    "version_stat": {
        "zh": "**版本 {no}**（{wc} 字，{score} 分）",
        "en": "**Version {no}** ({wc} words, score {score})",
    },
    "word_delta": {"zh": "字数变化", "en": "Word count change"},
    "score_delta": {"zh": "总分变化", "en": "Score change"},

    # ------------------------------------------------------------------
    # 成长档案 / Growth
    # ------------------------------------------------------------------
    "no_growth_yet": {"zh": "还没有成长记录。", "en": "No growth records yet."},
    "col_time": {"zh": "时间", "en": "Time"},
    "col_topic": {"zh": "题目", "en": "Topic"},
    "col_wordcount": {"zh": "字数/词数", "en": "Words"},
    "col_score": {"zh": "总分", "en": "Score"},
    "total_practices": {"zh": "累计练习次数", "en": "Total essays"},
    "avg_words": {"zh": "平均字数/词数", "en": "Average words"},
    "avg_score": {"zh": "平均总分", "en": "Average score"},

    # ------------------------------------------------------------------
    # 会员中心 / Membership
    # ------------------------------------------------------------------
    "member_center": {"zh": "会员中心", "en": "Member center"},
    "already_member": {
        "zh": "你已是会员，有效期至 {date}。",
        "en": "You are a premium member until {date}.",
    },
    "free_tier_desc": {
        "zh": "当前为免费版：每天 {n} 次 AI 点评；会员可享不限次 AI 点评、英语 AI 精批、手写识别、看图作文、继续改写与版本对比。",
        "en": "You are on the free tier: {n} AI reviews per day. Premium unlocks unlimited AI reviews, English AI grading, handwriting recognition, picture writing, revising and version compare.",
    },
    "plan_table": {
        "zh": "| 套餐 | 价格 |\n|---|---|\n| 月度会员 | **{month} 元 / 月** |\n| 年度会员 | **{year} 元 / 年**（约 {permonth} 元/月） |",
        "en": "| Plan | Price |\n|---|---|\n| Monthly | **{month} CNY / month** |\n| Yearly | **{year} CNY / year** (≈ {permonth} CNY/month) |",
    },
    "choose_plan": {"zh": "选择套餐", "en": "Choose a plan"},
    "plan_month": {"zh": "月度会员", "en": "Monthly plan"},
    "plan_year": {"zh": "年度会员", "en": "Yearly plan"},
    "create_order_btn": {"zh": "生成付款订单", "en": "Create payment order"},
    "order_line": {
        "zh": "#### 订单号：`{order_no}`（{amount} 元）",
        "en": "#### Order no.: `{order_no}` ({amount} CNY)",
    },
    "scan_qr": {
        "zh": "请扫码支付，并在转账备注中填写订单号",
        "en": "Scan to pay and put the order number in the transfer note",
    },
    "contact_admin_qr": {
        "zh": "请联系管理员获取收款二维码，支付时备注订单号。",
        "en": "Contact the admin for the payment QR code; include the order number in the note.",
    },
    "pay_note": {
        "zh": "请在家长指导下完成支付。管理员确认到账后会员自动开通。",
        "en": "Please pay with a parent's guidance. Premium activates once the admin confirms the payment.",
    },
    "use_activation_code": {"zh": "使用激活码", "en": "Use an activation code"},
    "enter_code": {"zh": "输入激活码", "en": "Enter activation code"},
    "activate_btn": {"zh": "激活会员", "en": "Activate premium"},

    # ------------------------------------------------------------------
    # 家长端 / Parent
    # ------------------------------------------------------------------
    "parent_home": {"zh": "家长端", "en": "Parent workspace"},
    "no_bound_students": {
        "zh": "暂无已绑定学生，请联系管理员绑定。",
        "en": "No linked students yet. Ask the admin to link one.",
    },
    "select_student": {"zh": "选择学生", "en": "Select student"},
    "growth_trend": {"zh": "成长趋势", "en": "Growth trend"},

    # ------------------------------------------------------------------
    # 管理员端 / Admin
    # ------------------------------------------------------------------
    "admin_home": {"zh": "管理员端", "en": "Admin console"},
    "tab_dashboard": {"zh": "总体运营", "en": "Operations"},
    "tab_accounts": {"zh": "账号管理", "en": "Accounts"},
    "tab_ai_status": {"zh": "AI 状态", "en": "AI status"},
    "tab_parent_links": {"zh": "家长绑定", "en": "Parent links"},
    "tab_orders": {"zh": "订单核销", "en": "Orders"},
    "tab_codes": {"zh": "激活码", "en": "Activation codes"},
    "ops_overview": {"zh": "总体运营情况", "en": "Operations overview"},
    "m_users_total": {"zh": "注册用户", "en": "Registered users"},
    "m_new_7d": {"zh": "近7天 +{n}", "en": "+{n} in 7 days"},
    "m_submissions": {"zh": "作文提交总数", "en": "Total submissions"},
    "m_today": {"zh": "今日 {n}", "en": "{n} today"},
    "m_ai_calls": {"zh": "AI 点评次数（免费额度）", "en": "AI reviews (free quota)"},
    "m_members": {"zh": "有效会员", "en": "Active members"},
    "m_students": {"zh": "学生", "en": "Students"},
    "m_teachers": {"zh": "老师", "en": "Teachers"},
    "m_disabled": {"zh": "已注销账号", "en": "Deactivated accounts"},
    "m_revenue": {"zh": "已核销收入（元）", "en": "Confirmed revenue (CNY)"},
    "m_pending_orders": {"zh": "待核销订单 {n}", "en": "{n} pending orders"},
    "role_composition": {"zh": "各角色账号构成", "en": "Accounts by role"},
    "col_role": {"zh": "角色", "en": "Role"},
    "col_count": {"zh": "数量", "en": "Count"},
    "role_student": {"zh": "学生", "en": "student"},
    "role_teacher": {"zh": "老师", "en": "teacher"},
    "role_parent": {"zh": "家长", "en": "parent"},
    "role_admin": {"zh": "管理员", "en": "admin"},
    "trend_14d": {"zh": "近 14 天作文提交趋势", "en": "Submissions in the last 14 days"},
    "no_recent_submissions": {
        "zh": "近 14 天暂无提交。",
        "en": "No submissions in the last 14 days.",
    },
    "account_list": {"zh": "账号列表", "en": "Account list"},
    "col_username": {"zh": "用户名", "en": "Username"},
    "col_realname": {"zh": "姓名", "en": "Name"},
    "col_grade": {"zh": "年级", "en": "Grade"},
    "col_status": {"zh": "状态", "en": "Status"},
    "col_registered": {"zh": "注册时间", "en": "Registered"},
    "status_active": {"zh": "正常", "en": "active"},
    "status_disabled": {"zh": "已注销", "en": "deactivated"},
    "manual_create_account": {"zh": "人工开通账号", "en": "Create account manually"},
    "role_label": {"zh": "角色", "en": "Role"},
    "class_label": {"zh": "班级", "en": "Class"},
    "initial_password": {"zh": "初始密码", "en": "Initial password"},
    "create_account_btn": {"zh": "创建账号", "en": "Create account"},
    "deactivate_reactivate": {
        "zh": "注销 / 重新开通账号",
        "en": "Deactivate / reactivate account",
    },
    "select_account": {"zh": "选择账号", "en": "Select account"},
    "account_option": {
        "zh": "{username}（{name}，{role}，{status}）",
        "en": "{username} ({name}, {role}, {status})",
    },
    "deactivate_btn": {
        "zh": "注销该账号（停用登录，数据保留）",
        "en": "Deactivate (block login, keep data)",
    },
    "reactivate_btn": {"zh": "重新开通该账号", "en": "Reactivate account"},
    "reset_password_hdr": {"zh": "重置密码", "en": "Reset password"},
    "new_password": {"zh": "新密码", "en": "New password"},
    "reset_password_btn": {"zh": "重置所选账号密码", "en": "Reset selected account's password"},
    "ai_service_status": {"zh": "AI 服务状态", "en": "AI service status"},
    "ai_configured": {
        "zh": "已配置 AI 服务：模型 `{model}`，接口 `{base_url}`",
        "en": "AI configured: model `{model}`, endpoint `{base_url}`",
    },
    "ai_not_configured": {
        "zh": "未配置 OPENAI_API_KEY —— 学生只能收到本地基础点评，不会调用 AI。请在环境变量或 .streamlit/secrets.toml 中设置 OPENAI_API_KEY 后重启应用。",
        "en": "OPENAI_API_KEY is not configured — students only get local basic feedback and the AI is never called. Set OPENAI_API_KEY via environment variable or .streamlit/secrets.toml, then restart.",
    },
    "ai_last_success": {"zh": "最近一次 AI 调用成功：{at}", "en": "Last successful AI call: {at}"},
    "ai_last_error": {"zh": "最近一次 AI 调用失败：{err}", "en": "Last AI call failure: {err}"},
    "test_ai_btn": {"zh": "测试 AI 连接", "en": "Test AI connection"},
    "testing_ai": {"zh": "正在调用 AI ...", "en": "Calling the AI ..."},
    "parent_username": {"zh": "家长用户名", "en": "Parent username"},
    "student_username": {"zh": "学生用户名", "en": "Student username"},
    "link_btn": {"zh": "绑定家长与学生", "en": "Link parent and student"},
    "linked_ok": {"zh": "已绑定。", "en": "Linked."},
    "no_pending_orders": {"zh": "暂无待核销订单。", "en": "No pending orders."},
    "select_order": {"zh": "选择订单", "en": "Select order"},
    "confirm_order_btn": {"zh": "确认到账并开通会员", "en": "Confirm payment & activate"},
    "plan_label": {"zh": "套餐", "en": "Plan"},
    "plan_month_short": {"zh": "月度", "en": "Monthly"},
    "plan_year_short": {"zh": "年度", "en": "Yearly"},
    "gen_code_btn": {"zh": "生成激活码", "en": "Generate activation code"},
    "code_created": {
        "zh": "激活码：`{code}`（一次性，请线下发给用户）",
        "en": "Activation code: `{code}` (one-time; hand it to the user offline)",
    },

    # ------------------------------------------------------------------
    # 点评展示 / Feedback display
    # ------------------------------------------------------------------
    "feedback_title": {"zh": "作文点评结果", "en": "Essay feedback"},
    "by_ai": {"zh": "✅ 本次点评由 AI 智能生成。", "en": "✅ This feedback was generated by the AI."},
    "fallback_generic": {
        "zh": "本次为本地基础点评（AI 暂不可用）。",
        "en": "This is local basic feedback (AI unavailable).",
    },
    "fb_quota": {
        "zh": "今日免费 AI 点评已用完，本次为本地基础点评（不限次）。升级会员可享不限次 AI 智能点评。",
        "en": "Your free daily AI reviews are used up, so this is local basic feedback (always unlimited). Upgrade to premium for unlimited AI reviews.",
    },
    "fb_no_api_key": {
        "zh": "系统尚未配置 AI 服务（OPENAI_API_KEY），本次为本地基础点评。请联系管理员开启 AI 点评。",
        "en": "The AI service (OPENAI_API_KEY) is not configured, so this is local basic feedback. Ask the admin to enable AI reviews.",
    },
    "fb_rate_limited": {
        "zh": "请求过于频繁已被限流，本次为本地基础点评。稍等一分钟再试即可使用 AI 点评。",
        "en": "Too many requests, so this is local basic feedback. Wait a minute and try again for AI feedback.",
    },
    "fb_api_error": {
        "zh": "AI 服务暂时不可用，本次为本地基础点评。稍后重试，或联系管理员查看「AI 状态」。",
        "en": "The AI service is temporarily unavailable, so this is local basic feedback. Retry later or ask the admin to check \"AI status\".",
    },
    "teacher_version": {"zh": "教师点评版", "en": "Teacher-style feedback"},
    "student_version": {"zh": "学生鼓励版", "en": "Student-friendly feedback"},
    "strengths": {"zh": "优点", "en": "Strengths"},
    "suggestions": {"zh": "改进建议", "en": "Suggestions"},
    "polished": {"zh": "佳句润色", "en": "Polished sentence"},
    "grammar_fixes": {"zh": "语法与拼写订正", "en": "Grammar & spelling fixes"},
    "step_rewrite_hdr": {"zh": "分步改写", "en": "Step-by-step revision"},
}


def tr(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    """取指定语言文案；缺失时回退中文，再缺失则原样返回 key。"""
    entry = TEXTS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
