# AI Zhao Tutor — 工程级交付计划
## Engineering Delivery Plan (EDP)

> **文档定位：** 本文是唯一的执行基准。UPGRADE_PLAN_2026.md 是设计参考，本文是交付执行。
> **更新规则：** 每个任务完成后立即更新状态，不批量更新。
> **版本：** EDP-v1.0 | 2026-02-21

---

## Part 0 — 交付元信息

### 0.1 系统边界

```
┌─────────────────────────────────────────────────────────┐
│  AI Zhao Tutor System                                   │
│                                                         │
│  ┌─────────────────┐    ┌──────────────────────────┐   │
│  │  iOS App        │───▶│  FastAPI Backend          │   │
│  │  SwiftUI/MVVM   │    │  SQLite/PostgreSQL        │   │
│  │  Keychain Auth  │    │  Engine / Services / Auth │   │
│  └─────────────────┘    └──────────────────────────┘   │
│                                    │                    │
│                         ┌──────────▼──────────┐        │
│                         │  Claude API          │        │
│                         │  (Phase 8.5+)        │        │
│                         └─────────────────────┘        │
└─────────────────────────────────────────────────────────┘

服务对象: Jon、Astrid（当前）/ 可扩展多家庭（Phase 8+）
部署环境: Mac Mini（家用本地）+ iOS 设备
```

### 0.2 交付原则

| 原则 | 约束 |
|------|------|
| **最小可验证单元** | WBS 任务粒度 ≤ 4 小时；超过必须拆分 |
| **实际代码优先** | 计划以真实文件路径为准，不写"新增 xxx.py"而写"修改 `app/models/mastery.py` 第 9-14 行" |
| **回滚先行** | 每个数据库变更任务必须先写 DOWN 脚本，再写 UP 脚本 |
| **测试命令可执行** | DoD 中的验证命令必须在当前 venv 中直接运行，不写"运行测试"这种模糊指令 |
| **不依赖记忆** | 任何配置值、密钥、端口必须写在文档中，不能说"你知道的" |

### 0.3 风险等级定义

| 等级 | 颜色 | 定义 | 响应策略 |
|------|------|------|---------|
| CRITICAL | 🔴 | 影响数据安全或导致数据丢失 | 立即停工，修复后才能继续 |
| HIGH | 🟠 | 影响核心链路可用性 | 当日修复，不过夜 |
| MEDIUM | 🟡 | 影响功能完整性，有降级方案 | 记录 + 本 Phase 内修复 |
| LOW | 🟢 | 体验问题，不影响核心流程 | 积压到下一 Phase |

---

## Part 1 — 当前系统基线核查（Reality Check）

> ⚠️ 本节基于 2026-02-21 对真实代码的扫描，非计划文档的描述。差异项以 `[GAP]` 标注。

### 1.1 后端文件清单（已确认存在）

```
services/api/app/
├── auth/
│   ├── dependencies.py   ✅ require_parent / require_student / require_student_access
│   ├── jwt.py            ✅ JWT encode/decode
│   ├── schemas.py        ✅ Pydantic auth schemas
│   └── security.py       ✅ bcrypt hashing
├── engine/
│   ├── adaptive.py       ✅ 选题引擎
│   ├── protocol.py       ✅ SelectionRequest / SelectionResult
│   └── tracks/           ✅ jon.py / astrid.py / base.py
├── models/
│   ├── achievement.py    ✅
│   ├── daily_session.py  ✅
│   ├── event.py          ✅
│   ├── item.py           ✅
│   ├── mastery.py        ✅ (但无 Phase 7 新字段，见下方 GAP)
│   ├── parent.py         ✅
│   └── student.py        ✅ parent_id 外键已加
├── routers/
│   ├── auth.py           ✅
│   ├── events.py         ✅
│   ├── items.py          ✅
│   ├── mastery.py        ✅
│   ├── parent.py         ✅
│   ├── students.py       ✅
│   ├── daily_sessions.py ✅
│   ├── achievements.py   ✅
│   └── placement.py      ✅
├── services/
│   ├── achievement_service.py  ✅
│   ├── event_processor.py      ✅
│   ├── item_service.py         ✅
│   └── mastery_service.py      ✅
├── database.py           ✅ create_all（无 Alembic）
└── config.py             ✅ production_validation_errors()
```

### 1.2 [GAP] 计划声明 vs 代码实际

| Phase | 计划声明状态 | 代码实际状态 | 差异 |
|-------|------------|------------|------|
| Phase 7 | ✅ 已完成 | `models/mastery.py` 无 `last_n_results`、`score_trend`、`next_review_at` 字段 | **[GAP-01] 🟠 HIGH** |
| Phase 7 | ✅ 已完成 | `engine/protocol.py` 无 `zpd_zone`、`flow_signal` 字段 | **[GAP-02] 🟡 MEDIUM** |
| Phase 8 | 🟡 收口中（2026-02-21） | `auth/` 模块已实现；DoD 自动化回归 `41 passed, 0 failed` | 待 W8D-12 手工验收与环境 smoke 复核 |
| Phase 8 | 🟡 收口中 | 无 Alembic，数据库用 `create_all()`；已补 `M-000` 版本表与执行器 | **[GAP-03] 🟠 HIGH**（阶段性缓解） |
| 测试 | ✅ 可执行 | `services/api/.venv` 已建立，`pytest --collect-only` 与全量回归可执行 | GAP-04 已关闭 |

