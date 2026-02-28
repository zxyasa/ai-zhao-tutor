# AI Zhao Tutor 升级计划 2026
## 打造：低摩擦、可持续、动态自适应的家庭 AI 数学教练系统

**日期：** 2026-02-18（持续更新中）
**服务对象：** Jon、Astrid
**当前完成度：** ~93%（核心链路稳定，已完成架构固化）

---

## 进展快照（2026-02-21）

- ✅ Phase 0：已完成（Notes 早晚自动流程可用）
- ✅ Phase 1：已完成（双学生档案 + 学生选择）
- ✅ Phase 2：已完成（20 skills / 1275 items / 全量校验通过）
- ✅ Phase 3（MVP）：已完成（自适应引擎抽离 + 连对升/连错降）
- 🟡 Phase 4：大部分完成（daily session + streak 接口已补齐，题单标准化待收口）
- 🟡 Phase 5：大部分完成（日报/周报 + 单学生 progress 已上线，图表页待完善）
- 🟡 Phase 6：大部分完成（徽章解锁/查询/新徽章接口已上线，激励动画与扩展徽章待做）
- ✅ Phase 6.5：已完成（架构固化 — 协议/服务层/插件化/去副作用/CORS/测试）
- ✅ Phase 7：已完成（时间衰减掌握度 + 风险信号 + 指标输出 + 详情/主页面趋势图 + 周报联动图）
- 🟡 Phase 8：收口验证完成，待手工签字关闭（2026-02-21）（自动化回归 `41 passed, 0 failed`；待补 iOS 401 手工回跳验证与线上 smoke 环境一致性）

> 注：下文 Phase 0-6 的大段方案为历史设计草案，保留用于追溯；以本节“进展快照”和 `CURRENT_STATUS.md` 为当前执行基线。

---

## 一、现状分析（已有什么）

```
✅ FastAPI 后端（Docker + PostgreSQL）
✅ iOS SwiftUI 应用（MVVM 架构）
✅ 基础自适应题目选择（基于 mastery_score）
✅ 110 道题（分数领域，3 个技能）
✅ 答案验证（exact / numeric / fraction）
✅ 计时器 + 提示系统

❌ 只有 1 个测试学生（test_001），没有真实的 Jon / Astrid 档案
❌ 只有 3 个技能，缺少完整技能树
❌ 没有每日习惯机制（无调度、无连续打卡）
❌ 没有错题模式分析
❌ 没有家长仪表盘
❌ 没有成就/激励系统
❌ 没有每日汇总报告
```

---

## 二、核心缺口 → 升级目标映射

| 现状缺口 | 升级目标 | 优先级 |
|---------|---------|--------|
| 单学生 | Jon + Astrid 独立档案 | P0 |
| 3个技能 | 20+ 技能覆盖 NSW Year 3-6 | P0 |
| 无每日习惯 | 每日自动调度 + 连续打卡 | P0 |
| 简单难度选择 | 真正自适应算法 + 错题优先 | P1 |
| 无家长视图 | 家长仪表盘 + 每日报告 | P1 |
| 无激励 | 徽章 + 连续天数 + 成就 | P2 |

---

## 三、分阶段实施计划

---

### 🚀 Phase 0：Mac Notes 每日推送（短期过渡方案，本周落地）

**目标：** 在 iOS App 完全就绪前，**今天就能开始训练**。

利用 Mac Studio 常驻运行的优势，每天早晨自动生成题目、推送到 iCloud 共享便签，孩子在 iPad 的 Notes App 里打开就能做题。

**完整流程：**

```
07:30 Mac Studio 定时任务
  → Python 脚本生成今日题目
  → AppleScript 写入 Apple Notes（iCloud 同步）
  → Jon 的便签 + Astrid 的便签（分开）
  → iPad 上打开 Notes App 即可看到

晚上 20:00
  → 家长收到 iMessage 汇总（用 Python + osascript）
```

#### Phase 0 实现文件

**`services/notes/daily_generator.py`**（新增）

```python
#!/usr/bin/env python3
"""
每日题目生成 + 推送到 Apple Notes
运行方式: python daily_generator.py --student jon
"""
import subprocess
import datetime
import random

def generate_questions_for_student(student_id: str, count: int = 10) -> list[dict]:
    """
    从后端 API 拉取今日题目
    如果后端未运行，退化为本地静态生成
    """
    try:
        import httpx
        resp = httpx.get(f"http://localhost:8000/api/v1/daily-session/{student_id}")
        return resp.json()["items"]
    except Exception:
        # 降级方案：直接本地生成（不依赖后端）
        return _generate_local(student_id, count)

def format_note_content(student_name: str, questions: list[dict]) -> str:
    today = datetime.date.today().strftime("%m月%d日")
    lines = [
        f"📐 {student_name} 的数学练习 — {today}",
        "─" * 30,
        "",
    ]
    for i, q in enumerate(questions, 1):
        lines.append(f"{i}. {q['question_text']}")
        lines.append(f"   答案：___________")
        lines.append("")
    lines += [
        "─" * 30,
        f"完成 {len(questions)} 题后告诉爸爸 ✅",
    ]
    return "\n".join(lines)

def push_to_apple_notes(title: str, content: str, folder: str = "数学练习"):
    """通过 AppleScript 写入 Apple Notes（iCloud 账户自动同步到 iPad）"""
    escaped = content.replace('"', '\\"').replace("\\n", "\\n")
    script = f'''
    tell application "Notes"
        tell account "iCloud"
            if not (exists folder "{folder}") then
                make new folder with properties {{name:"{folder}"}}
            end if
            set theFolder to folder "{folder}"
            set newNote to make new note at theFolder with properties {{
                name:"{title}",
                body:"{escaped}"
            }}
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def send_parent_summary(summary: str):
    """用 osascript 发 iMessage 给家长"""
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "你的手机号" of targetService
        send "{summary}" to targetBuddy
    end tell
    '''
    subprocess.run(["osascript", "-e", script])
```

**`services/notes/scheduler.sh`**（新增，用 launchd 调度）

```bash
#!/bin/bash
# 注册为 Mac 开机自启动定时任务

PLIST="$HOME/Library/LaunchAgents/com.zhao.mathcoach.daily.plist"

cat > "$PLIST" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.zhao.mathcoach.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/michaelzhao/agents/apps/ai-zhao-tutor/services/notes/run_daily.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <!-- 早上 7:30 生成题目 -->
        <dict>
            <key>Hour</key><integer>7</integer>
            <key>Minute</key><integer>30</integer>
        </dict>
        <!-- 晚上 20:00 发汇总 -->
        <dict>
            <key>Hour</key><integer>20</integer>
            <key>Minute</key><integer>0</integer>
        </dict>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/mathcoach_daily.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/mathcoach_daily_err.log</string>
</dict>
</plist>
EOF

launchctl load "$PLIST"
echo "✅ 定时任务已注册。每天 7:30 自动生成题目，20:00 发送汇总。"
```

**`services/notes/run_daily.py`**（新增，统一入口）

```python
#!/usr/bin/env python3
"""
每日定时任务入口
07:30 → 生成题目推送到 Notes
20:00 → 汇总今日结果
"""
import datetime
import sys
from daily_generator import generate_questions_for_student, format_note_content, push_to_apple_notes

STUDENTS = [
    {"id": "jon_zhao",    "name": "Jon"},
    {"id": "astrid_zhao", "name": "Astrid"},
]

hour = datetime.datetime.now().hour

if 6 <= hour < 12:
    # 早晨：推送题目
    for s in STUDENTS:
        questions = generate_questions_for_student(s["id"])
        title = f"{s['name']} 数学 {datetime.date.today().strftime('%m/%d')}"
        content = format_note_content(s["name"], questions)
        push_to_apple_notes(title, content)
        print(f"✅ {s['name']} 的题目已推送到 Notes")

elif hour >= 18:
    # 晚上：发汇总给家长（第一阶段可以手动查看 Notes，后续接 API）
    print("📊 晚间汇总（Phase 0 暂时打印到日志，待家长仪表盘完成后接入）")
```

**操作步骤（一次性设置，15 分钟完成）：**

```bash
# 1. 确保 Apple Notes 账户已登录 iCloud
# 2. 创建共享文件夹（在 Notes App 里手动建一次"数学练习"文件夹并共享给孩子的 iPad）

# 3. 安装依赖
pip3 install httpx

# 4. 测试推送
cd ~/agents/ai-zhao-tutor/services/notes
python3 run_daily.py  # 手动运行看效果

# 5. 注册定时任务
bash scheduler.sh
```

**Phase 0 的优势：**
- ✅ 今天就能用，不需要等 iOS App
- ✅ 孩子在 iPad 上 Notes App 已经熟悉
- ✅ iCloud 自动同步，无需手动操作
- ✅ Mac Studio 24/7 常驻，天然调度器
- ✅ 随时可以升级接入后端 API（已预留 httpx 接口）

**Phase 0 的局限（可以接受）：**
- 孩子用纸笔写答案，你批改（暂时）
- 没有自动批改
- 没有进度追踪

→ 这些由后续 Phase 1-6 逐步解决。

---

### 🟢 Phase 1：双学生真实档案（1-2天）

**目标：** 让 Jon 和 Astrid 能独立登录、独立训练、独立记录进度

#### 后端变更

**1. 创建真实学生数据（`services/api/scripts/seed_students.py`）**

```python
students = [
    {
        "id": "jon_zhao",
        "name": "Jon",
        "year_level": 4,        # 根据实际年级调整
        "avatar": "lion",       # 孩子选择的头像
        "target_daily_questions": 10,
    },
    {
        "id": "astrid_zhao",
        "name": "Astrid",
        "year_level": 3,        # 根据实际年级调整
        "avatar": "unicorn",
        "target_daily_questions": 10,
    }
]
```

**2. 扩展 Student 模型（`services/api/app/models/student.py`）**

新增字段：
- `avatar` — 头像标识符
- `target_daily_questions` — 每日目标题数
- `current_streak` — 当前连续天数
- `longest_streak` — 历史最长连续天数
- `last_practice_date` — 上次练习日期
- `total_sessions` — 总训练次数

#### iOS 变更

**3. 学生选择界面（新增 `Views/StudentPickerView.swift`）**

```
┌─────────────────────────────────────┐
│         谁来练习数学？                │
│                                     │
│    🦁                  🦄           │
│   Jon                Astrid         │
│  Year 4              Year 3         │
│  🔥 5天              🔥 3天          │
│                                     │
│  [开始训练]          [开始训练]       │
└─────────────────────────────────────┘
```

**4. 修改应用入口（`ContentView.swift`）**

将欢迎界面改为学生选择 → 进入各自训练

---

### 🟢 Phase 2：技能树扩展（2-3天）

**目标：** 覆盖 NSW Year 3-6 完整数学技能树

