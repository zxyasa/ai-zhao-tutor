# 今日工作计划

**日期：** 2026-02-21
**当前阶段：** Phase 8 — 认证与发布收尾（进行中）

---

## 背景

Phase 0-6 功能验证已完成。当前最大风险不是功能缺失，而是三层架构边界未固化：
- 引擎层有副作用（写 DB）
- 路由层有业务决策（mastery + streak + achievement 全混在 events.py）
- 行为层与引擎层未解耦

今日目标：完成 Phase 8 收尾（权限回归、生产门禁、发布清单与联调演练）。

---

## ✅ 今日任务（Phase 6.5 已完成记录）

### 任务 1：创建 `engine/protocol.py`（30 分钟）

**文件：** `services/api/app/engine/protocol.py`

定义引擎标准输入/输出数据类：

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SelectionRequest:
    student_id: str
    skill_id: Optional[str] = None
    year_level: Optional[int] = None

@dataclass
class SelectionResult:
    item_id: str
    skill_id: str
    question_text: str
    question_type: str
    difficulty: int
    correct_answer: str
    hint: str
    explanation: str
    parameters: dict = field(default_factory=dict)
    validation_rule: str = "numeric"
    # 引擎元数据（内部用，不透传客户端）
    selection_reason: str = "unknown"
    difficulty_delta: int = 0
```

验收：文件创建完毕，import 无报错。

---

### 任务 2：创建 `services/` 目录结构（15 分钟）

```bash
mkdir -p services/api/app/services
touch services/api/app/services/__init__.py
touch services/api/app/services/achievement_service.py
touch services/api/app/services/mastery_service.py
touch services/api/app/services/event_processor.py
```

---

### 任务 3：迁移 Achievement 逻辑（45 分钟）

**从：** `services/api/app/routers/events.py`（第 156-192 行）
**到：** `services/api/app/services/achievement_service.py`

迁移内容：
- `BADGE_DEFS` 字典
- `_unlock_achievements()` 函数
- `_maybe_grant_badge()` 函数

`events.py` 路由改为 import 调用：
```python
from ..services.achievement_service import unlock_achievements
```

验收：`POST /events` 接口行为不变，Badge 逻辑仍正常触发。

---

### 任务 4：创建 `engine/tracks/` 目录（30 分钟）

```bash
mkdir -p services/api/app/engine/tracks
touch services/api/app/engine/tracks/__init__.py
touch services/api/app/engine/tracks/base.py
```

**`tracks/base.py` 内容：**

```python
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class TrackPlugin(ABC):
    @property
    @abstractmethod
    def student_id(self) -> str: ...

    @abstractmethod
    def build_item(self, db: Session) -> dict: ...
