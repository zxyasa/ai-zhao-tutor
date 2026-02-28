# Context: phase8-gate
Last updated: 2026-02-21

## Key Files (ONLY read these on resume)
- `ENGINEERING_DELIVERY_PLAN.md` — WBS 权威来源，Part 4 是本任务全部任务定义
- `services/api/requirements.txt` — pip 依赖（Step 1 需要）
- `services/api/tests/test_phase8_api_authz.py` — Phase 8 HTTP 权限测试
- `services/api/tests/test_phase8_models.py` — Phase 8 ORM 注册/PIN 测试
- `services/api/tests/test_auth_dependencies.py` — JWT role 依赖测试
- `services/api/tests/test_auth_utils.py` — bcrypt / JWT encode 测试
- `services/api/app/auth/dependencies.py` — require_parent / require_student 实现
- `services/api/app/config.py` — production_validation_errors()
- `services/api/scripts/check_phase8_readiness.py` — 生产配置检查（W8S-05）
- `services/api/scripts/smoke_phase8_auth.py` — 跨家长数据隔离 smoke test（W8S-04）
- `ops/migrations/` — 迁移脚本目录（W8C-01 需创建）
- `ops/migrations/run_migration.py` — SQLite 迁移执行器（status/up/down）
- `ops/migrations/M-000__init_migration_table.sql` — 初始版本表迁移
- `ops/migrations/M-000__init_migration_table.down.sql` — M-000 回滚脚本
- `services/api/app/database.py` — `init_db()` 已加入 schema 自愈补列逻辑
- `docs/qa/phase8_gate_report.md` — Phase 8 收口 QA 报告

## Architecture Notes
- 认证层：`auth/dependencies.py` 已实现 require_parent/require_student/require_student_access
- DB：SQLite，无 Alembic，用手动 SQL 脚本管理迁移（见 EDP Part 3）
- JWT：role 字段区分 parent/student；student_id 只从 token.sub 取
- iOS：KeychainStore.swift 存 token；401 应触发跳转 AuthView.swift

## Recent Changes Summary
本轮已完成 W8C~W8X 自动化部分：
- `services/api/.venv` 已建立并可成功 `pytest --collect-only`（41 tests）
- `services/api/requirements.txt` 已升级为 Python 3.13 兼容依赖
- `ops/migrations/run_migration.py` 已创建，`status` 可运行
- 已完成 W8C-02：`M-000` 已应用，`schema_migrations` 可查询
- 已完成全量回归：`41 passed`
- 已更新 `UPGRADE_PLAN_2026.md` 与 `ENGINEERING_DELIVERY_PLAN.md` 的 Phase 8 状态
- 已生成 DB 快照：`backups/phase8-baseline-20260221-1516.db`
- 已完成运行环境修复：`students.parent_id/pin_hash` 缺列已补齐，W8S-04 smoke 通过
- `jon_zhao` 与 `astrid_zhao` 已绑定 `michael@micleah.com`
- iOS 侧已修复：
  - `ContentView.logout()` 改为本地清 token（避免通知循环）
  - `QuestionView` 题目文字固定黑色（修复白底看不见）
- EDP 已同步真实验收命令（测试名漂移、PBKDF2 口径、脚本运行命令）
- 仍待人工闭环：W8D-12（401 -> AuthView 手测，需安装新包到 iPad）

## Search Hints
- 找认证逻辑：grep "require_parent\|require_student" services/api/app/routers/
- 找 student_id 来源：grep "student_id" services/api/app/routers/ --include="*.py"
- 找 iOS token 存储：grep "UserDefaults\|Keychain" apps/ios/
- 迁移工具：ops/migrations/（目录存在但 run_migration.py 尚未创建）