#### 技能树结构（`services/content/curriculum/skill_tree.py`）

```python
SKILL_TREE = {
    # ── Year 3 ──────────────────────────────
    "yr3_add_2digit":      {"name": "两位数加法",    "year": 3, "domain": "number"},
    "yr3_sub_2digit":      {"name": "两位数减法",    "year": 3, "domain": "number"},
    "yr3_mul_table_2to5":  {"name": "乘法口诀2-5",  "year": 3, "domain": "number"},
    "yr3_frac_basic":      {"name": "分数基础",      "year": 3, "domain": "fraction"},
    "yr3_frac_compare":    {"name": "分数比较",      "year": 3, "domain": "fraction",
                            "prereq": ["yr3_frac_basic"]},
    "yr3_measure_length":  {"name": "长度测量",      "year": 3, "domain": "measurement"},
    "yr3_time_basic":      {"name": "时间基础",      "year": 3, "domain": "measurement"},

    # ── Year 4 ──────────────────────────────
    "yr4_add_3digit":      {"name": "三位数加减法",  "year": 4, "domain": "number"},
    "yr4_mul_table_6to9":  {"name": "乘法口诀6-9",  "year": 4, "domain": "number"},
    "yr4_div_basic":       {"name": "除法基础",      "year": 4, "domain": "number"},
    "yr4_frac_equiv":      {"name": "等价分数",      "year": 4, "domain": "fraction",
                            "prereq": ["yr3_frac_compare"]},
    "yr4_decimal_basic":   {"name": "小数基础",      "year": 4, "domain": "decimal"},
    "yr4_area_perimeter":  {"name": "面积与周长",    "year": 4, "domain": "measurement"},

    # ── Year 5 ──────────────────────────────
    "yr5_mul_2digit":      {"name": "两位数乘法",    "year": 5, "domain": "number"},
    "yr5_div_long":        {"name": "长除法",        "year": 5, "domain": "number"},
    "yr5_frac_add_diff":   {"name": "异分母分数加法", "year": 5, "domain": "fraction"},
    "yr5_decimal_ops":     {"name": "小数运算",      "year": 5, "domain": "decimal"},
    "yr5_percentage":      {"name": "百分数基础",    "year": 5, "domain": "percentage"},

    # ── Year 6 ──────────────────────────────
    "yr6_ratio":           {"name": "比例",          "year": 6, "domain": "ratio"},
    "yr6_algebra_basic":   {"name": "代数基础",      "year": 6, "domain": "algebra"},
    "yr6_statistics":      {"name": "数据统计",      "year": 6, "domain": "statistics"},
}
```

#### 内容生成目标

每个技能生成 **50 道题**（难度 1-5，每级 10 道），总计 **1000+ 道题**。

优先为 Jon（Year 4）和 Astrid（Year 3）覆盖的技能先实现：

**本月必须完成的题型模板（按优先级）：**
1. `yr3_mul_table_2to5` — 乘法口诀（Astrid 最需要）
2. `yr4_mul_table_6to9` — 乘法口诀（Jon 最需要）
3. `yr4_div_basic` — 除法基础
4. `yr3_add_2digit` / `yr4_add_3digit` — 加减法
5. `yr4_decimal_basic` — 小数

---

### 🟡 Phase 3：真正自适应算法（2-3天）

**目标：** 从"随机难度选择"升级为"智能训练计划生成"

#### 核心算法（`services/api/app/engine/adaptive.py`）

**3.1 掌握度模型（每个学生每个技能独立）**

```python
class MasteryState:
    skill_id: str
    mastery_score: float     # 0.0 ~ 1.0
    attempts: int
    correct_streak: int      # 连续答对次数
    error_streak: int        # 连续答错次数
    last_error_types: list   # 最近错误类型
    current_difficulty: int  # 当前难度 1-5

    def should_level_up(self) -> bool:
        return self.correct_streak >= 3 and self.mastery_score > 0.75

    def should_level_down(self) -> bool:
        return self.error_streak >= 2 or self.mastery_score < 0.4
```

**3.2 题目选择策略（`select_next_item()`）**

```python
def select_next_item(student_id: str) -> Item:
    """
    优先级顺序：
    1. 错题复习（最近 24h 内的错题，30% 概率）
    2. 当前弱点技能（mastery_score 最低的技能）
    3. 正常训练（当前技能当前难度）
    4. 探索新技能（mastery > 0.8 时解锁下一技能）
    """
```

**3.3 错误模式识别**

```python
ERROR_TYPES = {
    "calculation_error":   "计算错误（过程对，结果错）",
    "concept_error":       "概念错误（根本不理解）",
    "careless_error":      "粗心错误（简单题答错）",
    "time_pressure_error": "时间压力错误（超时失误）",
}
```

通过分析：
- 是否对同类题型反复错
- 错误发生在哪个难度
- 是否只在快速作答时出错

来识别错误类型，选择对应的矫正题。

**3.4 每日训练计划生成**

```python
def generate_daily_session(student_id: str, target: int = 10) -> list[Item]:
    """
    生成今日练习题单（40道）
    组成：
    - 3道 错题复习（昨天的错题）
    - 4道 当前弱点技能练习
    - 2道 主技能稳固
    - 1道 挑战题（当前难度+1）
    """
```

---

### 🟡 Phase 4：每日习惯系统（2-3天）

**目标：** 让"每天练习"变成自然发生的事，而不是需要提醒的事

#### 4.1 每日会话管理

**新增 API 端点：**

```
GET  /api/v1/daily-session/{student_id}   # 获取今日练习题单
POST /api/v1/daily-session/{student_id}/complete  # 完成今日练习
GET  /api/v1/streak/{student_id}          # 获取连续天数
```

**会话限制逻辑：**
- 每日目标：10 道题（可调整）
- 完成后显示"今天完成了！"页面
- 次日自动重置
- 允许"加练"（完成基础后可选择继续）

#### 4.2 iOS 端每日状态（修改 `QuestionView.swift`）

```
今日进度条：
[██████████] 10/10 ✅ 今天完成了！

或

[████░░░░░░] 4/10  继续加油！
```

#### 4.3 Apple Shortcuts 自动调度

创建两个 Shortcut：

**晨间提醒（7:30 AM）：**
```
触发：每天早上 7:30
动作：发送通知 "Jon，今天的数学练习准备好了！" + 打开 App
```

**晚间汇总（8:00 PM）：**
```
触发：每天晚上 8:00
动作：调用 GET /api/v1/daily-summary → 发送总结给 Michael
```

#### 4.4 连续打卡机制（后端 + iOS）

**后端：**
```python
def update_streak(student_id: str):
    today = date.today()
    student = get_student(student_id)

    if student.last_practice_date == today - timedelta(days=1):
        student.current_streak += 1
        student.longest_streak = max(student.current_streak, student.longest_streak)
    elif student.last_practice_date < today - timedelta(days=1):
        student.current_streak = 1  # 断了，重新开始

    student.last_practice_date = today
```

**iOS 显示：**
```
🔥 Jon 已连续练习 12 天！
```

---

### 🟡 Phase 5：家长仪表盘（2-3天）

**目标：** 让你（Michael）不需要手动监督，系统自动告诉你该知道的

#### 5.1 家长视图入口（iOS）

隐藏入口：在设置里，长按 3 秒 → 输入 PIN（4位数）→ 进入家长模式

#### 5.2 家长仪表盘界面（新增 `Views/ParentDashboardView.swift`）

```
┌──────────────────────────────────────────────┐
│  📊 家长中心                      今天 2/18   │
├──────────────────────────────────────────────┤
│                                              │
│  Jon (Year 4)              Astrid (Year 3)   │
│  🔥 12天连续              🔥 5天连续          │
│  今日 ✅ 10/10            今日 ⏳ 0/10        │
│  本周正确率 84%           本周正确率 71%       │
│                                              │
│  Jon 的弱点：                                │
│  ⚠️ 小数运算（掌握度 43%）                    │
│  ⚠️ 长除法（掌握度 51%）                      │
│                                              │
│  Astrid 的弱点：                              │
│  ⚠️ 分数比较（掌握度 38%）                    │
│                                              │
│  [查看详细报告]  [本周总结]  [调整设置]        │
└──────────────────────────────────────────────┘
```

#### 5.3 每日自动汇总（新增 API）

```
GET /api/v1/daily-summary?date=2026-02-18
```

返回：
```json
{
  "date": "2026-02-18",
  "students": [
    {
      "name": "Jon",
      "completed": true,
      "questions_attempted": 10,
      "correct": 8,
      "accuracy": 0.80,
      "streak": 12,
      "skills_practiced": ["yr4_mul_table_6to9", "yr4_div_basic"],
      "weakest_skill": "yr4_decimal_basic",
      "improvement_vs_yesterday": "+5%"
    },
    {
      "name": "Astrid",
      "completed": false,
      "questions_attempted": 0,
      "streak_at_risk": true
    }
  ]
}
```

#### 5.4 进度图表（`Views/ProgressChartView.swift`）

使用 Swift Charts（iOS 16+）展示：
- 每日正确率趋势（折线图，30天）
- 各技能掌握度（雷达图）
- 连续天数日历视图

---

### 🔵 Phase 6：成就与激励系统（2-3天）

**目标：** 让孩子发自内心地想每天练习

#### 6.1 徽章系统（`services/api/app/models/achievement.py`）

```python
BADGES = {
    # 连续天数徽章
    "streak_3":   {"name": "连续3天",   "emoji": "🌱", "condition": "streak >= 3"},
    "streak_7":   {"name": "一周连续",   "emoji": "🔥", "condition": "streak >= 7"},
    "streak_30":  {"name": "月度冠军",   "emoji": "🏆", "condition": "streak >= 30"},

    # 正确率徽章
    "perfect_day": {"name": "完美一天",  "emoji": "⭐", "condition": "daily_accuracy == 1.0"},
    "accuracy_90": {"name": "精准射手",  "emoji": "🎯", "condition": "weekly_accuracy >= 0.9"},

    # 技能掌握徽章
    "skill_master": {"name": "技能大师", "emoji": "🧠", "condition": "any mastery_score >= 0.9"},
    "all_rounder":  {"name": "全能冠军", "emoji": "👑", "condition": "5+ skills mastered"},

    # 里程碑徽章
    "q100":   {"name": "百题达人",  "emoji": "💯", "condition": "total_questions >= 100"},
    "q500":   {"name": "五百题侠", "emoji": "🦸", "condition": "total_questions >= 500"},
    "q1000":  {"name": "千题王者", "emoji": "⚡", "condition": "total_questions >= 1000"},
}
```

#### 6.2 成就解锁动画（iOS）

解锁新徽章时：
- 全屏庆祝动画（烟花 + 音效）
- "你解锁了：🏆 月度冠军！"
- 保存到成就收藏册

