# Progress: phase7-gap-fix
Last updated: 2026-02-21T00:00:00
Terminal: unknown
Current step: 1 / 6

## Completed
(none yet)

## Current
- [ ] Step 1/6: W7G-01 — 执行 M-001 迁移
  - Status: pending
  - Notes: 需先确认迁移工具存在（phase8-gate W8C-01 创建）；迁移前备份 DB

## Remaining
- [ ] Step 2/6: W7G-02 — ORM 更新
- [ ] Step 3/6: W7G-03 — 滑动窗口服务
- [ ] Step 4/6: W7G-04 — protocol 新字段
- [ ] Step 5/6: W7G-05 — 引擎 ZPD 联动
- [ ] Step 6/6: W7G-06 — 全量回归

## Recovery Notes
- Step 1 依赖：`ops/migrations/run_migration.py` 必须存在（由 phase8-gate W8C-01 创建）
- M-001 SQL 内容见 ENGINEERING_DELIVERY_PLAN.md Part 3.3
- 迁移前必须备份：`cp data/mathcoach.db data/backup_$(date +%Y%m%d).db`
- SQLite DROP COLUMN 需版本 ≥ 3.35，先运行 `sqlite3 --version` 确认
