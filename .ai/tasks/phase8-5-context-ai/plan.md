# Plan: phase8-5-context-ai

## Steps
- [x] Step 1: W85 任务拆解与执行顺序确定 | Files: `.ai/tasks/phase8-5-context-ai/progress.md` | Risk: low
- [x] Step 2: W85-01 基线备份（SQLite + PostgreSQL） | Files: `backups/` | Risk: low
- [x] Step 3: W85-02~03 M-002 迁移与 ORM 模型 | Files: `ops/migrations/M-002__parent_context_events.sql`, `services/api/app/models/parent_context_event.py`, `services/api/app/models/__init__.py` | Risk: medium
- [x] Step 4: W85-04~05 Context AI 服务与缺 key 处理 | Files: `services/api/app/services/context_ai_service.py`, `services/api/tests/test_context_ai_service.py`, `services/api/app/config.py` | Risk: medium
- [x] Step 5: W85-06~08 引擎 hint 协议与难度调节 | Files: `services/api/app/engine/protocol.py`, `services/api/app/engine/adaptive.py`, `services/api/tests/test_adaptive_engine.py` | Risk: medium
- [x] Step 6: W85-09~11 路由集成与日报 AI 洞察 | Files: `services/api/app/routers/parent.py`, `services/api/app/routers/items.py`, `services/api/tests/test_parent_summary.py` | Risk: medium
- [x] Step 7: W85-12~14 iOS 输入/展示接入 | Files: `apps/ios/MathCoach/MathCoach/Views/ParentDashboardView.swift`, `apps/ios/MathCoach/MathCoach/Models/ParentDailySummary.swift`, `apps/ios/MathCoach/MathCoach/Services/APIClient.swift` | Risk: medium
- [x] Step 8: W85-15 全量回归测试 | Files: `services/api/tests/` | Risk: low
- [ ] Step 9: W85-16 DoD 收口与手工验收 | Files: `.ai/tasks/phase8-5-context-ai/progress.md` | Risk: low
- [x] Step 10: 登录体验与权限 UX 修正（已完成） | Files: `apps/ios/MathCoach/MathCoach/Views/AuthView.swift`, `apps/ios/MathCoach/MathCoach/ContentView.swift` | Risk: medium
  - Delivered:
    - 登录页自动触发 Face ID/设备密码验证（保留账号填充，不保存密码/PIN）
    - 学生角色隐藏“切换学生”
    - 登录失败提示改为英文友好文案
- [ ] Step 11: 家长自助修改密码（新需求） | Files: `services/api/app/routers/parent.py`, `services/api/tests/test_phase8_api_authz.py`, `apps/ios/MathCoach/MathCoach/Views/ParentDashboardView.swift` | Risk: medium
  - DoD:
    - 提供已登录家长修改自己密码的 API（需旧密码校验、最小强度校验）
    - iOS 家长页面提供修改密码入口与提交表单
    - 新增后端用例覆盖成功/旧密码错误/弱密码三类场景
    - 完成一次手工验证并记录在 `progress.md`
  - Delivered:
    - 已实现 `POST /api/v1/parent/change-password`
    - 已实现 iOS 家长页 `Account Security` 修改密码表单
    - 已补后端测试并通过
- [ ] Step 12: 家长添加学生（新需求） | Files: `services/api/app/routers/parent.py`, `services/api/tests/test_phase8_api_authz.py`, `apps/ios/MathCoach/MathCoach/Services/APIClient.swift`, `apps/ios/MathCoach/MathCoach/Views/ParentDashboardView.swift` | Risk: medium
  - DoD:
    - 家长可在家长面板创建学生（姓名/年级/PIN）
    - 后端创建后自动绑定当前家长并返回 student profile
    - 覆盖后端测试（创建成功 + 学生 PIN 登录成功）
    - iPad 真机完成一次创建与登录验收
- [ ] Step 13: 新注册/新增学生邮件通知家长（新需求） | Files: `services/api/app/routers/parent.py`, `services/api/app/services/`, `services/api/tests/` | Risk: medium
  - DoD:
    - 新学生创建后向家长邮箱发送通知（可配置开关）
    - 邮件失败不阻塞创建流程，记录失败并可重试
    - 增加发送成功/失败测试用例
  - Delivered:
    - 新增 `parent_notification_service`（SMTP 发送 + 重试）
    - 创建学生流程已接入通知，失败仅告警不阻塞
    - 已补通知触发/失败不阻塞/重试测试并通过

## Dependencies
- W85-16 手工验收依赖 iPad 安装最新构建
- Step 11 依赖现有 parent JWT 登录态与 `users` 密码哈希逻辑可复用
- Step 12 依赖现有 `Student` 模型与 parent scope 鉴权
- Step 13 依赖可用 SMTP/API 邮件通道与配置管理

## Estimated Token Budget
Total steps: 13 | High-risk steps: 0 | Recommend: 3-4 sessions