#### 6.3 连续天数可视化

```
一月：
Mo Tu We Th Fr Sa Su
          ◆  ◆  ◆  ◆
◆  ◆  ◆  ◆  ◆  ◆  ◆
◆  ◆  ◆  ◆  ◆  ◆  ◆
◆  ◆  ◆

◆ = 完成练习的天数（绿色填充）
```

---

## 四、技术实现细节

### 数据库新增表

```sql
-- 每日会话记录
CREATE TABLE daily_sessions (
    id UUID PRIMARY KEY,
    student_id VARCHAR REFERENCES students(id),
    session_date DATE NOT NULL,
    target_questions INT DEFAULT 10,
    completed_questions INT DEFAULT 0,
    correct_questions INT DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 成就记录
CREATE TABLE achievements (
    id UUID PRIMARY KEY,
    student_id VARCHAR REFERENCES students(id),
    badge_id VARCHAR NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, badge_id)
);

-- 错题记录（用于复习）
CREATE TABLE mistake_reviews (
    id UUID PRIMARY KEY,
    student_id VARCHAR REFERENCES students(id),
    item_id UUID REFERENCES items(id),
    error_type VARCHAR,           -- calculation/concept/careless/time_pressure
    mistake_made_at TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP
);
```

### 新增 API 端点总览

```
# 学生管理
GET  /api/v1/students                    # 所有学生列表（for student picker）

# 每日会话
GET  /api/v1/daily-session/{student_id}  # 今日训练题单
POST /api/v1/daily-session/{student_id}/complete

# 成就系统
GET  /api/v1/achievements/{student_id}   # 获取所有成就
GET  /api/v1/achievements/{student_id}/new  # 检查新成就

# 家长报告
GET  /api/v1/parent/summary              # 所有学生今日汇总
GET  /api/v1/parent/weekly-report        # 本周报告
GET  /api/v1/parent/{student_id}/progress  # 单个学生进度图表数据

# 连续天数
GET  /api/v1/streak/{student_id}

# 错题管理
GET  /api/v1/mistakes/{student_id}?unreviewed=true
```

---

## 五、文件变更清单

### 后端（`services/api/`）

| 文件 | 操作 | 内容 |
|------|------|------|
| `app/models/student.py` | 修改 | 添加 streak、avatar、target_daily 字段 |
| `app/models/daily_session.py` | 新增 | 每日会话模型 |
| `app/models/achievement.py` | 新增 | 成就模型 |
| `app/models/mistake_review.py` | 新增 | 错题复习模型 |
| `app/engine/adaptive.py` | 新增 | 自适应算法核心 |
| `app/engine/streak.py` | 新增 | 连续天数逻辑 |
| `app/engine/achievements.py` | 新增 | 成就解锁逻辑 |
| `app/routers/daily_session.py` | 新增 | 每日会话端点 |
| `app/routers/parent.py` | 新增 | 家长报告端点 |
| `app/routers/achievements.py` | 新增 | 成就端点 |
| `scripts/seed_students.py` | 新增 | 创建 Jon & Astrid |

### 内容生成（`services/content/`）

| 文件 | 操作 | 内容 |
|------|------|------|
| `curriculum/skill_tree.py` | 修改 | 扩展到 20+ 技能 |
| `templates/multiplication.py` | 新增 | 乘法口诀模板 |
| `templates/division.py` | 新增 | 除法模板 |
| `templates/addition_subtraction.py` | 新增 | 加减法模板 |
| `templates/decimals.py` | 新增 | 小数模板 |

### iOS（`apps/ios/MathCoach/`）

| 文件 | 操作 | 内容 |
|------|------|------|
| `Views/StudentPickerView.swift` | 新增 | 学生选择主页 |
| `Views/DailyProgressView.swift` | 新增 | 今日进度显示 |
| `Views/ParentDashboardView.swift` | 新增 | 家长仪表盘 |
| `Views/AchievementView.swift` | 新增 | 成就收藏册 |
| `Views/ProgressChartView.swift` | 新增 | 进度图表 |
| `Models/Achievement.swift` | 新增 | 成就数据模型 |
| `Models/DailySession.swift` | 新增 | 每日会话模型 |
| `ViewModels/StudentViewModel.swift` | 新增 | 学生选择逻辑 |
| `ViewModels/ParentViewModel.swift` | 新增 | 家长视图逻辑 |
| `ContentView.swift` | 修改 | 改为学生选择作为入口 |

---

## 六、实施路线图

```
今天（Day 0）— Phase 0 落地
├── 创建 services/notes/ 目录
├── 写 daily_generator.py + run_daily.py
├── 手动测试一次推送到 Notes
└── 注册 launchd 定时任务
→ 结果：明早 7:30 Jon 和 Astrid 各自有一份便签题目

Week 1
├── Day 1-2: Phase 1（双学生档案）
│   ├── 后端：seed_students.py + Student 模型扩展
│   └── iOS：StudentPickerView + 多学生切换
│
├── Day 3-4: Phase 2（技能树扩展）
│   ├── 乘法口诀模板（Jon+Astrid 最紧迫）
│   ├── 除法模板
│   └── 加减法模板
│
└── Day 5: Phase 3（自适应算法）
    ├── adaptive.py 核心逻辑
    ├── Phase 0 升级：daily_generator.py 接入后端 API
    └── 错题复习机制

Week 2
├── Day 1-2: Phase 4（每日习惯系统）
│   ├── 每日会话 API
│   ├── iOS 进度条
│   └── Notes 推送退役，全面切换到 iOS App
│
├── Day 3-4: Phase 5（家长仪表盘）
│   ├── 家长 API 端点
│   └── iOS 家长视图
│
└── Day 5: Phase 6（成就系统）
    ├── 徽章定义
    └── iOS 成就动画

Week 3: 真实测试
├── Jon 和 Astrid 试用 3 天
├── 根据反馈调整
└── 优化体验细节
```

---

## 七、关键成功指标

**习惯形成（最重要）：**
- Jon 连续练习 7 天 ✓
- Astrid 连续练习 7 天 ✓
- 每天完成率 > 80%

**学习效果：**
- 每周进步（正确率提升 > 5%）
- 弱点技能掌握度提升
- 错题不再重复出错

**系统运行：**
- 你每天花在监督上的时间 < 5 分钟
- 系统自动汇报，无需手动检查

---

## 八、第一步行动（今天就做）

1. **创建 Jon 和 Astrid 的真实学生档案**
   ```bash
   cd services/api/scripts
   python seed_students.py  # 需要先创建这个文件
   ```

2. **乘法口诀题目生成**（Jon 和 Astrid 最需要的技能）
   - 创建 `services/content/templates/multiplication.py`
   - 生成 100 道乘法口诀题

3. **学生选择界面**
   - 创建 `StudentPickerView.swift`
   - 替换当前的欢迎界面

---

*这个计划的核心不是"技术有多复杂"，而是"孩子有没有每天打开 App"。*
*一切技术决策都应该服务于这个终极目标。*

---

### 🔵 Phase 6.5：架构固化（当前阶段，1-2 周）

**目标：** 在进入 Phase 7 之前，将系统固化为结构稳定的教育引擎平台。
当前系统已具备完整功能骨架，但三层边界尚未固化，若继续叠加功能将导致维护成本指数增长。

#### 核心问题诊断

| 级别 | 问题 | 位置 |
|------|------|------|
| 🔴 Critical | 硬编码学生 ID 在引擎核心（`JON_STUDENT_ID`, `ASTRID_STUDENT_ID`） | `engine/adaptive.py:14-43` |
| 🔴 Critical | 引擎内部直接写数据库（`_create_dynamic_item` 含 `db.add()` + `db.commit()`） | `engine/adaptive.py:158-187` |
| 🔴 Critical | 全部业务逻辑堆积在路由层（mastery 更新 + streak + daily session + achievement 全在 `events.py`） | `routers/events.py` |
| 🟠 High | 无引擎输入/输出 Pydantic 协议模型 | `engine/` |
| 🟠 High | 无 `EventCreate` Pydantic 模型，路由接受裸 `Dict` | `routers/events.py:24` |
| 🟠 High | `sys.path.append("../../packages/shared")` hack | `events.py:7`, `mastery.py:5` |
| 🟠 High | `BADGE_DEFS` 硬编码在路由文件 | `routers/events.py:156-161` |
| 🟡 Medium | `mastery_score = correct/total` 无时间衰减 | `routers/events.py:75` |
| 🟡 Medium | `CORS allow_origins=["*"]` | `main.py:21` |
| 🟡 Medium | 函数体内懒导入 `from ..models import Item` | `routers/events.py:61` |
| 🟢 Low | `pytest` 全量尚未执行 | `tests/` |
| 🟢 Low | `total_sessions` 每次事件+1（应为每日会话计数） | `routers/events.py:123` |

#### 目标模块结构

```
services/api/app/
├── engine/
│   ├── protocol.py          ← 新增：引擎输入/输出契约（SelectionRequest / SelectionResult）
│   ├── adaptive.py          ← 重构：只读 DB，无 DB 写操作
│   ├── tracks/              ← 新增：个性化学习轨道插件系统
│   │   ├── base.py          ← TrackPlugin 抽象基类
│   │   ├── jon.py           ← Jon 专属轨道（从 adaptive.py 迁出）
│   │   └── astrid.py        ← Astrid 专属轨道（从 adaptive.py 迁出）
│   └── __init__.py
├── services/                ← 新增：业务逻辑服务层
│   ├── event_processor.py   ← 从 events.py 路由剥离的事件处理逻辑
│   ├── mastery_service.py   ← 掌握度计算（方便后续升级公式）
│   └── achievement_service.py ← Badge 定义 + 解锁逻辑（从路由迁出）
├── routers/
│   ├── events.py            ← 精简为：验证 → 调 service → 返回
│   └── items.py             ← 已干净，保持不变
```

#### 引擎协议设计（`engine/protocol.py`）

```python
from dataclasses import dataclass
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
    parameters: dict
    validation_rule: str
    # 引擎元数据（内部使用，不透传给客户端）
    selection_reason: str    # "weakest_skill" | "requested" | "fallback" | "custom_track"
    difficulty_delta: int    # -1 降难 | 0 持平 | +1 升难
```

#### 轨道插件系统（`engine/tracks/base.py`）

```python
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from ..protocol import SelectionResult

class TrackPlugin(ABC):
    @property
    @abstractmethod
    def student_id(self) -> str: ...

    @abstractmethod
    def build_item(self, db: Session) -> SelectionResult: ...

# 引擎主入口变为 Registry 查找，新增学生无需修改引擎核心
TRACK_REGISTRY: dict[str, TrackPlugin] = {}
```

#### events.py 路由精简后的形态