### 1.3 iOS 文件清单（已确认存在）

```
apps/ios/MathCoach/MathCoach/
├── Services/
│   ├── APIClient.swift     ✅
│   └── KeychainStore.swift ✅
├── Views/
│   ├── AuthView.swift      ✅
│   ├── QuestionView.swift  ✅
│   ├── ParentDashboardView.swift ✅
│   ├── AchievementsView.swift    ✅
│   └── StudentPickerView.swift   ✅
├── Models/
│   └── Auth.swift          ✅
└── ViewModels/
    └── QuestionViewModel.swift ✅
```

### 1.4 数据库现状

- **引擎：** SQLAlchemy `create_all()` — 只增不减，无法回滚列变更
- **文件：** SQLite（本地 `./data/mathcoach.db`）
- **迁移工具：** ❌ 无 Alembic，无版本控制
- **行动要求：** 在 Phase 8.5 首个 DB 变更前，必须先完成 Part 3（迁移管理体系）

---

## Part 2 — 架构决策记录（ADR）

> ADR 一旦确认不得随意推翻；如需变更，新建 ADR 标注"取代 ADR-XXX"。

### ADR-001：认证方案（JWT + bcrypt）

- **状态：** ✅ 已实施
- **决策：** 家长用 email/password（bcrypt cost=12）登录，学生用 4 位 PIN；JWT 有效期 7 天
- **理由：** 家用系统复杂度适中，无需 OAuth；PIN 对儿童友好
- **约束：** PIN 不得明文存储；JWT 密钥必须来自环境变量 `SECRET_KEY`
- **放弃的方案：** OAuth2（过重）、Session Cookie（iOS 端复杂）

### ADR-002：数据库引擎（SQLite → PostgreSQL）

- **状态：** ✅ 已决策，🔵 迁移待执行
- **决策：** 开发/本地用 SQLite；生产目标是 PostgreSQL（Docker Compose 已配置）
- **理由：** SQLite 零依赖适合单机，PostgreSQL 支持并发家庭用户
- **约束：** 代码层用 SQLAlchemy ORM，不写原生 SQL，保证双库兼容
- **触发迁移的条件：** Phase 9 多家庭用户 > 1 家庭同时在线时

### ADR-003：迁移策略（手动 SQL 脚本替代 Alembic）

- **状态：** ⬜ 待确认
- **决策候选 A：** 引入 Alembic（自动生成迁移脚本，版本链完整）
- **决策候选 B：** 手动 SQL 脚本（`ops/migrations/V{N}__description.sql` + `V{N}__rollback.sql`）
- **当前推荐：** **候选 B**（项目规模小，手动脚本可控，无需引入新依赖复杂性）
- **约束：** 每个 UP 脚本必须有对应 DOWN 脚本；脚本幂等（可重复执行不报错）
- **决策截止：** Phase 8.5 第一个 DB 变更前必须确认

### ADR-004：Claude API 集成方式

- **状态：** ⬜ 待决策（Phase 8.5）
- **决策候选 A：** 同步调用（家长提交上下文后等待 AI 响应）— 简单，但 P99 > 3s
- **决策候选 B：** 异步 + 轮询（提交后立即返回 202，前端轮询结果）— 复杂，体验好
- **当前推荐：** **候选 A**，配合前端 loading 动画；Phase 9 如有性能问题升级为 B
- **约束：** `ANTHROPIC_API_KEY` 必须来自环境变量；调用失败返回 503，不崩溃

### ADR-005：engine_hint 影响引擎的方式

- **状态：** ⬜ 待决策（Phase 8.5）
- **决策：** `engine_hint` 作为**软约束**（soft constraint）影响选题难度分布，不强制覆盖引擎逻辑
- **实现：** `SelectionRequest` 新增可选字段 `engine_hint: str | None`，引擎读取后调整 difficulty 分布权重
- **理由：** 避免家长主观输入完全覆盖客观数据导致引擎混乱

---

## Part 3 — 数据库变更管理

> **重要：** 当前系统无迁移版本控制（[GAP-03]）。本 Part 建立管理规范，在任何 Phase 8.5+ DB 变更前必须先执行 M-000。

### 3.1 迁移脚本规范

```
ops/migrations/
├── M-000__init_migration_table.sql       ← 必须首先执行
├── M-000__init_migration_table.down.sql
├── M-001__mastery_phase7_fields.sql      ← Phase 7 GAP 修复
├── M-001__mastery_phase7_fields.down.sql
├── M-002__parent_context_events.sql      ← Phase 8.5
├── M-002__parent_context_events.down.sql
└── ...

命名规则：M-{三位序号}__{snake_case_description}.sql
```

