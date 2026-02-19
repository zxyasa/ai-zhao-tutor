# AI Zhao Tutor 升级计划 2026
## 打造：低摩擦、可持续、动态自适应的家庭 AI 数学教练系统

**日期：** 2026-02-18
**服务对象：** Jon、Astrid
**当前完成度：** ~70%（基础框架已就绪）

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
        <string>/Users/michaelzhao/agents/ai-zhao-tutor/services/notes/run_daily.py</string>
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