```python
# 当前：路由直接处理所有业务逻辑（200+ 行）
# 目标：路由只负责验证 + 分发

@router.post("/events")
async def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    result = await event_processor.process(db, event_data)
    return {"status": "success", "event_id": result.event_id}
```

#### 实施步骤（有序）

**Step 1（无破坏性，先做）：**
1. 创建 `engine/protocol.py`，定义 `SelectionRequest` / `SelectionResult`
2. 创建 `services/` 目录，将 `BADGE_DEFS` 迁移至 `services/achievement_service.py`
3. 将 `achievement_service` 中的 `_unlock_achievements` 逻辑从 `events.py` 迁出

**Step 2（需回归测试）：**
4. 创建 `services/event_processor.py`，将 events 路由中的业务逻辑迁入
5. 创建 `services/mastery_service.py`，将 mastery 更新逻辑迁入
6. 添加 `EventCreate` Pydantic 模型，替换裸 `Dict`

**Step 3（引擎重构）：**
7. 创建 `engine/tracks/` 插件系统
8. 将 `_build_jon_item` / `_build_astrid_item` 迁移至 `tracks/jon.py` / `tracks/astrid.py`
9. 将 `_create_dynamic_item` 的 DB 写操作移出引擎，迁至 `services/` 层
10. 引擎主函数改为 Registry 查找模式

**Step 4（收尾）：**
11. 修复 `sys.path.append` hack（proper package install 或内联 schema）
12. 执行全量 `pytest`，确保回归通过
13. 限制 `CORS allow_origins` 至已知来源

---

### ⬜ Phase 7：掌握度引擎升级（Phase 6.5 完成后）

**目标：** 将 `mastery_score = correct/total` 的朴素公式升级为具备时间感知的真实掌握度模型。

#### 当前公式的问题

```python
# 当前（events.py:75）
mastery_score = correct_attempts / total_attempts
```

问题：
- 100 次答对 60 次 = 最近 10 次答对 6 次 → 分数相同，但学习状态完全不同
- 无时间衰减：一个月前的练习与今天等权
- 无置信度区间：3 次答对 3 次（100%）被视为已掌握

#### 目标：加权滑动窗口掌握度

```python
# Phase 7 目标（mastery_service.py）
def compute_mastery_score(recent_results: list[bool], overall_rate: float) -> float:
    """
    recent_results: 最近 10 次答题结果（True/False 列表，最新在前）
    overall_rate: 历史总体正确率
    """
    if not recent_results:
        return overall_rate
    # 近期权重 0.7，历史权重 0.3
    recent_avg = sum(recent_results) / len(recent_results)
    return round(0.7 * recent_avg + 0.3 * overall_rate, 4)
```

#### Mastery 模型新增字段

| 字段 | 类型 | 用途 |
|------|------|------|
| `last_n_results` | JSON `[bool]` | 最近 10 次结果滑动窗口 |
| `score_trend` | Float | 近期斜率（正=进步，负=退步） |
| `confidence` | Float | 基于样本量的置信度（< 5 次为低置信） |
| `last_practiced_gap_days` | Int | 距上次练习的天数（用于衰减计算） |

#### skill_risk_level（家长预警触发器）

```python
def compute_risk_level(mastery: Mastery) -> str:
    """
    检测掌握度下滑，触发家长端预警提示
    """
    if mastery.score_trend < -0.1 and mastery.mastery_score < 0.5:
        return "high"       # 近期退步 + 基础薄弱
    if mastery.score_trend < 0 and mastery.last_practiced_gap_days > 7:
        return "medium"     # 近期退步 + 长期未练
    return "low"
```

#### A/B 实验框架（Phase 7 收尾）

在 `Student` 模型新增 `engine_variant` 字段：

```python
engine_variant = Column(String, default="default")
# 可选值："default" | "mastery_v2" | "experimental"
```

引擎根据 `student.engine_variant` 选择对应的选题策略，支持对不同学生使用不同算法版本。

#### Phase 7 实施步骤

1. Mastery 模型迁移：新增 `last_n_results` / `score_trend` / `confidence` 字段
2. `mastery_service.py` 实现 `compute_mastery_score()` 滑动窗口逻辑
3. `event_processor.py` 中替换旧公式
4. 引擎中新增 `skill_risk_level` 计算
5. 家长端 API 暴露 `risk_level` 字段
6. iOS 家长页接入风险预警展示
7. `Student.engine_variant` 字段 + 引擎分支逻辑

---

## 九、学生状态持久化机制

> 本节记录系统"记忆"的完整数据架构，供 Phase 7 数据模型升级参考。

### 存储层

系统无内存缓存，所有学生状态持久化在单一 SQLite 文件（生产切 PostgreSQL）：

```
services/api/mathcoach.db   ← 所有"记忆"的唯一来源
```

`DATABASE_URL` 环境变量为空时自动 fallback SQLite（`config.py:8`）。API 本身完全无状态，每次请求重新查库。

### 六张表 = 六类记忆

| 表 | 职责 | 读写模式 |
|----|------|---------|
| `students` | 身份 + 聚合行为状态（streak、总场次） | 每次答题后更新 |
| `events` | 原始答题日志 | Append-only，永不修改 |
| `mastery` | 每个技能的掌握度快照（per student × skill） | 每次答题后更新 |
| `daily_sessions` | 每日目标进度（per student × date） | 每次答题后更新 |
| `achievements` | 已解锁徽章 | 只增不减 |
| `items` | 题库内容 | 只读（题目生成时写入） |

### 一次答题触发的完整状态更新链

```
POST /api/v1/events
  │
  ├─ 1. 写 events 表（原始记录，永久保留）
  │       student_id, item_id, is_correct, time_spent, timestamp
  │
  ├─ 2. 更新 students 表（聚合状态）
  │       current_streak  ← 今天 vs last_practice_date 推算
  │       longest_streak  ← max(当前, 历史)
  │       last_practice_date ← 今天
  │       total_sessions += 1
  │
  ├─ 3. 更新 mastery 表（per student × per skill）
  │       total_attempts += 1
  │       correct_attempts += 1  (if correct)
  │       mastery_score = correct_attempts / total_attempts   ← Phase 7 升级此处
  │       last_updated = now()
  │
  ├─ 4. 更新 daily_sessions 表（per student × per date）
  │       completed_questions += 1
  │       is_completed = True  (if >= target)
  │
  └─ 5. 检查 achievements（条件满足 → 写 achievements 表）
          streak_3 / streak_7 / daily_goal_1 / sessions_20
```

### 引擎选题时的状态读取链

```
GET /api/v1/next-item?student_id=jon_zhao
  │
  └─ engine/adaptive.py
        │
        ├─ 读 mastery 表 → 找 mastery_score 最低的 skill_id（弱项优先）
        ├─ 读 mastery 表 → 该 skill 当前难度（score 分段映射 1-5）
        ├─ 读 events 表 → 最近 3 次该 skill 的答题结果（streak 调整）
        │       全对 3 次 → difficulty +1
        │       连错 2 次 → difficulty -1
        └─ 读 items 表 → 匹配 skill_id + difficulty 随机取一题
```

### Phase 7 升级的核心动因

当前 `mastery_score = correct_attempts / total_attempts` 存在时间盲区：

```
场景：Jon 三个月前做了 20 题对 16 题 → mastery_score = 0.80
      Jon 今天做了 5 题全错           → mastery_score = 16/25 = 0.64  ← 仍偏高
      引擎看到 0.64，选难题，但 Jon 今天状态很差
```

Phase 7 通过新增 `last_n_results`（滑动窗口）字段解决此问题，
使 `mastery_score` 同时反映**历史积累**和**近期表现**。

---

## 十、Phase 8：多租户认证系统（商业化扩展前提）

> 当前系统为单家庭硬编码模式（Jon / Astrid）。
> Phase 8 目标：任意家长可注册账号、绑定子女、登录后仅能看到自己家庭的数据。

### 8.1 核心需求

- 家长注册（email + password）
- 家长登录 → 获取 JWT token（role: `parent`）
- 家长账号下注册 1-N 个学生，学生可单独登录（role: `student`）
- **角色隔离：学生登录后只能访问做题接口，无法访问任何家长视图**
- 所有 API 需携带 token，且数据严格隔离到当前家长名下
- iOS 客户端：登录页区分家长/学生入口，界面根据角色自动适配

### 8.2 角色权限模型

系统有且仅有两种角色，权限严格分离：

| 角色 | 登录凭证 | 可访问 | 不可访问 |
|------|---------|--------|---------|
| `parent` | email + password | 全部接口（包括家长仪表盘） | — |
| `student` | student_id + PIN | 做题接口（`/next-item`、`/events`、`/mastery`、`/achievements`、`/streak`） | `/parent/*` 全部接口 |

**JWT payload 中携带角色：**

```python
payload = {
    "sub": identity_id,     # parent_id 或 student_id
    "role": "parent",       # 或 "student"
    "exp": ...,
}
```

**路由层守卫设计：**

```python
# dependencies.py

async def require_parent(token = Depends(oauth2_scheme), db = Depends(get_db)) -> Parent:
    """只允许 role=parent 的 token 通过"""
    claims = verify_token(token)
    if claims["role"] != "parent":
        raise HTTPException(status_code=403, detail="仅家长可访问")
    return get_parent(db, claims["sub"])

async def require_student(token = Depends(oauth2_scheme), db = Depends(get_db)) -> Student:
    """只允许 role=student 的 token 通过，且学生只能访问自己的数据"""
    claims = verify_token(token)
    if claims["role"] != "student":
        raise HTTPException(status_code=403, detail="需要学生身份登录")
    return get_student(db, claims["sub"])
```

**路由注解：**

```python
# 家长专属接口 —— 学生 token 调用直接 403
@router.get("/parent/daily-summary")
async def get_daily_summary(parent = Depends(require_parent)):
    ...

# 学生专属接口 —— 且学生只能查自己的数据
@router.get("/next-item")
async def get_next_item(student = Depends(require_student)):
    ...

# 学生接口中禁止接受外部 student_id 参数
# student_id 直接从 token 中取，防止越权查他人数据
```

**iOS 界面隔离：**

```
App 启动
  └─ 检测 token role
        ├─ role = "parent"  → 进入家长主页（学生选择 + 仪表盘 + 报告）
        └─ role = "student" → 直接进做题页（隐藏所有家长入口，TabBar 无家长选项）
```

---

### 8.3 数据模型变更

**新增 `parents` 表：**

```sql
CREATE TABLE parents (
    id          VARCHAR PRIMARY KEY,       -- UUID
    email       VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,        -- bcrypt
    display_name VARCHAR,
    created_at  TIMESTAMP NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE
);
```

**`students` 表新增两列：**

```sql
ALTER TABLE students ADD COLUMN parent_id VARCHAR REFERENCES parents(id);
ALTER TABLE students ADD COLUMN pin_hash  VARCHAR;   -- 学生登录 PIN（4位数，bcrypt）
```