### 3.2 迁移版本跟踪表（M-000 内容）

```sql
-- M-000__init_migration_table.sql (UP)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     TEXT PRIMARY KEY,
    applied_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- M-000__init_migration_table.down.sql (DOWN)
DROP TABLE IF EXISTS schema_migrations;
```

### 3.3 M-001：Phase 7 掌握度字段（修复 GAP-01）

```sql
-- M-001__mastery_phase7_fields.sql (UP)
ALTER TABLE mastery ADD COLUMN last_n_results   TEXT    DEFAULT '[]';
ALTER TABLE mastery ADD COLUMN score_trend       TEXT    DEFAULT 'stable';
ALTER TABLE mastery ADD COLUMN next_review_at    TIMESTAMP;
ALTER TABLE mastery ADD COLUMN review_interval_days INTEGER DEFAULT 1;
ALTER TABLE mastery ADD COLUMN review_streak     INTEGER DEFAULT 0;

INSERT INTO schema_migrations (version, description)
VALUES ('M-001', 'mastery phase7 sliding window fields');

-- M-001__mastery_phase7_fields.down.sql (DOWN)
-- SQLite 不支持 DROP COLUMN（< 3.35），需重建表
-- 生产前必须确认 SQLite 版本 >= 3.35，否则回滚需手动数据迁移
ALTER TABLE mastery DROP COLUMN last_n_results;
ALTER TABLE mastery DROP COLUMN score_trend;
ALTER TABLE mastery DROP COLUMN next_review_at;
ALTER TABLE mastery DROP COLUMN review_interval_days;
ALTER TABLE mastery DROP COLUMN review_streak;
DELETE FROM schema_migrations WHERE version = 'M-001';
```

> ⚠️ **SQLite 版本约束：** `DROP COLUMN` 需要 SQLite ≥ 3.35（2021-03-12 发布）。
> 执行前运行：`sqlite3 --version` 确认版本，若 < 3.35，DOWN 脚本需改为重建表方式。

### 3.4 M-002：家长上下文事件表（Phase 8.5）

```sql
-- M-002__parent_context_events.sql (UP)
CREATE TABLE IF NOT EXISTS parent_context_events (
    id              TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    parent_id       TEXT NOT NULL REFERENCES parents(id),
    student_id      TEXT NOT NULL REFERENCES students(id),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tags            TEXT NOT NULL DEFAULT '[]',   -- JSON array
    free_text       TEXT,
    engine_hint     TEXT,
    ai_insight      TEXT
);

CREATE INDEX IF NOT EXISTS idx_pce_student_date
    ON parent_context_events (student_id, created_at DESC);

INSERT INTO schema_migrations (version, description)
VALUES ('M-002', 'parent context events table');

-- M-002__parent_context_events.down.sql (DOWN)
DROP INDEX IF EXISTS idx_pce_student_date;
DROP TABLE IF EXISTS parent_context_events;
DELETE FROM schema_migrations WHERE version = 'M-002';
```

### 3.5 迁移执行程序

```bash
# 执行迁移（每次发布前运行）
python ops/migrations/run_migration.py up M-001
python ops/migrations/run_migration.py up M-002

# 回滚（出问题时）
python ops/migrations/run_migration.py down M-002
python ops/migrations/run_migration.py down M-001

# 查看当前版本
python ops/migrations/run_migration.py status
```

> `ops/migrations/run_migration.py` 脚本待创建（WBS 任务 W8C-01）。

### 3.6 发布前数据库备份流程

```bash
# 必须在每次迁移前执行
BACKUP_FILE="data/backup_$(date +%Y%m%d_%H%M%S).db"
cp data/mathcoach.db "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"
```

**保留策略：** 保留最近 7 份备份，7 天以上自动清理。

---

## Part 4 — 工作分解结构（WBS）

> **任务规格：**
> - 粒度：XS(<1h) / S(1-2h) / M(2-4h) / L(4-8h)
> - DoD：可直接执行的命令或可二元判定的检查
> - 前置条件（Dep）：必须先完成的任务 ID

---

### Phase 8 收口 WBS（当前阶段）

> **目标：** 将进行中的 Phase 8 正式关闭，满足 14.3 节 DoD 14 项全通过。

#### 基础设施修复（必须先完成）

| 任务 ID | 描述 | 文件 | 规模 | DoD | Dep |
|---------|------|------|------|-----|-----|
| **W8C-00** | 确认并修复 pytest venv | `services/api/` | S | `cd services/api && pip install -r requirements.txt && pytest --collect-only -q` 无报错 | — |
| **W8C-01** | 创建迁移脚本执行工具 | `ops/migrations/run_migration.py` | M | `python ops/migrations/run_migration.py status` 输出当前版本表 | W8C-00 |
| **W8C-02** | 执行 M-000（初始化版本表） | DB | XS | `sqlite3 services/api/mathcoach.db "SELECT * FROM schema_migrations"` 返回版本记录（表存在） | W8C-01 |

