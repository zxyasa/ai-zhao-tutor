# Task: phase8-gate
Created: 2026-02-21
Status: active

## Goal
Phase 8 多租户认证系统正式关闭：修复测试基础设施 → 逐项执行 DoD 14 条 → 安全专项 5 条 → 签字关闭

## EDP Reference
ENGINEERING_DELIVERY_PLAN.md — Part 4, "Phase 8 收口 WBS"
WBS 任务 ID: W8C-00 ~ W8C-02, W8D-01 ~ W8D-14, W8S-01 ~ W8S-05, W8X-01 ~ W8X-03

## Scope
- 修复 pytest venv（W8C-00）
- 创建迁移执行工具 ops/migrations/run_migration.py（W8C-01）
- 执行 M-000 初始化迁移版本表（W8C-02）
- Phase 8 DoD 14 条逐一验证（W8D-01 ~ W8D-14）
- 安全专项 5 条（W8S-01 ~ W8S-05）
- 更新进展快照、打 git tag（W8X-01 ~ W8X-03）

## Out of Scope
- Phase 7 GAP 修复（→ 见 phase7-gap-fix 任务）
- Phase 8.5 新功能开发

## Acceptance Criteria
- [ ] `pytest services/api/tests/ -v --tb=short` 最后一行含 "passed, 0 failed"
- [ ] 安全专项 W8S-01 ~ W8S-05 全通过
- [ ] UPGRADE_PLAN_2026.md 进展快照 Phase 8 → ✅
- [ ] git tag `phase8-closed-20260221` 已创建