> 迁移策略：现有 Jon / Astrid 记录归入一个默认管理员 parent 账号，不丢数据。

**数据隔离原则：**
- 家长接口：所有查询必须带 `student.parent_id = current_parent.id` 过滤
- 学生接口：`student_id` 从 token 中提取，**不接受客户端传入的 `student_id` 参数**，防越权

### 8.3 新增认证模型

```
services/api/app/
├── auth/
│   ├── __init__.py
│   ├── schemas.py        ← ParentRegister / ParentLogin / TokenResponse
│   ├── hashing.py        ← bcrypt 密码哈希
│   ├── jwt.py            ← JWT 签发 / 验证 / 刷新
│   └── dependencies.py   ← get_current_parent() FastAPI 依赖注入
├── routers/
│   └── auth.py           ← 新增认证路由
├── models/
│   └── parent.py         ← Parent ORM 模型
```

### 8.5 认证 API 端点

```
# 家长认证
POST /api/v1/auth/register          # 家长注册（email + password）
POST /api/v1/auth/login             # 家长登录 → JWT(role=parent)
POST /api/v1/auth/refresh           # 刷新 token
POST /api/v1/auth/logout            # 登出

# 学生认证（由家长设置 PIN，学生用 PIN 登录）
POST /api/v1/auth/student-login     # 学生登录（student_id + PIN）→ JWT(role=student)

# 学生管理（需家长 token）
POST /api/v1/students               # 注册新学生，归属当前家长
PUT  /api/v1/students/{id}/pin      # 家长为学生设置/重置 PIN
GET  /api/v1/students               # 返回当前家长名下所有学生
```

所有现有接口改为必须携带 `Authorization: Bearer <token>`，路由依赖注入根据 `role` 决定权限。

### 8.5 JWT 方案设计

```python
# jwt.py
TOKEN_EXPIRE_MINUTES = 60 * 24 * 7   # 7 天（移动端常驻）

def create_access_token(parent_id: str) -> str:
    payload = {
        "sub": parent_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

# dependencies.py
async def get_current_parent(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Parent:
    parent_id = verify_token(token)
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if not parent or not parent.is_active:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return parent
```

### 8.6 路由层改造示例

```python
# 改造前
@router.get("/parent/daily-summary")
async def get_parent_daily_summary(db: Session = Depends(get_db)):
    students = db.query(Student).all()   # ← 返回所有学生，不安全

# 改造后
@router.get("/parent/daily-summary")
async def get_parent_daily_summary(
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent),   # ← 必须登录
):
    students = db.query(Student).filter(
        Student.parent_id == current_parent.id              # ← 数据隔离
    ).all()
```

### 8.7 iOS 客户端变更

**新增页面：**
- `AuthView.swift` — 登录 / 注册页（email + password）
- `RegisterStudentView.swift` — 添加学生页（姓名、年级、头像）

**Token 管理：**
- 登录成功后 token 存入 `Keychain`（非 UserDefaults，安全存储）
- 每次 API 请求 header 自动携带 `Authorization: Bearer <token>`
- token 过期 → 自动跳转登录页

**入口流程变更：**
```
App 启动
  ├─ Keychain 有有效 token → 直接进学生选择页
  └─ 无 token / 已过期   → 显示登录页
                              ├─ 登录成功 → 学生选择页
                              └─ 注册成功 → 添加学生页 → 学生选择页
```

### 8.8 新增配置项

`config.py` 新增：

```python
secret_key: str = "change-me-in-production"   # JWT 签名密钥
token_expire_minutes: int = 60 * 24 * 7
```

生产部署必须通过环境变量 `SECRET_KEY` 覆盖。

### 8.9 实施步骤

1. 创建 `models/parent.py`，执行数据库迁移（`students.parent_id`）
2. 创建 `auth/` 模块（hashing + jwt + dependencies）
3. 创建 `routers/auth.py`（register / login / refresh）
4. 改造所有现有路由 → 注入 `get_current_parent`，查询加 `parent_id` 过滤
5. 迁移现有 Jon / Astrid 数据到默认 parent 账号
6. `config.py` 新增 `secret_key`，requirements.txt 新增 `python-jose[cryptography]`、`passlib[bcrypt]`
7. iOS 新增 AuthView + Keychain token 管理 + APIClient header 注入
8. 全量 pytest 回归（新增认证相关测试）

### 8.10 安全要点

| 项目 | 要求 |
|------|------|
| 家长密码存储 | bcrypt，cost factor ≥ 12 |
| 学生 PIN 存储 | bcrypt（同上，4 位数 PIN 也不得明文存储） |
| JWT 密钥 | 环境变量注入，不得出现在代码或 git 中 |
| token 存储（iOS） | Keychain（非 UserDefaults） |
| 角色隔离 | `role=student` 的 token 调用 `/parent/*` 直接 403，不做业务处理 |
| student_id 来源 | 学生接口中 `student_id` 只从 token 取，禁止从请求参数读取 |
| 数据隔离 | 家长接口所有查询必须带 `parent_id` 过滤，禁止全表扫描 |
| HTTPS | 生产环境强制 HTTPS，token 不得明文传输 |
| 密码重置 | Phase 8.5 处理（需邮件服务），本 Phase 暂不实现 |
| PIN 重置 | 家长登录后可随时为学生重置 PIN，学生无法自行修改 |

---

## 十一、Phase 8.5：家长上下文输入 × AI 学生状态融合

> 系统当前的学生状态完全来自答题日志（定量数据）。
> 但真实的学习状态是混合的：孩子今天很累、刚考完试、最近课堂主题变了——这些家长知道，系统不知道。
> Phase 8.5 目标：让家长向系统输入真实场景，AI 将定性观察与定量数据融合，形成更完整的学生画像。

### 核心设计思路

```
当前系统对学生的理解：
  mastery_score + streak + recent_events = 定量快照

Phase 8.5 之后：
  定量快照 + 家长上下文 → AI 综合解读 → 更准确的状态判断
```

两种信息的本质区别：

| 类型 | 来源 | 例子 |
|------|------|------|
| 定量 | 答题日志 | 最近 5 题对 2 题，mastery 下滑 |
| 定性 | 家长输入 | "今天期末考试刚结束，他很累" |

只有定量：引擎看到成绩下滑 → 降难度，但不知道是"累"还是"没学会"
定量 + 定性：AI 知道是考试疲劳 → 今天轻松练，明天正常恢复

---

### 8.5.1 家长上下文输入设计

**结构化 + 自由文本混合输入：**

```
家长今日情况备注（可选填写）：

场景标签（多选）：
  □ 今天很累 / 情绪不好
  □ 刚结束考试 / 测验
  □ 刚放假回来 / 长期未练
  □ 学校本周重点：___________
  □ 孩子说某个知识点不懂：___________
  □ 其他：___________

自由补充（可选）：
  [                              ]
```

**iOS 入口：** 家长仪表盘顶部 "今日情况" 卡片（每日可填一次，非强制）

---

### 8.5.2 数据模型

**新增 `parent_context_events` 表：**

```sql
CREATE TABLE parent_context_events (
    id            VARCHAR PRIMARY KEY,
    parent_id     VARCHAR REFERENCES parents(id),
    student_id    VARCHAR REFERENCES students(id),
    event_date    DATE NOT NULL,
    tags          JSON,           -- ["tired", "post_exam", "school_focus:fractions"]
    free_text     TEXT,           -- 家长自由输入
    ai_summary    TEXT,           -- AI 处理后的摘要（异步生成）
    created_at    TIMESTAMP NOT NULL
);
```

---

### 8.5.3 AI 融合处理流程

```
家长提交上下文
  │
  ├─ 1. 存入 parent_context_events 表
  │
  ├─ 2. 异步触发 AI 处理（调用 Claude API）
  │       输入：
  │         - 家长上下文（tags + free_text）
  │         - 学生近 7 天定量数据：
  │             mastery_score per skill
  │             recent accuracy trend
  │             streak status
  │             time_spent 变化
  │       输出（结构化）：
  │         - state_summary: "Jon 今天可能处于考试后疲劳状态，建议轻量练习"
  │         - engine_hint:   "reduce_difficulty" | "focus_skill:fractions" | "normal"
  │         - risk_flags:    ["post_exam_fatigue", "skill_gap:division"]
  │
  └─ 3. 写回 ai_summary 字段，engine_hint 影响今日选题
```

**AI Prompt 结构（`services/api/app/services/context_ai_service.py`）：**

```python
SYSTEM_PROMPT = """
你是一个儿童数学学习顾问。
你会收到两类信息：
1. 家长对孩子今日状态的描述（定性）
2. 系统记录的孩子近期学习数据（定量）

请综合这两类信息，输出：
- 对孩子当前学习状态的简短判断（1-2句，用于给家长看）
- 今日选题建议（reduce_difficulty / normal / focus_skill:<skill_id> / light_review）
- 需要关注的风险标签列表

输出为 JSON 格式。
"""
```

---

### 8.5.4 对自适应引擎的影响

AI 输出的 `engine_hint` 作为**今日软性约束**传入引擎：

```python
# adaptive.py 中，select_next_item 新增可选参数
def select_next_item(
    db: Session,
    *,
    student_id: str,
    skill_id: Optional[str] = None,
    engine_hint: Optional[str] = None,   # 来自今日 AI 分析
) -> Optional[SelectionResult]:

    if engine_hint == "reduce_difficulty":
        # 今日最大难度 cap 为 base_difficulty - 1
        ...
    elif engine_hint and engine_hint.startswith("focus_skill:"):
        target_skill = engine_hint.split(":")[1]
        # 优先选该 skill 的题目
        ...
    elif engine_hint == "light_review":
        # 只出已掌握（mastery > 0.7）技能的低难度复习题
        ...
```

引擎规则优先级：`custom_track` > `engine_hint` > 正常自适应逻辑

---

### 8.5.5 家长端展示

**家长仪表盘新增 "AI 今日洞察" 卡片：**

```
┌─────────────────────────────────────────┐
│  🤖 AI 今日洞察                          │
│                                         │
│  Jon                                    │
│  "考试后第一天，建议轻量练习。            │
│   分数类题目近期正确率下滑，             │
│   明后天可重点巩固。"                    │
│                                         │
│  📌 今日引擎模式：轻量复习               │
│  ⚠️  关注：yr4_frac_equiv（掌握度 42%）  │
│                                         │
│  [更新今日情况]                          │
└─────────────────────────────────────────┘
```

---

### 8.5.6 隐私与控制原则