#### Phase 8 DoD 验证（对照 14.3 节）

| 任务 ID | 验收项 | 验证命令 | 规模 | Dep |
|---------|--------|---------|------|-----|
| **W8D-01** | 家长-学生关系字段可用 | `pytest tests/test_phase8_models.py::test_parent_student_relationship_fields -v` | XS | W8C-00 |
| **W8D-02** | 正确密码登录 200，错误密码 401 | `pytest tests/test_auth_utils.py -v` | XS | W8C-00 |
| **W8D-03** | JWT payload 含 role 字段 | `pytest tests/test_auth_utils.py::test_token_roundtrip_parent_claims -v` | XS | W8C-00 |
| **W8D-04** | 家长数据隔离（不泄露他人学生） | `pytest tests/test_phase8_api_authz.py::test_parent_scope_requires_student_id_and_blocks_other_family -v` | S | W8C-00 |
| **W8D-05** | student role 访问越权范围被拒绝 | `pytest tests/test_phase8_api_authz.py::test_student_cannot_access_other_student_scope -v` | XS | W8C-00 |
| **W8D-06** | parent role 缺少/越权 student scope 被拒绝 | `pytest tests/test_phase8_api_authz.py::test_parent_scope_requires_student_id_and_blocks_other_family -v` | XS | W8C-00 |
| **W8D-07** | 学生 PIN 登录 | `pytest tests/test_phase8_api_authz.py::test_student_login_and_me_endpoints -v` | XS | W8C-00 |
| **W8D-08** | student_id 只从 token 取 | 代码审查：`grep -r "student_id" app/routers/ --include="*.py"` 确认无从 query/body 取 student_id 的逻辑 | S | — |
| **W8D-09** | JWT 密钥来自环境变量 | `grep -rn "SECRET_KEY\|secret_key" app/ --include="*.py"` 只有 config.py 引用，无硬编码字符串 | XS | — |
| **W8D-10** | 密码/PIN 使用强哈希（PBKDF2） | `pytest tests/test_auth_utils.py::test_hash_and_verify_secret -v` | S | W8C-00 |
| **W8D-11** | iOS Keychain 无 UserDefaults | `grep -r "UserDefaults" apps/ios/` 无 token 相关写入 | XS | — |
| **W8D-12** | 401 触发 iOS 登录页跳转 | 手动：使 token 过期 → 点击"下一题"→ 确认跳转至 AuthView | M | — |
| **W8D-13** | 历史数据兼容（学生关系字段可读） | `pytest tests/test_phase8_models.py::test_parent_student_relationship_fields -v` | S | W8C-00 |
| **W8D-14** | 全量回归零失败 | `pytest services/api/tests/ -v --tb=short 2>&1 \| tail -5` 最后一行含"passed, 0 failed" | M | W8D-01..13 |

#### 安全专项（Phase 8 必须）

| 任务 ID | 检查项 | 命令 | 规模 |
|---------|--------|------|------|
| **W8S-01** | 无明文密码落库 | `docker exec mathcoach-postgres psql -U mathcoach -d mathcoach -c "SELECT substr(password_hash,1,13) FROM parents LIMIT 3"` 全为 `pbkdf2_sha256` | XS |
| **W8S-02** | 无明文 PIN 落库 | `docker exec mathcoach-postgres psql -U mathcoach -d mathcoach -c "SELECT substr(pin_hash,1,13) FROM students WHERE pin_hash IS NOT NULL LIMIT 3"` 全为 `pbkdf2_sha256` | XS |
| **W8S-03** | JWT 密钥无硬编码 | `git grep -i "hs256\|my.secret\|changeme" -- "*.py" "*.env*"` 返回 0 结果 | XS |
| **W8S-04** | 跨家长数据泄露测试 | `cd services/api && PHASE8_PARENT_EMAIL=... PHASE8_PARENT_PASSWORD=... PHASE8_STUDENT_ID=... PHASE8_STUDENT_PIN=... PYTHONPATH=. .venv/bin/python scripts/smoke_phase8_auth.py` | S |
| **W8S-05** | 生产配置门禁 | `cd services/api && PYTHONPATH=. .venv/bin/python scripts/check_phase8_readiness.py` 返回 exit 0 | XS |

#### Phase 8 关闭动作

| 任务 ID | 描述 | 规模 |
|---------|------|------|
| **W8X-01** | 更新 `UPGRADE_PLAN_2026.md` 进展快照：Phase 8 → ✅ | XS |
| **W8X-02** | 更新本文 Part 1 基线核查状态 | XS |
| **W8X-03** | 创建 DB 备份并标记为 Phase 8 基线快照 | XS |

---

### Phase 7 GAP 修复 WBS（并行进行，不阻塞 Phase 8 关闭）

