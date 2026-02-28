# Plan: phase8-gate
EDP Reference: ENGINEERING_DELIVERY_PLAN.md Part 4 → Phase 8 收口 WBS

## Steps

### 阶段一：基础设施（必须先完成，否则无法运行测试）
- [x] Step 1/9: W8C-00 — 安装 pytest venv
  Files: `services/api/requirements.txt`
  Risk: LOW | Effort: S
  DoD: `cd services/api && pip install -r requirements.txt && python -m pytest --collect-only -q` 无报错

- [x] Step 2/9: W8C-01 — 创建迁移执行工具
  Files: `ops/migrations/run_migration.py`, `ops/migrations/M-000__init_migration_table.sql`
  Risk: LOW | Effort: M
  DoD: `python ops/migrations/run_migration.py status` 输出版本表内容

- [x] Step 3/9: W8C-02 — 执行 M-000
  Files: DB（`data/mathcoach.db`）
  Risk: LOW | Effort: XS
  DoD: `sqlite3 data/mathcoach.db "SELECT * FROM schema_migrations"` 返回空行（表存在）

### 阶段二：DoD 认证验证（Step 4 批量跑测试，记录哪些缺失需补充）
- [x] Step 4/9: W8D-01~07 — 运行认证相关测试，记录缺失用例
  Files: `services/api/tests/test_phase8_*.py`, `test_auth_*.py`
  Risk: MEDIUM | Effort: M
  DoD: 7 条 DoD 全 ✅；缺失的补写测试用例

- [x] Step 5/9: W8D-08~11 — 代码审查（安全设计）
  Files: `app/routers/*.py`, `apps/ios/`
  Risk: LOW | Effort: S
  DoD: grep 命令全返回 0（无 student_id 从 body 取；无 UserDefaults 存 token）

- [ ] Step 6/9: W8D-12 — iOS 401 回跳手动验证
  Files: `apps/ios/.../AuthView.swift`, `APIClient.swift`
  Risk: LOW | Effort: S（手动）
  DoD: token 过期后任意操作 → 自动跳转 AuthView

- [x] Step 7/9: W8D-13~14 — 历史数据迁移 + 全量回归
  Files: tests
  Risk: MEDIUM | Effort: M
  DoD: 全量 pytest 零失败

### 阶段三：安全专项
- [x] Step 8/9: W8S-01~05 — 安全专项 5 项
  Files: DB, git history, config
  Risk: 🔴 任何失败 = 当前 Phase 冻结
  DoD: 5 条全通过（sqlite3 查询 + grep + smoke 脚本）

### 阶段四：关闭
- [x] Step 9/9: W8X-01~03 — 更新文档 + 备份 + git tag
  Files: `UPGRADE_PLAN_2026.md`, `ENGINEERING_DELIVERY_PLAN.md`, `data/`
  Risk: LOW | Effort: XS

## Dependencies
- phase7-gap-fix 任务**不阻塞**本任务（并行执行）
- Phase 8.5 必须等本任务 Step 9 完成后才能开始

## Estimated Token Budget
Total steps: 9 | High-risk steps: Step 8 | Recommend: 2-3 sessions

## Current Gate
- Remaining manual item: Step 6/9 (W8D-12, iOS `401 -> AuthView` on updated app build)