| 原则 | 实现 |
|------|------|
| 家长输入完全可选 | 不填时系统正常运行，无 AI 融合 |
| AI 仅辅助，不替代 | `engine_hint` 为软性建议，引擎可忽略（无匹配题目时 fallback 正常逻辑） |
| 家长数据不跨家庭 | `parent_context_events` 按 `parent_id` 严格隔离 |
| 输入不存储敏感信息 | 提示家长不要输入医疗、个人身份等敏感内容 |
| 可随时删除 | 家长可删除任意日期的上下文记录 |

---

### 8.5.7 实施步骤

1. 创建 `parent_context_events` 表和 ORM 模型
2. 新增 `POST /api/v1/parent/context` 接口（接收 tags + free_text）
3. 创建 `services/context_ai_service.py`（调用 Claude API，返回结构化分析）
4. `adaptive.py` 新增 `engine_hint` 参数支持
5. `GET /api/v1/parent/daily-summary` 返回中附加 `ai_insight` 字段
6. iOS 家长页新增 "今日情况" 输入卡片 + "AI 洞察" 展示卡片
7. 新增 `ANTHROPIC_API_KEY` 配置项，requirements.txt 添加 `anthropic`

---

## 十二、完整升级路线图

```
Phase 0-6  ✅ 功能验证完成
              ↓
Phase 6.5  ✅ 架构固化（已完成）
           - 引擎协议 / 服务层 / 插件化 / CORS / 测试
              ↓
Phase 7    🔵 掌握度引擎升级（进行中）
           - 滑动窗口公式
           - 时间衰减
           - 风险检测
           - A/B 实验框架
              ↓
Phase 8    🟡 多租户认证系统（收口中，待签字）
           - 家长注册 / 登录 / JWT
           - 角色隔离（学生看不到家长页）
           - 学生 PIN 登录
           - 数据安全加固
              ↓
Phase 8.5  ⬜ 家长上下文 × AI 状态融合
           - 家长输入真实场景（标签 + 自由文本）
           - AI 融合定性 + 定量数据
           - engine_hint 软性影响选题
           - 家长端 AI 洞察卡片
              ↓
Phase 9    ⬜ 预测引擎（未来）
           - Skill 依赖图
           - 学习轨迹预测
           - 家长智能预警
           - 多学生横向分析
```

> 教育科学融合贯穿全链路：ZPD + 心流检测 → Phase 7；间隔重复调度 → Phase 7.5；SDT 自主选域 + 成长型思维文案 → Phase 8；元认知自评 + 生态系统上下文融合 → Phase 8.5；文化响应式题目标签 → Phase 9。

**当前阶段判断：**
Phase 6.5 架构固化已完成，系统进入 Phase 7 掌握度引擎升级。
Phase 8 多租户认证是商业化扩展的硬性前提，需在对外开放注册前完成。
Phase 8.5 是本系统从"数据驱动"升级为"数据 + 人类洞察双驱动"的关键节点。

---

## 十三、现代教育科学融合框架

> 核心原则：学习路径分析不应只靠答对率数字，必须结合教育学、心理学、社会学的理论基础，让系统真正理解"这个孩子为什么会卡在这里"。

---

### 13.1 教育心理学理论映射

#### 维果茨基最近发展区（ZPD）
**理论：** 学生的最优学习区间在"独立能力上限"与"有帮助时能达到的上限"之间。

| 区域 | 系统判断标准 | 引擎行为 |
|------|------------|---------|
| 挫败区（太难） | 近 5 题正确率 < 40%，且 time_spent 持续偏高 | 强制回退到前置技能，触发"脚手架" hint |
| ZPD（最优） | 近 5 题正确率 50%–80% | 维持当前难度，加入变式题（同技能，换题型） |
| 舒适区（太简） | 近 10 题正确率 > 90%，time_spent 持续偏低 | 加速升档，推送"挑战题"（difficulty +1）|

```python
# engine/zdp_detector.py 新增模块
def detect_zpd_zone(recent_events: list[Event]) -> Literal["frustration", "zpd", "comfort"]:
    accuracy = sum(e.is_correct for e in recent_events) / len(recent_events)
    avg_time = sum(e.time_spent for e in recent_events) / len(recent_events)
    if accuracy < 0.4:
        return "frustration"
    elif accuracy > 0.9 and avg_time < FAST_THRESHOLD:
        return "comfort"
    return "zpd"
```

---

#### 艾宾浩斯遗忘曲线 + 间隔重复（Spaced Repetition）
**理论：** 记忆随时间指数衰减；在遗忘前复习，可最大化长期记忆效率。

**现状问题：** 系统目前无"复习调度"概念，掌握后的技能从不再主动推送复习题。

**计划实现：**

```
mastery 表新增字段：
  next_review_at  DateTime   -- 下次复习推荐时间
  review_interval  Integer   -- 当前复习间隔（天）

复习间隔计算（SM-2 算法简化版）：
  首次掌握（mastery_score >= 0.8）：next_review = now + 1 天
  第 2 次复习通过：interval = 3 天
  第 3 次复习通过：interval = 7 天
  第 4 次复习通过：interval = 16 天（指数增长）
  复习失败：interval 重置为 1 天
```

**引擎选题逻辑新增复习优先队列：**
1. 先检查 `next_review_at <= now` 的技能（复习队列优先）
2. 再选 ZPD 区间内的新进阶题
3. 最后选强化练习题

---

#### 认知负荷理论（Cognitive Load Theory）
**理论：** 工作记忆容量有限；题目中的"无效认知负荷"会干扰真正的数学学习。

**系统应用：**

| 负荷类型 | 表现 | 系统干预 |
|---------|------|---------|
| 内在负荷过高 | 多步骤题 + 低掌握度 | 拆解为单步子题，按步骤解锁 |
| 外在负荷 | 题目文字过长/布局混乱 | content layer 标记 `complexity_level`，引擎过滤 |
| 相关负荷（有益） | 同技能多表征（图形/数字/文字） | 变式题系统支持 `representation_type` 字段 |

---

#### 刻意练习（Deliberate Practice）
**理论：** 进步来自在舒适区边缘的有目的训练，而非重复完成简单题。

**计划：**
- 识别学生的"拖延回避技能"（long_idle_skills：10天未练习但 mastery < 0.7）
- 家长看板标注"待突破技能"，引擎每天强制插入 1-2 道回避技能的练习题

---

### 13.2 心理学理论映射

#### 自我决定理论（Self-Determination Theory，SDT）
**理论（Deci & Ryan）：** 内在动机由三个心理需求驱动：
- **自主感（Autonomy）**：感到自己有选择权
- **能力感（Competence）**：感到在进步，能胜任
- **归属感（Relatedness）**：感到被认可和连接

| 需求 | 系统设计响应 |
|------|------------|
| 自主感 | 每日开始时提供 "今天想练什么领域？" 选项（软性选择，不影响核心推荐） |
| 能力感 | 连续答对 3 题时触发"进步提示"动画；掌握新技能触发成就徽章 |
| 归属感 | 家长每日收到孩子进步摘要；AI 洞察卡片使用温暖语气 |

---

#### 成长型思维（Growth Mindset，Dweck）
**理论：** 相信能力可以通过努力提升的学生比相信能力固定的学生更能抵抗失败。

**系统设计原则：**
- ❌ 避免：显示"错误次数"累计计数
- ✅ 推荐：显示"今天尝试了 N 道新题型"
- ❌ 避免：按绝对分数排名（伤害自我效能感）
- ✅ 推荐：按个人进步幅度展示（"本周比上周提升 15%"）
- 错题提示文案使用成长语言：
  ```
  "这道题很有挑战性！让我们看看哪里可以换个思路..."
  而非："你答错了。"
  ```

---

#### 心流理论（Flow State，Csikszentmihalyi）
**理论：** 最佳学习状态出现在"挑战 ≈ 能力"时，既不无聊也不焦虑。

**与 ZPD 联动：** ZPD 区间即心流区间的数学近似。系统目标是让学生始终待在心流区。

**检测信号（来自行为数据）：**
```
心流状态指标：
  - 连续答题无中断（session_gap < 30秒）
  - time_spent 稳定（不飙高也不过快）
  - 正确率 60-80%

心流破坏信号：
  - 突然 time_spent > 3×平均（卡住了）
  - 连续 > 2 次 hint_requested（放弃信号）
  - 答题间隔突增（分心/沮丧）
```

---

#### 元认知培养
**理论：** 能监控和调节自己学习过程的学生，长期学业表现更好。

**系统设计：**
- 每完成 10 题后，展示"今日表现回顾"（学生自评卡）：
  - "今天哪道题让你最困惑？"（帮助识别元认知盲点）
  - "你觉得今天的难度合适吗？"（自主感 + 元认知）
- 家长端展示 AI 分析："根据行为数据，孩子在分数加法上出现了理解断层，建议..."

---

### 13.3 社会学理论映射

#### 布朗芬布伦纳生态系统理论（Bronfenbrenner）
**理论：** 儿童的学习深受多层社会环境影响：微系统（家庭）→ 中系统（家校互动）→ 外系统（父母工作压力）→ 宏系统（文化背景）。

**系统响应：**

| 环境层 | 家长可输入的上下文 | AI 如何利用 |
|--------|-----------------|-----------|
| 微系统 | "今天家里有客人，孩子很兴奋" | 降低当日目标题数；选更趣味性题型 |
| 微系统 | "孩子刚和弟弟吵架" | 识别情绪负向状态，引擎降低难度阈值 |
| 外系统 | "我今天工作很忙，孩子独立完成" | 提高 hint 容忍度，避免挫败感堆积 |
| 宏系统 | 时区/文化背景（未来） | 题目场景本地化（货币单位、单位制等） |

---

#### 社会比较理论（Social Comparison）
**理论：** 人们通过与他人比较来评估自己；向上比较激励但也伤害自尊，向下比较可临时提振自信但无法持续激励。

**设计原则：**
- 家长端**不显示学生间横向排名**
- 只展示"个人历史进步曲线"（纵向自我比较）
- 若未来引入多孩子家庭，Jon 和 Astrid 的数据只对各自家长可见，不交叉显示

---

#### 文化响应式教学（Culturally Responsive Teaching）
**理论：** 学习材料应与学生的文化背景和生活经验相连，提高内在相关性。

**系统实现路径：**
```
Item 模型新增字段：
  context_theme: str  # "shopping" | "cooking" | "sports" | "nature" | "science"
  locale_tags: list[str]  # ["us", "cn", "generic"]

引擎选题时，参考家长设置的 family_context.interests
例：家长标注 "孩子喜欢篮球" → 优先推送 context_theme="sports" 的题目
```

---

### 13.4 理论 → 系统模块映射总表