> 修复 GAP-01（mastery 字段缺失）和 GAP-02（protocol 字段缺失）

| 任务 ID | 描述 | 文件 | 规模 | DoD |
|---------|------|------|------|-----|
| **W7G-01** | 执行 M-001 迁移，mastery 表新增 5 字段 | `ops/migrations/M-001__mastery_phase7_fields.sql` | S | `sqlite3 data/mathcoach.db ".schema mastery"` 显示新字段 |
| **W7G-02** | 更新 `models/mastery.py` ORM 映射新字段 | `app/models/mastery.py` | S | `pytest tests/test_mastery_service.py -v` 全通过 |
| **W7G-03** | `mastery_service.py` 实现滑动窗口更新逻辑 | `app/services/mastery_service.py` | M | `pytest tests/test_mastery_service.py::test_sliding_window -v` 通过 |
| **W7G-04** | `engine/protocol.py` 新增 `zpd_zone` 和 `flow_signal` 字段 | `app/engine/protocol.py` | S | `grep "zpd_zone\|flow_signal" app/engine/protocol.py` 有输出 |
| **W7G-05** | `engine/adaptive.py` 读取 zpd_zone 调整难度 | `app/engine/adaptive.py` | M | `pytest tests/test_adaptive_engine.py::test_zpd_frustration_zone -v` 通过 |
| **W7G-06** | 全量回归 | — | S | `pytest services/api/tests/ -v --tb=short` 零失败 |

---

### Phase 8.5 WBS（下一阶段）

**前置条件：** Phase 8 完全关闭（W8X-01 ～ W8X-03 完成）

#### 数据层

| 任务 ID | 描述 | 文件 | 规模 | DoD | Dep |
|---------|------|------|------|-----|-----|
| **W85-01** | 备份数据库（Phase 8.5 前基线） | `data/` | XS | 备份文件存在且可打开 | W8X-03 |
| **W85-02** | 执行 M-002 迁移（parent_context_events 表） | `ops/migrations/M-002__parent_context_events.sql` | S | `sqlite3 data/mathcoach.db ".schema parent_context_events"` 显示完整结构 | W85-01 |
| **W85-03** | 新增 ORM 模型 `models/parent_context_event.py` | `app/models/parent_context_event.py` | S | Python import 无报错；`ParentContextEvent.__tablename__ == "parent_context_events"` | W85-02 |

#### 服务层

| 任务 ID | 描述 | 文件 | 规模 | DoD | Dep |
|---------|------|------|------|-----|-----|
| **W85-04** | `services/context_ai_service.py`：调用 Claude API，返回 `engine_hint` + `ai_insight` | `app/services/context_ai_service.py` | M | `pytest tests/test_context_ai_service.py -v`（mock Claude，不实际调用 API） | — |
| **W85-05** | 处理 `ANTHROPIC_API_KEY` 缺失场景：返回 503 不崩溃 | `app/services/context_ai_service.py` | S | `pytest tests/test_context_ai_service.py::test_missing_key_returns_503 -v` | W85-04 |
| **W85-06** | `engine/protocol.py` 新增 `engine_hint: str \| None = None` | `app/engine/protocol.py` | XS | `grep "engine_hint" app/engine/protocol.py` 有输出 | — |
| **W85-07** | `engine/adaptive.py` 读取 engine_hint 调整难度权重 | `app/engine/adaptive.py` | M | `pytest tests/test_adaptive_engine.py::test_engine_hint_reduces_difficulty -v` | W85-06 |
| **W85-08** | engine_hint=None 时引擎行为不变 | — | S | `pytest tests/test_adaptive_engine.py::test_engine_hint_none_no_effect -v` | W85-07 |

#### 路由层

| 任务 ID | 描述 | 文件 | 规模 | DoD | Dep |
|---------|------|------|------|-----|-----|
| **W85-09** | `POST /api/v1/parent/context` 接口 | `app/routers/parent.py` | M | `curl -X POST /api/v1/parent/context -H "Authorization: Bearer {parent_token}" -d '{"tags":["tired"],"free_text":"孩子今天状态差"}' → 201` | W85-03, W85-04 |
| **W85-10** | `GET /api/v1/parent/daily-summary` 响应附加 `ai_insight` 字段 | `app/routers/parent.py` | S | `pytest tests/test_parent_summary.py::test_daily_summary_has_ai_insight -v` | W85-09 |
| **W85-11** | `config.py` 新增 `anthropic_api_key` 配置项 | `app/config.py` | XS | `grep "anthropic_api_key" app/config.py` 有输出；`python -c "from app.config import settings; print(settings.anthropic_api_key)"` 无 ImportError | — |

#### iOS 层

