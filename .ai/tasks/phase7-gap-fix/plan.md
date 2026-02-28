# Plan: phase7-gap-fix
EDP Reference: ENGINEERING_DELIVERY_PLAN.md Part 4 → Phase 7 GAP 修复 WBS

## Steps

- [ ] Step 1/6: W7G-01 — 执行 M-001 迁移（mastery 表新增 5 字段）
  Files: `ops/migrations/M-001__mastery_phase7_fields.sql`, DB
  Risk: MEDIUM（DB schema 变更，需先备份）| Effort: S
  DoD: `sqlite3 data/mathcoach.db ".schema mastery"` 显示 last_n_results, score_trend, next_review_at, review_interval_days, review_streak

- [ ] Step 2/6: W7G-02 — 更新 models/mastery.py ORM 映射
  Files: `services/api/app/models/mastery.py`
  Risk: LOW | Effort: S
  DoD: `python -c "from app.models.mastery import Mastery; print(Mastery.__table__.columns.keys())"` 包含新字段

- [ ] Step 3/6: W7G-03 — mastery_service.py 实现滑动窗口更新
  Files: `services/api/app/services/mastery_service.py`
  Risk: MEDIUM | Effort: M
  DoD: `pytest tests/test_mastery_service.py::test_sliding_window -v` 通过

- [ ] Step 4/6: W7G-04 — protocol.py 新增 zpd_zone + flow_signal
  Files: `services/api/app/engine/protocol.py`
  Risk: LOW | Effort: S
  DoD: `grep "zpd_zone\|flow_signal" services/api/app/engine/protocol.py` 有输出

- [ ] Step 5/6: W7G-05 — adaptive.py 读取 zpd_zone 调整难度
  Files: `services/api/app/engine/adaptive.py`
  Risk: MEDIUM | Effort: M
  DoD: `pytest tests/test_adaptive_engine.py::test_zpd_frustration_zone -v` 通过

- [ ] Step 6/6: W7G-06 — 全量回归
  Files: tests
  Risk: LOW | Effort: S
  DoD: `pytest services/api/tests/ -v --tb=short` 零失败

## Dependencies
- 需要 phase8-gate Step 1（pytest venv）完成后才能运行测试
- 不阻塞 phase8-gate（可并行，不修改同一文件）

## Estimated Token Budget
Total steps: 6 | High-risk steps: Step 1, 3 | Recommend: 1-2 sessions