| 理论 | 来源学科 | 对应系统模块 | 实现优先级 |
|------|---------|------------|----------|
| 最近发展区（ZPD） | 教育心理学 | `engine/zpd_detector.py` | 🔴 Phase 7 集成 |
| 遗忘曲线 + 间隔重复 | 教育心理学 | `mastery` 表 + 复习调度器 | 🟠 Phase 7.5 |
| 认知负荷理论 | 教育心理学 | `Item.complexity_level` + 引擎过滤 | 🟠 Phase 7.5 |
| 刻意练习 | 教育心理学 | 回避技能检测 + 每日强制插入 | 🟡 Phase 8 |
| 自我决定理论 | 心理学 | 每日选域选项 + 成就语气设计 | 🟡 Phase 8 |
| 成长型思维 | 心理学 | 文案系统 + 进步幅度展示 | 🟡 Phase 8 |
| 心流理论 | 心理学 | 行为信号检测 + ZPD 联动 | 🔵 Phase 7 |
| 元认知培养 | 心理学 | 课后自评卡 + AI 学习分析 | 🟡 Phase 8.5 |
| 生态系统理论 | 社会学 | 家长上下文融合（Phase 8.5） | 🟠 Phase 8.5 |
| 社会比较理论 | 社会学 | 数据隔离设计 + 纵向进步图 | 🟢 设计原则（即时生效） |
| 文化响应式教学 | 社会学 | `Item.context_theme` + 兴趣标签 | 🟡 Phase 9 |

---

### 13.5 Phase 7 教育科学集成行动项

在 Phase 7（掌握度引擎升级）中，立即集成以下内容：

**7.1 ZPD 区间检测器**
```python
# 在 SelectionRequest 中新增 zpd_zone 字段
@dataclass
class SelectionRequest:
    student_id: str
    skill_id: str | None
    recent_events: list[Event]
    zpd_zone: Literal["frustration", "zpd", "comfort"] | None = None
    flow_signal: Literal["flow", "stuck", "bored"] | None = None
    engine_hint: str | None = None
```

**7.2 心流信号检测**
```python
# services/flow_detector.py
def detect_flow_signal(recent_events: list[Event]) -> Literal["flow", "stuck", "bored"]:
    if len(recent_events) < 3:
        return "flow"
    avg_time = mean(e.time_spent for e in recent_events)
    hint_rate = sum(e.hint_requested for e in recent_events) / len(recent_events)
    if hint_rate > 0.5 or avg_time > STUCK_THRESHOLD:
        return "stuck"
    if avg_time < BORED_THRESHOLD and all(e.is_correct for e in recent_events[-5:]):
        return "bored"
    return "flow"
```

**7.3 间隔重复调度字段（mastery 表迁移）**
```sql
ALTER TABLE mastery ADD COLUMN next_review_at TIMESTAMP;
ALTER TABLE mastery ADD COLUMN review_interval_days INTEGER DEFAULT 1;
ALTER TABLE mastery ADD COLUMN review_streak INTEGER DEFAULT 0;
```

---

### 13.6 成长型思维文案系统

所有面向学生的文案，遵循以下原则：

```
✅ 过程导向语言：
  "你在这道题上花了很多心思！"
  "再试一次——你上次做类似题时进步了很多。"
  "这个技能有点难，但你已经做对了 3 道相关题！"

❌ 结果导向语言（避免）：
  "你做错了。"
  "你今天只对了 4 道题。"
  "你比昨天差。"

✅ 家长端 AI 洞察语气：
  "Jon 今天在分数加法上遇到了困难，但尝试次数增加了 ——说明他没有放弃。
   建议明天先从更简单的同分母加法开始热身。"
```

---

> **核心设计哲学：**
> 数字（答对率、掌握分数）只是观测信号，不是目标本身。
> 系统的真正目标是：在每个孩子的最近发展区内，用间隔重复构建长期记忆，
> 用成长型思维文案保护内在动机，用生态系统视角理解情境变化——
> 让 AI 成为真正理解孩子的"第二个家长"，而不是一个刷题机器。

---

## 十四、可验收标准与 QA 门禁体系

> **角色定位：** 本节由交付负责人/QA 架构师维护。
> 所有 Phase 必须通过本节对应的 DoD 清单，方可关闭该阶段并推进下一阶段。
> "完成" ≠ "可验收"；只有全部 ✅ 才算交付关闭。

---

### 14.0 全局验收原则

| 原则 | 说明 |
|------|------|
| **可复现** | 每条验收项必须可在本地/CI 环境独立复现，不依赖手动操作或特定数据 |
| **二元判定** | 每条 DoD 只有 ✅ 通过 / ❌ 未通过，不存在"部分通过" |
| **不破坏已有** | 每次 Phase 关闭前必须跑全量回归，无新增失败用例 |
| **数据安全门禁** | 含认证/权限变更的 Phase，必须通过安全清单全部项才可放行 |
| **教育科学对齐** | Phase 7+ 的引擎变更，必须附带行为验证（不仅是单元测试） |

---

### 14.1 Phase 6.5 验收基线（历史归档）

> 已完成。此节为后续 Phase 的回归基准。

**DoD — 必须永久保持（每次发布前自动验证）：**

- [ ] `pytest services/api/tests/` 全量通过（≥ 18 用例，零失败）
- [ ] `POST /api/v1/events` 接受合法事件，返回 `200`，写入 DB
- [ ] `GET /api/v1/next-item` 返回含 `skill_id + difficulty + item_id` 的结构化 JSON
- [ ] `SelectionRequest / SelectionResult` dataclass 边界存在于 `engine/protocol.py`，路由层无直接 DB 写入
- [ ] CORS origins 来自 `settings.cors_origins`，代码中无硬编码 `"*"`
- [ ] 引擎不含 `JON_STUDENT_ID` / `ASTRID_STUDENT_ID` 硬编码常量

---

### 14.2 Phase 7 验收标准

**目标：** 掌握度引擎升级 — 滑动窗口 + 时间衰减 + 风险检测

#### DoD 清单

| # | 验收项 | 验证方式 |
|---|--------|---------|
| 7-1 | `mastery.last_n_results` 字段存在，每次答题后正确更新（保留最近 N 次） | `pytest test_mastery_sliding_window` |
| 7-2 | 时间衰减生效：3 个月前的答题记录权重 < 上周记录权重（可量化） | `pytest test_mastery_time_decay` |
| 7-3 | 连续 3 次错误后，`skill_risk_level` 升至 `"high"`，家长 API 返回预警字段 | `pytest test_risk_level_escalation` |
| 7-4 | ZPD 区间检测：正确率 < 40% → `zpd_zone = "frustration"`，引擎降档 | `pytest test_zpd_frustration_zone` |
| 7-5 | ZPD 区间检测：正确率 > 90% 且 time_spent 低 → `zpd_zone = "comfort"`，引擎升档 | `pytest test_zpd_comfort_zone` |
| 7-6 | 心流信号检测：hint 使用率 > 50% → `flow_signal = "stuck"` | `pytest test_flow_detector_stuck` |
| 7-7 | `mastery_score` 仍在 [0, 1] 区间内（无公式越界） | 全量 events fixture 跑 score assertion |
| 7-8 | 全量回归：Phase 6.5 基线 18 用例全部通过 | `pytest --tb=short` |

#### 行为验收（非单元测试，需人工确认）

```
场景 A — 时间遗忘恢复：
  1. 用 seed 脚本写入 Jon 3 个月前 20 题（16 对）
  2. 再写入今日 5 题（全错）
  3. 调用 GET /mastery/jon_zhao，score 应 < 0.5（明显低于 0.64）
  ✅ 预期：time-decayed score 反映近期退步

场景 B — 风险预警链路：
  1. 连续 POST 3 次错误事件（同一 skill）
  2. 调用 GET /parent/daily-summary
  3. 响应中 risk_skills 包含该 skill_id
  ✅ 预期：家长端可见预警信号
```

#### Phase 7 → Phase 8 放行条件

> 所有 DoD 7-1 ～ 7-8 均 ✅，且行为验收场景 A、B 通过，方可开启 Phase 8。

---

### 14.3 Phase 8 验收标准（当前进行中）

**目标：** 多租户认证 — 家长注册/登录、学生 PIN、角色隔离、数据安全

#### DoD 清单

| # | 验收项 | 验证方式 |
|---|--------|---------|
| 8-1 | `POST /auth/register`：新家长注册，密码 bcrypt 存储，返回 201 | `pytest test_parent_register` |
| 8-2 | `POST /auth/login`：正确密码返回 JWT；错误密码返回 401 | `pytest test_parent_login_success` + `test_parent_login_wrong_pw` |
| 8-3 | JWT payload 含 `role: "parent"` / `"student"` 字段 | `pytest test_jwt_role_payload` |
| 8-4 | `GET /parent/students`：只返回当前 token 家长的学生，不泄露他人数据 | `pytest test_parent_data_isolation` |
| 8-5 | `role=student` 的 token 调用 `GET /parent/daily-summary` → 403 | `pytest test_student_cannot_access_parent_route` |
| 8-6 | `role=parent` 的 token 调用 `GET /student/next-item` → 403 | `pytest test_parent_cannot_access_student_route` |
| 8-7 | 学生 PIN 登录：4 位正确 PIN 返回 student JWT；错误 PIN 返回 401 | `pytest test_student_pin_login` |
| 8-8 | 学生接口中 `student_id` 来自 token，不接受 query/body 传入的 student_id | `pytest test_student_id_from_token_only` |
| 8-9 | JWT 密钥来自环境变量 `SECRET_KEY`，代码中无硬编码字符串 | `grep -r "SECRET_KEY" services/api/app/ --include="*.py"` 确认只有 config 引用 |
| 8-10 | bcrypt cost factor ≥ 12（家长密码 + 学生 PIN 均适用） | `pytest test_bcrypt_cost_factor` |
| 8-11 | iOS Keychain 存储 token，无 UserDefaults 使用 | 代码审查：`grep -r "UserDefaults" apps/ios/` 无 token 相关写入 |
| 8-12 | 401 响应触发 iOS 自动跳转登录页，不停留在空白页 | 手动 UI 测试：使 token 过期后操作任意接口 |
| 8-13 | Jon / Astrid 历史数据完整迁移至默认 parent 账号，无数据丢失 | `pytest test_legacy_data_migration` |
| 8-14 | 全量回归：Phase 6.5 + 7 基线用例全部通过 | `pytest --tb=short` |

#### 安全专项验收（必须全部通过，无例外）

| 安全项 | 检查命令 / 方式 | 预期结果 |
|--------|--------------|---------|
| 无明文密码落库 | `SELECT password_hash FROM parents LIMIT 5` | 全为 `$2b$` 开头的 bcrypt 串 |
| 无明文 PIN 落库 | `SELECT pin_hash FROM students LIMIT 5` | 全为 `$2b$` 开头的 bcrypt 串 |
| JWT 密钥不在代码中 | `git grep "hs256\|secret\|my-secret" -- "*.py"` | 0 匹配 |
| 跨家长数据泄露测试 | 用 Parent-A token 请求 Parent-B 的学生 ID | 返回 404 或 403，不返回数据 |
| HTTPS 强制（生产） | 访问 `http://` 端点 | 301 重定向到 `https://` |