| 任务 ID | 描述 | 文件 | 规模 | DoD | Dep |
|---------|------|------|------|-----|-----|
| **W85-12** | 家长端"今日情况"输入卡片（tags 多选 + 自由文本） | `Views/ParentDashboardView.swift` | M | 手动：输入 tags + 文字 → 点击提交 → 200 响应 → 无崩溃 | W85-09 |
| **W85-13** | "AI 洞察"展示卡片（显示 ai_insight 字段） | `Views/ParentDashboardView.swift` | S | 手动：提交后刷新 → ai_insight 文本出现在卡片中 | W85-12 |
| **W85-14** | `Models/ParentDailySummary.swift` 新增 `aiInsight: String?` 字段 | `Models/ParentDailySummary.swift` | XS | Swift 编译无错 | — |

#### 收口

| 任务 ID | 描述 | 规模 | DoD |
|---------|------|------|-----|
| **W85-15** | 全量回归 | M | `pytest services/api/tests/ -v --tb=short` 零失败 |
| **W85-16** | Phase 8.5 DoD 10 项逐一核对（对照 14.4 节） | M | 14.4 节清单全 ✅ |

---

### Phase 9 WBS（预定义，实施前重新评审）

| 任务 ID | 描述 | 规模 |
|---------|------|------|
| **W9-01** | Skill 依赖图数据结构设计 + `skill_tree.py` 新增 `prerequisites` | M |
| **W9-02** | 引擎：前置技能未达标则不推进阶题 | M |
| **W9-03** | `GET /parent/forecast` 接口（未来 7 日推荐技能） | L |
| **W9-04** | 连续 3 日回避技能检测 + 家长预警标记 | M |
| **W9-05** | 多学生家庭视图（家长看到两孩子独立进度，不交叉） | L |
| **W9-06** | 全量回归 + Phase 9 DoD 核对 | M |

---

## Part 5 — 回滚策略

### 5.1 代码回滚

```bash
# 回滚到上一个稳定提交（Phase 关闭点打 tag）
git tag phase8-closed        # Phase 关闭时打 tag
git checkout phase8-closed   # 需要回滚时

# 推荐 branch 策略
main          ← 仅在 Phase 关闭签字后合入，始终可用
phase/8.5     ← Phase 8.5 开发分支
phase/9       ← Phase 9 开发分支（从 main 拉出）
```

**规则：**
- `main` 分支代表最后一个完整通过 QA Gate 的版本
- 每次 Phase 关闭时在 `main` 上打 tag（格式：`phase{N}-closed-{YYYYMMDD}`）
- 任何时候回到 `main` + 最近 tag 的状态，系统必须是可用的

### 5.2 数据库回滚

```
回滚决策树：

出现问题
    │
    ├─ 是 Schema 变更引起？
    │       │
    │       ├─ 是 → 执行 DOWN 脚本
    │       │        python ops/migrations/run_migration.py down M-XXX
    │       │        然后恢复数据库备份
    │       │
    │       └─ 否 → 继续下一步
    │
    ├─ 是数据内容损坏？
    │       │
    │       └─ 是 → 从备份恢复
    │                cp data/backup_YYYYMMDD_HHMMSS.db data/mathcoach.db
    │                重启服务：docker-compose restart api
    │
    └─ 是代码逻辑 bug？
            │
            └─ 是 → git checkout phase{N-1}-closed
                     docker-compose up -d api
```

### 5.3 功能开关（Feature Flags）

> 当前系统无功能开关机制。以下为 Phase 8.5+ 的推荐方案：

```python
# app/config.py 新增
class Settings(BaseSettings):
    # Feature flags (default OFF in production until validated)
    feature_ai_context: bool = False       # Phase 8.5 AI 融合
    feature_spaced_repetition: bool = False # Phase 7.5 间隔复习
    feature_zpd_detector: bool = False      # Phase 7 ZPD 检测
```

**用法：**
```python
# 在路由/服务中
if not settings.feature_ai_context:
    return {"ai_insight": None}  # 降级返回，不报错
```

**好处：** 可以在不回滚代码的情况下关闭有问题的新功能。

### 5.4 iOS 回滚

- iOS 不能远程回滚，必须重新构建并安装
- 保留最近 2 个 `.ipa` 构建归档（Xcode Archives）
- 发布前 Xcode → Product → Archive → 保存到 `ops/ios-archives/`

---

## Part 6 — 测试策略

### 6.1 测试金字塔

```
              ╔══════════════╗
              ║  E2E（iOS）  ║  ← 手动，每次发布前，~5 个场景
              ╚══════════════╝
           ╔═════════════════════╗
           ║  集成测试（API）      ║  ← pytest，自动，~30 用例
           ╚═════════════════════╝
        ╔══════════════════════════════╗
        ║  单元测试（services/engine）  ║  ← pytest，自动，~50 用例
        ╚══════════════════════════════╝
```

### 6.2 测试文件 → 覆盖范围映射

