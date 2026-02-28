# Context: phase7-gap-fix
Last updated: 2026-02-21

## Key Files (ONLY read these on resume)
- `ENGINEERING_DELIVERY_PLAN.md` — Part 3.3（M-001 SQL）+ Part 4 W7G 系列 DoD
- `services/api/app/models/mastery.py` — 当前 ORM，需新增 5 字段
- `services/api/app/services/mastery_service.py` — 掌握度计算，需加滑动窗口逻辑
- `services/api/app/engine/protocol.py` — SelectionRequest/Result，需加 zpd_zone/flow_signal
- `services/api/app/engine/adaptive.py` — 选题引擎，需读取 zpd_zone
- `services/api/tests/test_mastery_service.py` — 掌握度测试（需新增滑动窗口用例）
- `services/api/tests/test_adaptive_engine.py` — 引擎测试（需新增 ZPD 用例）
- `ops/migrations/` — 迁移脚本目录

## Architecture Notes
- Mastery 表当前字段：student_id, skill_id, total_attempts, correct_attempts, mastery_score, last_updated
- 新增字段（M-001）：last_n_results(TEXT/JSON), score_trend(TEXT), next_review_at(TIMESTAMP), review_interval_days(INT), review_streak(INT)
- 滑动窗口逻辑：last_n_results 存最近 10 次结果的 JSON 数组（[1,0,1,1,0,...]）
- ZPD 区间：frustration(<40%) / zpd(40-80%) / comfort(>90% + 低用时)
- protocol.py 新增可选字段（Optional），不破坏现有调用

## Recent Changes Summary
任务刚创建（2026-02-21）。Phase 7 功能按快照标记为完成，但代码扫描显示
mastery.py 和 protocol.py 未见新字段（GAP-01, GAP-02）。

## Search Hints
- 找 mastery 更新逻辑：grep "mastery_score" services/api/app/services/mastery_service.py
- 找引擎选题逻辑：grep "difficulty" services/api/app/engine/adaptive.py
- 找现有测试结构：grep "def test_" services/api/tests/test_adaptive_engine.py