#### Phase 8 → Phase 8.5 放行条件

> DoD 8-1 ～ 8-14 全 ✅，且安全专项 5 项全通过。
> 代码审查（code review）必须由第二人确认安全清单无遗漏。

---

### 14.4 Phase 8.5 验收标准

**目标：** 家长上下文输入 × AI 学生状态融合

#### DoD 清单

| # | 验收项 | 验证方式 |
|---|--------|---------|
| 8.5-1 | `POST /parent/context`：保存 tags + free_text，返回 201 | `pytest test_parent_context_create` |
| 8.5-2 | Claude API 调用成功，返回结构化 `engine_hint` 字符串（非空） | `pytest test_context_ai_service_returns_hint` (mock Claude) |
| 8.5-3 | `engine_hint` 写入 `parent_context_events` 表 | DB 查询验证 |
| 8.5-4 | 引擎选题时，`engine_hint = "anxiety"` 使选题难度分布下移（统计验证） | `pytest test_engine_hint_reduces_difficulty` |
| 8.5-5 | `engine_hint` 为 None 时，引擎行为与无 hint 时完全一致（无副作用） | `pytest test_engine_hint_none_no_effect` |
| 8.5-6 | `GET /parent/daily-summary` 响应包含 `ai_insight` 字段（可为空字符串） | `pytest test_daily_summary_has_ai_insight` |
| 8.5-7 | iOS 家长端"今日情况"卡片可提交，提交后出现 AI 洞察文字 | 手动 UI 测试 |
| 8.5-8 | `ANTHROPIC_API_KEY` 缺失时，接口返回 503 而非 500 崩溃 | `pytest test_missing_api_key_graceful_fail` |
| 8.5-9 | 家长不输入上下文时，系统正常运行，不阻塞选题链路 | `pytest test_no_context_engine_unaffected` |
| 8.5-10 | AI 输入内容不持久化到 AI 服务商（本地 DB 存储，合规要求） | 代码审查：确认只调用 Claude API，不上传 student_id |

---

### 14.5 Phase 9 验收标准（预备）

**目标：** 预测引擎 — Skill 依赖图 + 学习轨迹预测 + 智能预警

#### DoD 清单（预定义，实施前可调整）

| # | 验收项 |
|---|--------|
| 9-1 | Skill 依赖图定义完整，每个 skill 有 `prerequisites` 列表 |
| 9-2 | 引擎选题时，前置技能未达标（mastery < 0.6）则不推送进阶题 |
| 9-3 | `GET /parent/forecast` 接口返回未来 7 天推荐练习技能 |
| 9-4 | 预警：连续 3 日回避某技能 → 家长端出现 `"待突破技能"` 标记 |
| 9-5 | 多学生家庭：家长看到两个孩子各自独立进度，数据不混合 |
| 9-6 | 全量回归通过（Phase 6.5 + 7 + 8 + 8.5 基线用例） |

---

### 14.6 教育科学融合验收标准（Section 13 集成）

> 教育科学模块不是独立功能，是引擎行为的**约束层**。验收重点是行为一致性。

| 理论 | 验收项 | Phase | 验证方式 |
|------|--------|-------|---------|
| ZPD | 正确率 < 40% 时引擎不选 difficulty ≥ 3 的题 | 7 | `pytest test_zpd_blocks_hard_items` |
| 间隔重复 | `next_review_at` 到期技能在下次选题中优先出现 | 7.5 | `pytest test_spaced_repetition_priority` |
| 认知负荷 | `complexity_level=3` 的题在 `frustration` 区间被过滤 | 7.5 | `pytest test_cognitive_load_filter` |
| 刻意练习 | 10 天未练习且 mastery < 0.7 的技能被标记为 `avoidance_skill` | 8 | `pytest test_avoidance_skill_detection` |
| SDT 自主感 | 家长端可设置"今日选域偏好"，引擎 soft-weight 对应 skill | 8 | `pytest test_domain_preference_weight` |
| 成长型思维 | API 响应中无"错误次数"字段；只有"尝试次数" | 即时 | `grep -r "wrong_count\|error_count" services/api/` 返回 0 |
| 心流检测 | hint_rate > 50% 时 `flow_signal = "stuck"`，引擎降档 | 7 | `pytest test_flow_stuck_lowers_difficulty` |
| 社会比较 | 家长 API 无跨学生 ranking 字段 | 即时 | `grep -r "rank\|leaderboard" services/api/` 返回 0 |

---

### 14.7 QA Gate 流程

```
                    ┌─────────────────────────────┐
                    │  Phase N 开发完成            │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Step 1: 单元测试全通过       │
                    │  pytest Phase-N 专项测试      │
                    └──────────────┬──────────────┘
                                   │ ✅
                    ┌──────────────▼──────────────┐
                    │  Step 2: 全量回归            │
                    │  pytest（所有历史基线）        │
                    └──────────────┬──────────────┘
                                   │ ✅（零新增失败）
                    ┌──────────────▼──────────────┐
                    │  Step 3: 行为验收场景         │
                    │  手动执行本节定义的场景脚本    │
                    └──────────────┬──────────────┘
                                   │ ✅
                    ┌──────────────▼──────────────┐
                    │  Step 4: 安全/合规检查        │
                    │  （Phase 8+ 必须）           │
                    └──────────────┬──────────────┘
                                   │ ✅
                    ┌──────────────▼──────────────┐
                    │  Step 5: 交付负责人签字关闭   │
                    │  更新进展快照状态 ✅           │
                    └─────────────────────────────┘
```

**Gate 失败处理规则：**
- Step 1/2 失败 → 当前 Phase 不得关闭，修复后重新从 Step 1 开始
- Step 3 失败 → 记录为 Bug，修复后重新从 Step 3 开始（无需重跑 Step 1/2，除非有代码改动）
- Step 4 失败 → **当前 Phase 冻结**，不得进行任何新功能开发，直至安全问题关闭

---

### 14.8 回归测试矩阵

每次 Phase 关闭前，以下核心链路**必须全部人工/自动验证通过**：

| 链路 | 覆盖范围 | 自动化程度 |
|------|---------|-----------|
| **答题链路** | POST /events → mastery 更新 → streak 更新 → daily_session 更新 | 自动（pytest） |
| **选题链路** | GET /next-item → engine 选题 → ZPD 检查 → 返回合法题目 | 自动（pytest） |
| **家长仪表盘** | GET /daily-summary → 聚合数据 → risk_skills → ai_insight | 自动（Phase 8.5 后） |
| **认证链路** | 注册 → 登录 → JWT → 受保护接口 → 角色隔离 → 401 回跳 | 自动（Phase 8 后） |
| **iOS 端到端** | 选题 → 答题 → 结果动画 → 下一题 | 手动（每次发布前） |
| **数据隔离** | 两家长账号互不可见对方数据 | 自动（Phase 8 后） |

---

### 14.9 性能基准

> 以下为系统在**单机本地部署**下的最低性能要求，生产环境应更优。

| 接口 | P50 响应时间 | P99 响应时间 | 说明 |
|------|------------|------------|------|
| `GET /next-item` | < 100ms | < 300ms | 选题是高频操作，直接影响用户体验 |
| `POST /events` | < 150ms | < 400ms | 答题后立即写入，不可有明显卡顿 |
| `GET /parent/daily-summary` | < 500ms | < 1500ms | 包含聚合计算，家长端容忍度较高 |
| `POST /parent/context`（AI 融合） | < 3000ms | < 8000ms | 含 Claude API 调用，异步可接受 |
| 数据库查询（本地 SQLite） | < 50ms | < 200ms | 无全表扫描，所有查询有索引 |

**检测方式：**
```bash
# 本地压测（Phase 关闭前执行）
python -m pytest services/api/tests/test_performance.py -v
# 或用 httpie 手动测量
time http GET localhost:8000/api/v1/next-item student_id==jon_zhao
```

---

### 14.10 上线发布检查清单

> 每次向生产/家人真实设备发布前，逐项确认。

**代码质量**
- [ ] 全量 pytest 通过（零失败）
- [ ] 无 `TODO: remove` / `FIXME` 注释残留在关键路径
- [ ] 无 `print()` 调试输出残留（用 `logging` 替代）
- [ ] `SECRET_KEY` / `ANTHROPIC_API_KEY` 来自环境变量，不在代码中

**数据安全**
- [ ] 所有密码/PIN 均 bcrypt 存储，已验证
- [ ] JWT 密钥已更换（如本次发布涉及认证变更）
- [ ] 跨家庭数据隔离测试通过

**功能回归**
- [ ] Jon 完整答题链路可用（选题 → 答题 → 掌握度更新）
- [ ] Astrid 完整答题链路可用
- [ ] 家长仪表盘可正常加载（含 streak / risk / 日报）
- [ ] 成就解锁链路可用（连续打卡触发徽章）

**iOS 客户端**
- [ ] App 在目标设备冷启动无崩溃
- [ ] 401 过期自动跳转登录页
- [ ] Keychain token 在 App 删除后清除

**数据库**
- [ ] 数据库迁移脚本已执行，无字段缺失
- [ ] Jon / Astrid 历史数据完整（事件数 / mastery 分数与上次一致）
- [ ] 新表有适当索引（`student_id`, `created_at` 等高频查询字段）

**发布后验证（T+5 分钟）**
- [ ] 用真实账号完成 1 次完整答题会话
- [ ] 家长端看到当日进度更新
- [ ] 日志无异常 ERROR/CRITICAL 输出

---

### 14.11 Phase 当前验收状态总览

| Phase | 状态 | DoD 完成度 | 放行签字 |
|-------|------|-----------|---------|
| Phase 0–6 | ✅ 已关闭 | 历史验收通过 | — |
| Phase 6.5 | ✅ 已关闭 | 18 测试通过，架构基线确立 | — |
| Phase 7 | ✅ 已关闭 | 时间衰减 + ZPD + 风险信号已落地 | — |
| Phase 8 | 🟣 进行中 | DoD 8-1～8-14 待逐项确认 | ⏳ 待签字 |
| Phase 8.5 | ⬜ 未开始 | — | — |
| Phase 9 | ⬜ 未开始 | — | — |
| Sec 13 教育科学 | 🔵 集成中 | ZPD/心流/成长型思维文案 随 Phase 7/8 滚动验收 | 随 Phase 滚动 |

> **当前行动项：** 对照 14.3 Phase 8 DoD 清单，逐项确认 Step 1–20 已落地的功能是否满足每条验收标准。未覆盖项补充测试后，执行 QA Gate 五步流程，完成 Phase 8 关闭签字。