| 测试文件 | 覆盖范围 | Phase |
|---------|---------|-------|
| `test_adaptive_engine.py` | 选题引擎、ZPD、心流信号 | 6.5, 7 |
| `test_mastery_service.py` | 掌握度计算、滑动窗口、时间衰减 | 7 |
| `test_auth_utils.py` | bcrypt、JWT encode/decode | 8 |
| `test_auth_dependencies.py` | require_parent/student 依赖 | 8 |
| `test_phase8_api_authz.py` | HTTP 级权限隔离 | 8 |
| `test_phase8_models.py` | Parent/Student ORM、注册、PIN | 8 |
| `test_events_logic.py` | 答题事件处理链路 | 6.5 |
| `test_parent_summary.py` | 家长日报聚合 | 5, 8.5 |
| `test_daily_sessions_router.py` | 每日会话 me 接口 | 8 |
| `test_students_router.py` | 学生信息、streak | 8 |
| `test_runtime_config.py` | 生产配置门禁 | 8 |
| `test_achievements_router.py` | 成就接口 | 6 |
| `test_context_ai_service.py` | AI 融合服务（Phase 8.5，待创建） | 8.5 |

### 6.3 测试执行规范

```bash
# 快速验证（开发中，频繁执行）
pytest services/api/tests/test_adaptive_engine.py -v

# Phase 关闭前全量回归（必须执行）
pytest services/api/tests/ -v --tb=short --durations=10

# 安全专项（Phase 8 后必须）
python services/api/scripts/check_phase8_readiness.py
python services/api/scripts/smoke_phase8_auth.py

# 覆盖率（每季度一次，了解盲区）
pytest services/api/tests/ --cov=app --cov-report=term-missing
```

### 6.4 测试数据管理

```python
# tests/conftest.py 规范
# - 每个测试使用独立的内存 SQLite DB（不污染真实数据）
# - 测试中的 Parent/Student 使用固定 fixture ID（不依赖真实 Jon/Astrid 数据）
# - Claude API 调用全部 mock（不产生真实 API 费用）

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield Session(engine)
    Base.metadata.drop_all(engine)
```

---

## Part 7 — 监控与可观测性

### 7.1 关键业务指标（需每日观察）

| 指标 | 来源 | 告警阈值 | 查询命令 |
|------|------|---------|---------|
| 日答题量（Jon） | `events` 表 | < 5 题/天持续 3 天 | `sqlite3 data/mathcoach.db "SELECT COUNT(*) FROM events WHERE student_id='jon_zhao' AND DATE(created_at)=DATE('now')"` |
| 日答题量（Astrid） | `events` 表 | < 5 题/天持续 3 天 | 同上，替换 student_id |
| 连续打卡天数 | `students` 表 | streak 归零 | `sqlite3 data/mathcoach.db "SELECT id,streak FROM students"` |
| 最近 5 题正确率 | `events` 表 | < 40%（挫败区）| `python ops/scripts/health_check.py` |
| 掌握度高风险技能 | `mastery` 表 | risk_level = 'high' | `sqlite3 data/mathcoach.db "SELECT student_id,skill_id FROM mastery WHERE score_trend='declining'"` |

### 7.2 系统健康指标

| 指标 | 告警阈值 | 检测方式 |
|------|---------|---------|
| API 响应时间 P99 | > 500ms（选题接口） | 本地 `time curl ...` |
| DB 文件大小 | > 100MB | `ls -lh data/mathcoach.db` |
| 错误日志 | 任何 ERROR 级别 | `grep ERROR logs/api.log | tail -20` |
| iOS 崩溃 | 任何 crash | Xcode Organizer 崩溃日志 |

### 7.3 日志规范

```python
# 统一日志格式（所有服务层使用）
import logging
logger = logging.getLogger(__name__)

# 规范：
logger.info("event.processed student_id=%s skill_id=%s correct=%s", ...)
logger.warning("mastery.risk_detected student_id=%s skill_id=%s level=high", ...)
logger.error("engine.selection_failed student_id=%s error=%s", ...)

# 禁止：
print("debug info")           # 禁止 print
logger.debug("raw sql: ...")  # 禁止在 info 级别输出 SQL
```

---

## Part 8 — 发布管理

### 8.1 发布流程（后端 + iOS 联合发布）

```
Step 1: 代码冻结
  - 创建 release/phase{N} 分支
  - 不再合入新功能

Step 2: QA Gate 执行（见 14.7 节）
  - [ ] 单元测试全通过
  - [ ] 全量回归零失败
  - [ ] 行为验收场景通过
  - [ ] 安全专项通过

Step 3: 数据库准备
  - [ ] 备份当前 DB（cp data/mathcoach.db data/backup_YYYYMMDD.db）
  - [ ] 执行新 migration UP 脚本
  - [ ] 验证 schema 正确

Step 4: 后端部署
  - [ ] docker-compose down
  - [ ] docker-compose up -d --build
  - [ ] 等待 30 秒，curl http://localhost:8000/health 返回 200

Step 5: iOS 构建发布
  - [ ] Xcode → Product → Archive
  - [ ] 通过 Xcode Organizer 安装到目标设备
  - [ ] 冷启动测试（从未运行状态启动）

Step 6: 发布后验证（T+5 分钟）
  - [ ] Jon 完成 1 次完整答题会话
  - [ ] Astrid 完成 1 次完整答题会话
  - [ ] 家长端加载日报成功
  - [ ] 无 ERROR 日志输出

Step 7: 关闭签字
  - [ ] 更新进展快照状态为 ✅
  - [ ] git tag phase{N}-closed-{YYYYMMDD}
  - [ ] git push（或本地保存）
```

