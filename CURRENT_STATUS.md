# MathCoach 当前功能状态

**最后更新：** 2026-02-21

## 🎯 项目概述
AI 数学训练系统（FastAPI + iOS），面向 Jon / Astrid 双学生场景。
当前状态：**Phase 7 可视化收口已完成**，**Phase 8 已推进到发布收尾与上线准备阶段**。

---

## ✅ 已落地能力

### 1) 内容与题库（Phase 2）
- ✅ NSW Year 3-6 技能树：20 skills
- ✅ 题库规模：1275 items
- ✅ 题目校验：1275/1275 通过
- ✅ 题型覆盖：分数、加减、乘除、小数、百分比、比例、代数入门

### 2) 后端 API（FastAPI）
- ✅ 核心接口：`/next-item`、`/events`、`/mastery/*`、`/students/*`
- ✅ 每日习惯接口：`/daily-session/*`、`/streak/{student_id}`
- ✅ 家长接口：`/parent/daily-summary`、`/parent/weekly-summary`、`/parent/{student_id}/progress`
- ✅ 成就接口：`/achievements/{student_id}`、`/achievements/{student_id}/new`

### 3) iOS 应用（SwiftUI）
- ✅ 学生选择 + 做题主链路
- ✅ 家长日报/周报
- ✅ 新徽章/连击风险提醒（可点击详情）
- ✅ 提醒按“类型”未读状态（按天自动重置）

---

## ✅ Phase 6.5 完成清单（架构固化）
1. ✅ 引擎协议：`services/api/app/engine/protocol.py`
2. ✅ 服务层：`services/api/app/services/`
3. ✅ Achievement 逻辑迁移：`achievement_service.py`
4. ✅ Event 路由瘦身 + EventCreate：`routers/events.py` + `app/schemas.py`
5. ✅ Mastery 更新逻辑下沉：`mastery_service.py`
6. ✅ 事件编排下沉：`event_processor.py`
7. ✅ 引擎插件化：`engine/tracks/jon.py`、`engine/tracks/astrid.py`、registry
8. ✅ 引擎去副作用：不再在引擎层写 DB（持久化在 `item_service.py`）
9. ✅ 清理 `sys.path.append` hack
10. ✅ CORS 收紧为配置化白名单（不再 `allow_origins=["*"]`）
11. ✅ 回归测试通过：`27 passed`

---

## 🔜 下一步（Phase 7）
1. ✅ 已落地：掌握度计算升级（滑动窗口 + 时间衰减）
2. ✅ 已落地：风险信号输出（accuracy/time/consecutive wrong）
3. ✅ 已落地：评估指标输出（完成率、波动度、恢复速度）
4. ✅ 已落地：家长端详情页趋势图 + 日报卡片指标摘要
5. ✅ 已落地：家长主页面图表化趋势（日报卡片 7 天准确率迷你图）
6. ✅ 已落地：周报页多指标联动图表（跨学生周维度对比）
7. ✅ 已落地（Phase 8 Step 1）：`Parent` 模型 + `students.parent_id` + `students.pin_hash`
8. ✅ 已落地（Phase 8 Step 2）：认证路由（register/login/student-login）+ JWT 权限依赖
9. ✅ 已落地（Phase 8 Step 3）：家长接口 `parent_id` 数据隔离（`/parent/*` 需 parent token）
10. ✅ 已落地（Phase 8 Step 4）：iOS APIClient token 存储与 Authorization 注入
11. ✅ 已落地（Phase 8 Step 5）：iOS 登录入口（家长登录/注册 + 学生 PIN 登录）与登出
12. ✅ 已落地（Phase 8 Step 6）：学生相关接口角色隔离收口（parent/student 按 `student_id` 授权）
13. ✅ 已落地（Phase 8 Step 7）：iOS 401 自动清 token + 回跳登录页
14. ✅ 已落地（Phase 8 Step 8）：iOS token Keychain 存储（含旧 token 迁移）
15. ✅ 已落地（Phase 8 Step 8.5）：学生模式核心链路 `student_id` 参数可省略（token 派生）
16. ✅ 已落地（Phase 8 Step 9）：学生查询接口 `me` 风格入口（mastery/streak/achievements）
17. ✅ 已落地（Phase 8 Step 9.5）：`events` 学生模式可省略 `student_id`
18. ✅ 已落地（Phase 8 Step 10）：iOS 学生模式提交事件不再显式传 `student_id`
19. ✅ 已落地（Phase 8 Step 10.5）：`students` 路由补齐 `me` 兼容（含单测覆盖学生/家长行为）
20. ✅ 已落地（Phase 8 Step 11）：`daily-session/status/{student_id}` 补齐 `me` 兼容，iOS 学生态统一走 `me` 查询路径
21. ✅ 已落地（Phase 8 Step 12）：iOS APIClient 学生相关接口改为 `studentId` 可选（student 角色可省略；parent 角色强校验）
22. ✅ 已落地（Phase 8 Step 13）：学生端页面开始切换无参调用（Question/Achievements 优先走隐式学生上下文）
23. ✅ 已落地（Phase 8 Step 14）：`QuestionView` 学生模式下不再向 ViewModel 传递显式 `student_id`
24. ✅ 已落地（Phase 8 Step 15）：新增 HTTP 级认证与权限回归测试（student login、`me` 接口、越权拦截、parent 作用域）
25. ✅ 已落地（Phase 8 Step 16）：生产配置安全门禁（启动校验 + 发布前检查脚本）
26. ✅ 已落地（Phase 8 Step 17）：补齐 `.env.example` 与 `docs/qa/PHASE8_RELEASE_CHECKLIST.md` 发布清单
27. ✅ 已落地（Phase 8 Step 18）：补齐联调演练脚本 `scripts/smoke_phase8_auth.py`
28. ✅ 已落地（Phase 8 Step 19）：本仓库 API 实例完成端到端联调演练（parent+student smoke 全通过）
29. ✅ 已落地（Phase 8 Step 20）：补齐发布审批模板 `docs/qa/PHASE8_RELEASE_APPROVAL.md`
30. ⏭️ 下一步：执行发布审批签核并进入上线窗口

---

## 🚀 验证命令
```bash
cd /Users/michaelzhao/agents/apps/ai-zhao-tutor
.venv/bin/pytest -q services/api/tests
# 41 passed
```