```

只创建基类和目录结构，Jon/Astrid 逻辑迁移留在 Step 3。

---

### 任务 5：执行现有测试（15 分钟）

```bash
cd services/api
pip install -r requirements.txt
pytest tests/ -v
```

记录当前测试通过状态（基线），确保 Step 1 改动后测试仍通过。

---

## 📋 今日完成标准

- [x] `engine/protocol.py` 创建完毕，import 无报错
- [x] `services/` 目录结构已创建
- [x] `achievement_service.py` 包含 BADGE_DEFS + 两个函数
- [x] `events.py` 路由 achievement 部分改为 import 调用
- [x] `engine/tracks/base.py` 创建完毕
- [x] pytest 基线已记录（当前全量 `27 passed`）

---

## ⏭️ 后续计划（更新）

**Step 2（已完成）：**
- ✅ `services/event_processor.py` — 已剥离 events 路由业务逻辑
- ✅ `services/mastery_service.py` — 已剥离 mastery 更新逻辑
- ✅ 已添加 `EventCreate` Pydantic 模型（`app/schemas.py`）

**Step 3（已完成）：**
- ✅ `engine/tracks/jon.py` + `engine/tracks/astrid.py`
- ✅ 已移除引擎内 `db.add()` / `db.commit()`（持久化迁移到路由侧 `item_service.py`）
- ✅ 引擎主函数改为 Registry 查找

**Step 4（已完成）：**
- ✅ 修复 `sys.path.append` hack
- ✅ 全量 pytest 通过（当前 `27 passed`）
- ✅ CORS 收紧（从 `*` 改为配置化白名单）

---

## 📝 结果备注

- 今日已超额完成：Step 1-4 全部落地。
- `POST /events` 仍可用，并通过测试回归。

---

## 🔵 当前待办（Phase 7）

- [x] 定义并输出评估指标：完成率、波动度、恢复速度
- [x] 为 Phase 7 指标新增后端测试用例
- [x] 家长端详情页补充趋势图可视化（最近7天准确率趋势）
- [x] 日报卡片补充指标摘要（完成率/波动度/恢复速度）
- [x] 家长主页面补充图表化趋势视图（日报卡片最近7天准确率迷你趋势图）
- [x] 周报页多指标联动图表（跨学生周维度对比）

---

## ⏭️ 下一阶段（Phase 8 启动清单）

- [x] 建立认证数据模型：`Parent` + `students.parent_id` + `students.pin_hash`
- [x] 新增认证路由：`/auth/register`、`/auth/login`、`/auth/student-login`
- [x] 新增 JWT 与权限依赖：`require_parent` / `require_student`
- [x] 家长接口加 `parent_id` 数据隔离
- [x] iOS APIClient 引入 token 存储与请求头注入
- [x] iOS 登录入口（家长登录/注册 + 学生 PIN 登录）已接通
- [x] 学生相关接口完成全链路角色收口（parent/student 均按 `student_id` 授权）
- [x] iOS 401 统一处理：清 token + 自动回跳登录页
- [x] 验证：后端 `27 passed`；iOS `xcodebuild ... build` 通过
- [x] iOS token 存储升级到 Keychain（含旧 UserDefaults token 迁移）
- [x] 学生模式核心做题链路支持不传 `student_id`（后端从 token 推导；家长模式保留显式 student_id）
- [x] 学生查询接口新增 `me` 风格入口（`/mastery/me`、`/streak/me`、`/achievements/me`）
- [x] `events` 支持学生模式省略 `student_id`（后端自动绑定 token 的 `sub`）
- [x] iOS 提交事件在学生模式下不再显式发送 `student_id`
- [x] `students` 路由补齐 `"me"` 别名兼容（`/students/me`、`/streak/me` 兼容动态路由匹配）
- [x] `daily-session/status/{student_id}` 补齐 `"me"` 别名兼容（动态路由与 `/daily-session/status` 行为一致）
- [x] iOS 学生角色查询统一走 `me` 路径（status/mastery/streak/achievements）
- [x] iOS APIClient 学生相关接口参数收敛：`studentId` 改为可选（student 角色省略；parent 角色保留强校验）
- [x] 学生端页面调用开始切换无参模式（QuestionViewModel/AchievementsView）
- [x] `QuestionView` 学生模式下不再向 ViewModel 传递显式 `studentId`
- [x] 新增 Phase 8 HTTP 级权限回归测试（auth + `me` + 越权拦截 + parent 作用域）
- [x] 新增 Phase 8 生产安全门禁：`ENVIRONMENT=production` 下启动配置校验 + 预检脚本
- [x] 补齐发布资产：`services/api/.env.example` + `docs/qa/PHASE8_RELEASE_CHECKLIST.md`
- [x] 补齐联调脚本：`services/api/scripts/smoke_phase8_auth.py`
- [x] 本仓库 API（8010）完成端到端 smoke 演练：parent + student 全通过
- [x] 补齐发布签核模板：`docs/qa/PHASE8_RELEASE_APPROVAL.md`
- [x] 验证更新：后端 `41 passed`；iOS `xcodebuild ... build` 通过
