# Context: phase8-5-context-ai
Last updated: 2026-02-21T10:07:02

## Key Files (ONLY read these on resume)
- `ENGINEERING_DELIVERY_PLAN.md` — Phase 8.5 WBS 权威定义（W85-01~16）
- `services/api/app/routers/parent.py` — parent summary 路由与后续 context 入口
- `services/api/app/engine/adaptive.py` — 引擎难度权重调整逻辑
- `services/api/app/engine/protocol.py` — SelectionRequest/Result 协议
- `services/api/app/config.py` — 运行时配置（anthropic_api_key）
- `services/api/app/config.py` — 运行时配置（openai_api_key）
- `services/api/app/services/parent_notification_service.py` — 新增学生邮件通知（SMTP + retry）
- `services/api/app/models/__init__.py` — ORM 导出
- `services/api/app/models/parent_context_event.py` — 家长上下文事件模型
- `apps/ios/MathCoach/MathCoach/Views/ParentDashboardView.swift` — 家长端卡片 UI
- `apps/ios/MathCoach/MathCoach/ContentView.swift` — 登录页标题与角色菜单入口
- `apps/ios/MathCoach/MathCoach/Views/AuthView.swift` — Face ID 快速填充上次账号
- `apps/ios/MathCoach/MathCoach/Models/ParentDailySummary.swift` — ai_insight 字段
- `apps/ios/MathCoach/MathCoach/Services/APIClient.swift` — parent/context 提交接口
- `apps/ios/MathCoach/MathCoach/ViewModels/QuestionViewModel.swift` — parent role 提交答案时需携带 `student_id`
- `services/api/tests/test_parent_summary.py` — 父母摘要测试
- `services/api/tests/test_adaptive_engine.py` — 引擎测试
- `services/api/tests/test_context_ai_service.py` — Claude 服务测试
- `services/api/tests/test_phase8_api_authz.py` — parent/context 路由行为测试
- `services/api/tests/test_parent_notification_service.py` — 邮件通知重试/失败测试
- `ops/migrations/M-002__parent_context_events.sql` — Phase 8.5 数据迁移

## Architecture Notes
- 当前后端无 Alembic，采用手动迁移 SQL + 启动自愈策略
- `/api/v1/parent/daily-summary` 已带 `ai_insight`
- `select_next_item(...)` 已接入 `engine_hint`

## Recent Changes Summary
- W85-01~W85-11 已完成并通过后端测试
- W85-12~W85-14 iOS 代码已完成（需新包手测）
- iOS 热修复：parent role 提交事件已补传 `student_id`（修复 HTTP 400）
- iOS 登录优化：自动触发 Face ID/设备密码填充上次账号基础信息（邮箱/学生ID）
- iOS 家长页新增：添加学生、Student ID 可复制列表、Account Security 改密码
- 后端新增：`POST /parent/change-password`、`POST /parent/students` 邮件通知接入
- AI provider 已切换到 OpenAI，容器环境已注入 `OPENAI_API_KEY`
- 最新回归：`pytest tests/test_phase8_api_authz.py tests/test_parent_notification_service.py -q` → `12 passed`
- 剩余：iOS 手工验收、SMTP 联调验收与 W85-16 最终签字

## Search Hints
- `rg -n "daily-summary|parent/" services/api/app/routers/parent.py`
- `rg -n "select_next_item|difficulty" services/api/app/engine/adaptive.py`
- `rg -n "ParentDailySummary|ParentDashboardView" apps/ios/MathCoach/MathCoach`
