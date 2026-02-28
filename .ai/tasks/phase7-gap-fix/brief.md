# Task: phase7-gap-fix
Created: 2026-02-21
Status: active (parallel with phase8-gate)

## Goal
修复 Phase 7 GAP：mastery 表新增滑动窗口字段 + ORM 更新 + 服务层实现 + protocol 新增 ZPD/心流字段

## EDP Reference
ENGINEERING_DELIVERY_PLAN.md — Part 1（GAP-01, GAP-02）+ Part 4 "Phase 7 GAP 修复 WBS"
WBS 任务 ID: W7G-01 ~ W7G-06

## Scope
- M-001 DB 迁移（mastery 表 +5 字段）
- `models/mastery.py` ORM 更新
- `services/mastery_service.py` 滑动窗口逻辑
- `engine/protocol.py` 新增 zpd_zone + flow_signal
- `engine/adaptive.py` 读取 zpd_zone 调整难度

## Out of Scope
- Phase 7.5 间隔重复调度（next_review_at 字段加了但逻辑留到 7.5）
- Phase 8 认证功能（→ 见 phase8-gate）

## Acceptance Criteria
- [ ] `sqlite3 data/mathcoach.db ".schema mastery"` 显示 5 个新字段
- [ ] `pytest tests/test_mastery_service.py -v` 全通过（含滑动窗口用例）
- [ ] `pytest tests/test_adaptive_engine.py -v` 全通过（含 ZPD 用例）
- [ ] 全量回归零失败
