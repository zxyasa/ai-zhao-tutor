# MathCoach Development Guide

## Project Overview
Full-stack AI math training system for NSW Year 3-6 students.

## Architecture
- **Monorepo**: All services in one repository
- **Backend**: FastAPI + PostgreSQL
- **Content**: Python generators (deterministic math)
- **Frontend**: SwiftUI iPad app (MVVM)

## Development Workflow

### 1. Backend Changes
```bash
cd services/api
# Make changes to models, routers, etc.
# Test locally:
uvicorn app.main:app --reload
```

### 2. Content Changes
```bash
cd services/content
# Edit curriculum or templates
python generate_items.py
python validate_items.py
```

### 3. Docker Workflow
```bash
cd ops/docker
docker-compose up -d
docker-compose logs -f api
docker-compose down
```

## Coding Standards

### Python
- Use type hints
- Follow PEP 8
- Keep functions small and focused
- Write deterministic code (no randomness in production)

### Database
- Always use migrations for schema changes
- Index foreign keys
- Use transactions for multi-step operations

### API
- RESTful endpoints
- Clear error messages
- Validate all inputs with Pydantic

### Content Generation
- All math must be verifiable
- Include hints and explanations
- Test edge cases

## Common Tasks

### Add a New Skill
1. Add to `services/content/curriculum/nsw_year3_6.py`
2. Create template in `services/content/templates/`
3. Register template in `templates/__init__.py`
4. Run `python generate_items.py`
5. Run `python validate_items.py`

### Add a New API Endpoint
1. Create router in `services/api/app/routers/`
2. Register in `services/api/app/main.py`
3. Test with curl or Swagger UI

### Add a New Database Model
1. Create model in `services/api/app/models/`
2. Update `models/__init__.py`
3. Create migration (if using Alembic)
4. Run migration

## Testing
- Validate all content with `validate_items.py`
- Test API endpoints via `/docs`
- Manual testing on iPad simulator

## Don'ts
- ❌ Don't skip validation
- ❌ Don't hardcode credentials
- ❌ Don't generate random answers
- ❌ Don't break determinism
- ❌ Don't overengineer simple features

## Deployment (Future)
- Use environment variables for config
- PostgreSQL for production
- Docker Compose for staging
- TestFlight for iOS app distribution

---

# AI 防爆仓协议 (Crash-Safe Protocol)

## 一、启动协议 (MANDATORY — 每次新会话第一步)

```
1. 读取 .ai/active-task.json → 获取当前任务名
2. 读取 .ai/tasks/<task>/progress.md → 了解进度
3. 读取 .ai/tasks/<task>/context.md → 获取最小上下文
4. 检查 .ai/lock.json → 是否有其他终端占用
5. 输出续跑计划，等待用户确认后再动手
```

**禁止**: 跳过上述步骤直接开始工作。
**禁止**: 在没有读取 progress.md 的情况下扫描项目文件。

如果 `.ai/active-task.json` 中 task 为 null，提示用户创建新任务。

## 二、步进执行协议 (Step Protocol)

每个步骤必须严格按以下顺序执行：

```
1. 宣布当前步骤: "Step N/M: <描述>"
2. 执行代码修改（最多 3 个文件）
3. 更新 .ai/tasks/<task>/progress.md（标记当前步骤完成）
4. 更新 .ai/tasks/<task>/context.md（如果关键文件清单变化）
5. 建议 git commit: [ai:<task>] step N/M: <描述>
6. 等待用户确认后再执行下一步
```

**关键原则: progress.md 先于一切。** 如果只能做一件事，就是更新 progress.md。

## 三、禁止全仓扫描规则

### 允许读取的文件
- `CLAUDE.md`（本文件）
- `.ai/active-task.json`
- `.ai/tasks/<当前任务>/` 下的所有文件
- `context.md` 中 "Key Files" 列出的文件
- `Grep` 精确搜索命中的文件（必须有明确搜索目标）

### 禁止
- 禁止一次性读取超过 5 个源码文件
- 禁止递归列目录获取全项目结构
- 禁止 "先了解一下项目" 式的大范围扫描
- 禁止读取与当前任务无关的模块

### 如需了解新模块
1. 先在 context.md 的 Search Hints 中查找线索
2. 用 Grep 精确搜索关键词
3. 只读命中的文件
4. 将新发现的关键文件加入 context.md

## 四、Token 风险控制

| 风险等级 | 条件 | 策略 |
|---------|------|------|
| LOW | 修改 1-2 文件，每文件 < 50 行变更 | 直接执行 |
| MEDIUM | 修改 3 文件，或单文件 > 50 行变更 | 先更新 progress，再执行 |
| HIGH | 修改 > 3 文件，或涉及重构 | **必须拆分**为多个 step |
| CRITICAL | 全局重命名/大规模重构 | **禁止**单步执行，拆分为独立子任务 |

### 强制规则
- 单步修改不超过 3 个文件
- 单个文件修改不超过 100 行
- 禁止一次性输出超过 200 行代码
- 如果预估操作会消耗大量 token，必须提前告知用户并建议拆分
- 生成测试文件时，每个测试文件单独一步

## 五、Git 工作流

### Commit message 格式
```
[ai:<task-name>] step N/M: <简短描述>

refs: .ai/tasks/<task-name>/progress.md
```

### 快捷脚本
```bash
.ai/scripts/ai-commit.sh <task-name> <step> <total> "<message>"
.ai/scripts/ai-save.sh
.ai/scripts/ai-new-task.sh <task-name> "<goal>"
```

## 六、多终端并发控制

### Terminal ID: `windows-vscode` / `macbook-vscode` / `iphone-ssh`

### 锁机制
- 开始工作前写入 `.ai/lock.json`（终端 ID + 时间戳 + TTL 30min）
- 锁超过 TTL 自动过期，新终端可接管

## 七、续跑模板

当被要求"继续"时，先读 progress.md + context.md，输出续跑报告，等待确认。

## 八、安全启动模板

当没有活跃任务时，提示用户创建新任务（名称 + 目标 + 模块）。
