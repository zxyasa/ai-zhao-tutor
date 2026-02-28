# Progress: phase8-gate
Last updated: 2026-02-21T17:08:00
Terminal: codex-cli
Current step: 9 / 9

## Completed
- [x] Step 1/9: W8C-00 — 安装 pytest venv
  - Status: completed
  - Notes:
    - 使用 `python3` (3.13.2) 重建 `services/api/.venv`
    - 兼容性修复后执行 `cd services/api && .venv/bin/pytest --collect-only -q`
    - 结果：`41 tests collected in 0.35s`
- [x] Step 2/9: W8C-01 — 创建迁移执行工具
  - Status: completed
  - Notes:
    - 新建 `ops/migrations/run_migration.py`
    - 支持 `status/up/down`，默认数据库 `services/api/mathcoach.db`
    - 验证：`python3 ops/migrations/run_migration.py status` 输出 `schema_migrations table not found`
- [x] Step 3/9: W8C-02 — 执行 M-000（初始化版本表）
  - Status: completed
  - Notes:
    - 新建 `ops/migrations/M-000__init_migration_table.sql`
    - 执行：`python3 ops/migrations/run_migration.py up M-000`
    - 验证：`sqlite3 services/api/mathcoach.db "SELECT version, description FROM schema_migrations;"`
    - 结果：`M-000|init migration table`
- [x] Step 4/9: W8D-01~07 — 认证测试验证
  - Status: completed (with test-name drift)
  - Notes:
    - EDP 中若干测试名已不存在（如 `test_parent_register`）
    - 等价验证已执行并通过：
      - `tests/test_phase8_models.py::test_parent_student_relationship_fields`
      - `tests/test_auth_utils.py`（3 项）
      - `tests/test_phase8_api_authz.py`（3 项）
    - 汇总：`7 passed`
- [x] Step 5/9: W8D-08~11 — 代码审查
  - Status: completed (with findings)
  - Notes:
    - `student_id` 访问路径已审查，核心接口均通过 `require_student_access(...)` 收敛
    - `SECRET_KEY/secret_key` 引用集中在配置与 JWT 读取，无硬编码密钥常量
    - iOS 存在 `UserDefaults` 读取/清理旧 token 的迁移逻辑，无新增 token 写入
    - `test_bcrypt_cost_factor` 不存在；当前实现采用 `pbkdf2_sha256`（非 bcrypt）
- [ ] Step 6/9: W8D-12 — iOS 401 手动验证
  - Status: blocked (manual)
  - Notes:
    - 需真机/模拟器手动执行：token 过期后点击“下一题”应跳转 `AuthView`
- [x] Step 7/9: W8D-13~14 — 全量回归
  - Status: partial
  - Notes:
    - `test_legacy_data_migration` 不存在（测试名漂移）
    - 全量回归命令通过：`pytest tests/ -v --tb=short` → `41 passed`
- [x] Step 8/9: W8S-01~05 — 安全专项
  - Status: completed (with env notes)
  - Notes:
    - `W8S-03`：`git grep -i "hs256|my.secret|changeme"` 返回 0（通过）
    - `W8S-05`：`PYTHONPATH=. .venv/bin/python scripts/check_phase8_readiness.py` exit 0（通过）
    - `W8S-04`：已修复目标环境 `students.parent_id/pin_hash` 缺列后重跑 smoke（通过）
    - `W8S-01/W8S-02`：当前实现为 `pbkdf2_sha256`，哈希落库校验通过（非 `$2b$`）
- [x] Step 9/9: W8X-01~03 — 关闭动作
  - Status: completed (pending manual sign-off)
  - Notes:
    - 已更新 `UPGRADE_PLAN_2026.md` Phase 8 快照状态
    - 已更新 `ENGINEERING_DELIVERY_PLAN.md` Part 1 基线核查状态
    - 已创建 DB 备份：`backups/phase8-baseline-20260221-1516.db`
    - 已补齐 `ENGINEERING_DELIVERY_PLAN.md` 中漂移验收命令与哈希口径（PBKDF2）
    - 已补齐 `ops/migrations/M-000__init_migration_table.down.sql`
    - 已输出 QA 报告：`docs/qa/phase8_gate_report.md`

## Current
- [ ] Manual sign-off
  - Status: pending
  - Notes:
    - 仅剩 W8D-12 手工验证（iPad 无法安装新包）

## Remaining
- [ ] W8D-12 手工验证签字

## Recovery Notes
- 当前 venv：`services/api/.venv` (Python 3.13.2)
- 迁移工具路径：`ops/migrations/run_migration.py`（已创建）
- 关键输出：
  - `cd services/api && .venv/bin/pytest tests/ -v --tb=short` → `41 passed`
  - `python3 ops/migrations/run_migration.py status` 可见 `M-000`
  - 备份文件：`backups/phase8-baseline-20260221-1516.db`
  - 运行环境修复：
    - `docker exec mathcoach-api python scripts/seed_students.py` 已补齐 `students.parent_id/pin_hash`
    - `phase8` 全链路 smoke（parent+student）已通过
    - `services/api/app/database.py` 已并入启动自愈补列逻辑（SQLite/PostgreSQL）
  - 线上绑定：
    - `jon_zhao`/`astrid_zhao` 已绑定 `michael@micleah.com`
  - iOS 当前阻塞：
    - 旧包存在 “退出登录” 旧逻辑；题目白色问题已在代码修复（`QuestionView.swift` 文字设为黑色），待安装新包生效
  - 状态同步：
    - `.ai/tasks/phase8-gate/plan.md` 已按真实进度更新
    - `ENGINEERING_DELIVERY_PLAN.md` 的“立即行动项/任务看板”已同步为最新状态
