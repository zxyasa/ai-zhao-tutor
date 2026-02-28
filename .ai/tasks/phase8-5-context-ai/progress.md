# Progress: phase8-5-context-ai
Last updated: 2026-02-21T10:07:02
Terminal: codex-cli
Current step: 9 / 13

## Completed
- [x] Step 1/9: 规划阶段（W85 拆解）
  - Status: completed
  - Notes:
    - 已对齐 EDP `W85-01 ~ W85-16`，拆为 9 步执行
    - 优先后端可验证闭环，再做 iOS 展示层
    - 保留与现有代码兼容，避免破坏 Phase 8 既有测试

- [x] Step 2/9: W85-01 — 创建 Phase 8.5 前基线备份
  - Status: completed
  - Notes:
    - SQLite 备份：`backups/phase8_5-baseline-20260221-155022.db`
    - PostgreSQL dump：`backups/phase8_5-baseline-20260221-155117.sql`

- [x] Step 3/9: W85-02~03 — M-002 迁移 + ORM 模型
  - Status: completed
  - Notes:
    - 新增 `ops/migrations/M-002__parent_context_events.sql`
    - 新增模型 `services/api/app/models/parent_context_event.py`
    - 已导出模型：`services/api/app/models/__init__.py`
    - 迁移验证：`python3 ops/migrations/run_migration.py up M-002`（已记录），`parent_context_events` 表存在

- [x] Step 4/9: W85-04~05 — context_ai_service + 缺 key 503
  - Status: completed
  - Notes:
    - 新增 `services/api/app/services/context_ai_service.py`
    - 新增 `services/api/tests/test_context_ai_service.py`
    - `services/api/app/config.py` 已增加 `anthropic_api_key`
    - 验证：`pytest tests/test_context_ai_service.py -v` → `2 passed`

- [x] Step 5/9: W85-06~08 — 协议与引擎 hint 集成 + 测试
  - Status: completed
  - Notes:
    - `engine/protocol.py` 新增 `engine_hint`
    - `engine/adaptive.py` 支持 `engine_hint` 难度微调
    - 新增测试通过：
      - `test_engine_hint_reduces_difficulty`
      - `test_engine_hint_none_no_effect`

## Current
- [x] Step 6/9: W85-09~11 — parent/context 路由 + daily-summary ai_insight + config
  - Status: completed
  - Notes:
    - 新增 `POST /api/v1/parent/context`（parent scope + student ownership 校验）
    - `daily-summary` 响应新增 `ai_insight`
    - `/next-item` 已接入最新 context `engine_hint`
    - 验证：
      - `pytest tests/test_parent_summary.py::test_daily_summary_has_ai_insight -v`
      - `pytest tests/test_phase8_api_authz.py::test_parent_scope_requires_student_id_and_blocks_other_family -v`

- [x] Step 7/9: W85-12~14 — iOS 输入卡片 + 展示 + 模型字段
  - Status: completed
  - Notes:
    - `ParentDailySummary` 已增加 `aiInsight`
    - `APIClient` 已增加 `submitParentContext(...)`
    - `ParentDashboardView` 已增加“今日情况”输入卡片与 AI 洞察展示位

- [x] Step 8/9: W85-15 — 全量回归
  - Status: completed
  - Notes:
    - 执行：`cd services/api && .venv/bin/pytest tests/ -v --tb=short`
    - 结果：`47 passed`

- [ ] Step 9/13: W85-16 — DoD 对照与收口
  - Status: in_progress
  - Notes:
    - 后端 DoD 已达成并验证
    - iOS 新增卡片与字段代码已完成，待安装新包后做手工验收
    - provider 切换：`context_ai_service` 已从 Anthropic 改为 OpenAI（`OPENAI_API_KEY`）
    - 运行环境：`mathcoach-api` 容器已注入 `OPENAI_API_KEY` 并重建
    - 验证：`POST /api/v1/parent/context`（无 `student_id`）返回 `201`
    - iOS 登录体验：`AuthView` 新增 Face ID 快速填充上次账号（保存账号类型+邮箱/学生ID，不保存密码/PIN）
    - 2026-02-21 hotfix：`AuthView.restoreSavedProfileWithBiometrics()` 持有 `LAContext` 避免点击无响应，并支持设备密码回退
    - 2026-02-21 UX 调整：`AuthView.onAppear` 自动触发一次身份验证（有缓存账号且输入框为空时）
    - 2026-02-21 UX 调整：学生角色隐藏“切换学生”；登录页移除手动 Face ID 按钮，仅保留自动验证
    - 2026-02-21 UX 调整：登录失败错误文案本地化（密码错误/学生PIN错误/网络错误/服务错误统一友好提示）
    - 2026-02-21 新增能力：家长可在家长面板“添加学生”（后端 `POST /parent/students` + iOS 表单）
    - 2026-02-21 UX 调整：家长面板新增 Student Accounts 列表，支持随时查看/复制 student_id
    - 2026-02-21 hotfix：将 `Student Accounts / Account Security` 移入同一滚动区，修复日报内容被挤出视口问题
    - 2026-02-21 UX 调整：登录页导航标题改为 `AJ Math Tutor`（与应用显示名一致）
    - iOS 应用显示名已改为 `AJ Math Tutor`（Debug/Release）
    - 2026-02-21 hotfix：`QuestionViewModel.submitAnswer()` 在 parent role 下补传 `student_id`，修复提交答案 `HTTP 400 student_id required`
    - 2026-02-21 新增能力：家长自助修改密码（`POST /parent/change-password` + iOS Account Security 表单）
    - 2026-02-21 新增能力：创建学生后邮件通知（可配置开关 + 重试 + 失败不阻塞创建）
    - 回归：`pytest tests/test_phase8_api_authz.py tests/test_parent_notification_service.py -q` → `12 passed`
    - 全量回归：`cd services/api && .venv/bin/pytest tests/ -q` → `55 passed`

## Remaining
- [ ] W85-12/W85-13 手工验收（iOS 新包）
- [ ] W85-16 最终签字
- [ ] 新增需求：家长自助修改密码（后端 API + iOS 页面入口 + 测试）
- [ ] 新增需求：家长添加学生（iPad 真机流程验收）
- [ ] 新增需求：新学生创建后邮件通知家长（可配置开关 + 失败重试）
- [ ] 配置并联调 SMTP（`SEND_PARENT_EMAIL_ON_STUDENT_CREATE=true`）后做一次真发信验收

## Recovery Notes
- 当前重点文件已识别：parent router、adaptive engine、config、ParentDashboardView、ParentDailySummary
- 已完成：
  - W85-01：基线备份（SQLite + PostgreSQL dump）
  - W85-02/03：M-002 + ParentContextEvent 模型
  - W85-04/05：context_ai_service + 缺 key 503
  - W85-06/07/08：engine_hint 协议/引擎集成 + 新测试
  - W85-09/10/11：`/parent/context`、`daily-summary.ai_insight`、config key
  - W85-12/13/14：iOS 模型/API/页面提交与展示代码
  - W85-15：全量回归 47 通过