### 8.2 发布回滚触发条件

以下任何情况立即触发回滚，不等待：
- iOS 冷启动崩溃
- 选题接口返回 5xx
- 家长数据泄露（错误返回他人学生数据）
- 数据库写入失败
- JWT 认证完全失效（所有请求 401）

### 8.3 环境策略

| 环境 | 配置 | 用途 |
|------|------|------|
| **local-dev** | SQLite + `ENV=development` + `CORS=*` | 日常开发 |
| **local-prod** | SQLite + `ENV=production` + 严格 CORS | 发布到家用设备前的最终验证 |
| **prod** | PostgreSQL（目标）+ `ENV=production` | Phase 9 多家庭用户后迁移 |

---

## Part 9 — 风险寄存器

| ID | 风险描述 | 等级 | 概率 | 影响 | 缓解措施 | 状态 |
|----|---------|------|------|------|---------|------|
| R-01 | 无迁移版本控制，DB schema 变更无法回滚 | 🟠 HIGH | 高 | 高 | Part 3 建立迁移体系（M-000 先行） | 🔴 待处理 |
| R-02 | Phase 7 字段未落地但标记已完成 | 🟠 HIGH | 已发生 | 中 | W7G-01~06 修复 GAP | 🔴 待处理 |
| R-03 | pytest venv 未安装，测试无法执行 | 🟡 MEDIUM | 已发生 | 高 | W8C-00 修复 | 🔴 待处理 |
| R-04 | Claude API key 泄露 | 🔴 CRITICAL | 低 | 极高 | 只存 `.env`（gitignore），config.py 从环境变量读 | 🟢 已缓解 |
| R-05 | SQLite 并发写入冲突（多设备同时答题） | 🟡 MEDIUM | 中 | 中 | 当前家用单用户，Phase 9 前迁移 PostgreSQL | 🟡 监控中 |
| R-06 | iOS token 过期后无限 401 循环 | 🟠 HIGH | 中 | 高 | 401 拦截器强制跳 AuthView，不重试 | 🟢 已实施 |
| R-07 | 学生 PIN 暴力破解（4 位数 = 10000 种） | 🟠 HIGH | 低 | 高 | 失败 5 次锁定 30 分钟（Phase 8 未实施） | 🟡 待评估 |
| R-08 | Claude API 超时/不可用时阻塞答题链路 | 🟡 MEDIUM | 中 | 高 | W85-05：返回 503，答题链路不依赖 AI | 🔵 Phase 8.5 处理 |
| R-09 | 教育科学模块引入过多 DB 查询拖慢选题 | 🟡 MEDIUM | 中 | 中 | 14.9 节性能基准：选题 P99 < 300ms；超过则 lazy-load | 🔵 Phase 7 验证 |
| R-10 | 历史设计文档（Phase 0-6）与实际代码不一致 | 🟢 LOW | 已发生 | 低 | 以本文 Part 1 基线核查为准，UPGRADE_PLAN_2026.md 标注"历史草案" | 🟢 已处理 |

---

## Part 10 — 当前执行状态

### 立即行动项（本周，有序执行）

```
优先级 1 — 基础设施（不完成则无法验证任何东西）
  [x] W8C-00: 安装 pytest venv
  [x] W8C-01: 创建迁移执行工具
  [x] W8C-02: 执行 M-000

优先级 2 — Phase 7 GAP 修复（并行）
  [ ] W7G-01: 执行 M-001 迁移
  [ ] W7G-02: 更新 ORM 模型
  [ ] W7G-03: 实现滑动窗口逻辑

优先级 3 — Phase 8 DoD 验证
  [ ] W8D-01 ~ W8D-14: 逐项执行并记录结果（仅 W8D-12 手工验证待完成）
  [x] W8S-01 ~ W8S-05: 安全专项

优先级 4 — Phase 8 关闭
  [x] W8X-01 ~ W8X-03: 关闭动作
```

### 任务状态看板

| Phase | 任务数 | 待执行 | 进行中 | 已完成 |
|-------|-------|--------|--------|--------|
| Phase 8 基础 | 3 | 0 | 0 | 3 |
| Phase 8 DoD | 14 | 0 | 1 | 13 |
| Phase 8 安全 | 5 | 0 | 0 | 5 |
| Phase 7 GAP | 6 | 6 | 0 | 0 |
| Phase 8.5 | 16 | 16 | 0 | 0 |

> **下一个检查点：** W8D-12（iOS 手工验证）完成后，执行 Phase 8 最终签字关闭。
