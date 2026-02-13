# MathCoach 当前功能状态

**最后更新：** 2026-02-13

## 🎯 项目概述

完整的 AI 数学训练系统，包含后端 API 和 iOS iPad 应用。

---

## ✅ 已完成的功能

### 1. 后端服务（FastAPI + PostgreSQL）

**位置：** `~/agents/ai-zhao-tutor/services/api/`

**功能：**
- ✅ FastAPI 服务器运行在 http://localhost:8000
- ✅ PostgreSQL 数据库（Docker）
- ✅ 健康检查端点：`GET /health`
- ✅ 获取下一题：`GET /api/v1/next-item?student_id=xxx`
- ✅ 提交答案：`POST /api/v1/events`
- ✅ 获取掌握度：`GET /api/v1/mastery/{student_id}`

**数据：**
- 110 道数学题（难度 1-4）
- 3 种题型模板：
  - 分数比较（yr3_frac_compare_001）
  - 等价分数（yr3_frac_equiv_001）
  - 分数加法（yr3_frac_add_001）
- 1 个测试学生：test_001（3年级）

**启动命令：**
```bash
cd ~/agents/ai-zhao-tutor/ops/docker
docker-compose up -d
```

---

### 2. iOS 应用（SwiftUI + MVVM）

**位置：** `~/agents/ai-zhao-tutor/apps/ios/MathCoach/`

#### 2.1 数据模型层（Models/）

**5 个模型文件：**

1. **AnyCodable.swift** - 动态 JSON 类型处理
   - 支持 Int, Double, String, Bool, Array, Dictionary
   - 用于 Item 的 parameters 字段

2. **Student.swift** - 学生档案
   - id, name, yearLevel, createdAt
   - Snake_case 到 camelCase 自动转换

3. **Item.swift** - 数学题目
   - 题目文本、类型、难度
   - 参数、正确答案、提示、解释
   - 验证规则

4. **Event.swift** - 答题事件
   - 学生答案、正确性
   - 耗时、是否使用提示
   - 时间戳

5. **Mastery.swift** - 技能掌握度
   - 总尝试次数、正确次数
   - 掌握分数（0-1）
   - 计算属性：百分比、等级（Beginner/Developing/Proficient/Mastered）

#### 2.2 网络层（Services/）

**APIClient.swift** - 后端通信

**配置：**
- Base URL: `http://192.168.86.63:8000/api/v1`（真实 iPad 用）
- 或 `http://localhost:8000/api/v1`（模拟器用）
- 超时时间：30秒
- ISO8601 日期格式

**方法：**
```swift
// 获取下一题
func fetchNextItem(studentId: String) async throws -> Item

// 提交答案
func submitEvent(_ event: Event) async throws

// 获取掌握度
func getMastery(studentId: String) async throws -> [Mastery]

// 健康检查
func checkHealth() async -> Bool
```

**错误处理：**
- InvalidURL
- NoData
- DecodingError
- ServerError
- NetworkError（带详细提示）

#### 2.3 业务逻辑层（ViewModels/）

**QuestionViewModel.swift** - 主要业务逻辑

**Published 属性：**
- `currentItem` - 当前题目
- `studentAnswer` - 学生答案
- `isLoading` - 加载状态
- `errorMessage` - 错误信息
- `showHint` - 显示提示
- `showExplanation` - 显示解释
- `isCorrect` - 答案正确性
- `timeSpent` - 答题耗时

**核心功能：**
- ✅ 加载下一题
- ✅ 提交答案
- ✅ 答案验证（exact/numeric/fraction）
- ✅ 实时计时器
- ✅ 提示切换
- ✅ 后端健康检查

**答案验证逻辑：**
- `exact` - 精确匹配（忽略大小写和空格）
- `numeric` - 数值比较（误差 < 0.0001）
- `fraction` - 分数比较（如 1/2 == 2/4）

#### 2.4 界面层（Views/）

**QuestionView.swift** - 主界面

**包含 4 个子界面：**

1. **欢迎界面**
   - MathCoach 标题和图标
   - "开始练习" 按钮
   - 自动后端健康检查

2. **答题界面**
   - 顶部：难度显示 + 计时器
   - 中间：题目卡片
   - 答案输入框（支持数字键盘）
   - 底部：显示提示 + 提交答案按钮
   - 黄色提示框（可切换）

3. **结果界面**
   - 大图标（✓ 或 ✗）
   - 对错提示
   - 答案对比（学生答案 vs 正确答案）
   - 详细解释
   - 统计信息（耗时、是否用提示）
   - "下一题" 按钮

4. **错误界面**
   - 错误图标
   - 错误信息
   - "重试" 按钮

**UI 特点：**
- ✅ 渐变背景
- ✅ 卡片阴影效果
- ✅ 响应式布局（iPad 优化）
- ✅ 自动键盘类型切换
- ✅ Submit on Return 支持
- ✅ Loading 状态显示

**ContentView.swift** - 应用入口
- 简单包装 QuestionView

---

## 🔧 技术架构

### 架构模式
- **MVVM**（Model-View-ViewModel）
- **单例模式**（APIClient）
- **依赖注入**（ViewModel 使用 APIClient）

### 并发处理
- **async/await** - 现代 Swift 并发
- **@MainActor** - UI 线程安全
- **Timer** - 计时器（主线程）

### 数据序列化
- **Codable** - JSON 编解码
- **自定义 CodingKeys** - Snake_case 转换
- **ISO8601DateFormatter** - 日期处理

### 网络通信
- **URLSession** - HTTP 请求
- **RESTful API** - 标准 REST 接口
- **JSON** - 数据格式

---

## 📱 部署配置

### 模拟器测试
- 目标设备：iPad Pro 13-inch (M5)
- API 地址：`http://localhost:8000`

### 真实 iPad 测试
- 连接：USB 或 WiFi
- API 地址：`http://192.168.86.63:8000`（Mac IP）
- 签名：Apple ID 自动签名
- 首次需要：设置 → 通用 → VPN与设备管理 → 信任

### ATS 配置
需要在 Info.plist 中允许 HTTP 本地连接：
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```

---

## 🎮 用户体验流程

1. **启动** → 自动检查后端健康
2. **欢迎界面** → 点击"开始练习"
3. **加载题目** → 显示 Loading
4. **答题** → 输入答案，可查看提示
5. **提交** → 验证答案
6. **查看结果** → 对错反馈 + 解释
7. **下一题** → 自动循环

---

## 🔑 关键数据

### 学生
- ID: `test_001`
- 姓名: 测试学生
- 年级: 3

### 题目分布
| 难度 | 数量 |
|------|------|
| 1    | 30   |
| 2    | 30   |
| 3    | 30   |
| 4    | 20   |
| **总计** | **110** |

### 技能类型
- `yr3_frac_compare_001` - 分数比较（同分母）
- `yr3_frac_equiv_001` - 等价分数
- `yr3_frac_add_001` - 分数加法（同分母）

---

## 📂 项目结构

```
~/agents/ai-zhao-tutor/
├── services/
│   ├── api/                    # FastAPI 后端
│   │   ├── app/
│   │   │   ├── models/         # 数据库模型
│   │   │   ├── routers/        # API 路由
│   │   │   └── main.py         # 应用入口
│   │   └── requirements.txt
│   └── content/                # 内容生成
│       ├── generate_items.py   # 题目生成器
│       ├── validate_items.py   # 验证器
│       └── output/
│           ├── skill_tree_v0.json
│           └── content_pack_v0.json
├── apps/
│   └── ios/
│       └── MathCoach/
│           ├── MathCoach.xcodeproj/
│           └── MathCoach/
│               ├── Models/          # 5 个模型
│               ├── Services/        # APIClient
│               ├── ViewModels/      # QuestionViewModel
│               ├── Views/           # QuestionView
│               ├── ContentView.swift
│               └── MathCoachApp.swift
├── ops/
│   └── docker/
│       ├── docker-compose.yml  # Docker 配置
│       └── api.Dockerfile
└── docs/
    ├── CLAUDE.md               # 开发规范
    ├── MAC_SETUP.md            # Mac 环境设置
    └── CURRENT_STATUS.md       # 本文档
```

---

## 🚀 快速启动指南

### 后端启动
```bash
cd ~/agents/ai-zhao-tutor/ops/docker
docker-compose up -d

# 验证
curl http://localhost:8000/health
```

### iOS 启动
```bash
cd ~/agents/ai-zhao-tutor/apps/ios
open MathCoach.xcodeproj

# 在 Xcode 中：
# 1. 选择 iPad 模拟器
# 2. 按 ⌘R 运行
```

---

## 🔜 待开发功能

### 优先级高
- [ ] 家长/教师设置面板（隐藏入口 + 密码保护）
- [ ] 难度范围控制
- [ ] 学习进度追踪
- [ ] 成绩统计报告

### 优先级中
- [ ] 更多题型模板（17 个技能待实现）
- [ ] 技能树可视化
- [ ] 自适应难度算法优化
- [ ] 离线模式支持

### 优先级低
- [ ] 多学生切换
- [ ] 数据导出功能
- [ ] 主题切换（深色模式）
- [ ] 声音效果

---

## 🐛 已知问题

### 需要注意
1. **外键约束** - 需要先创建学生才能提交事件（已解决）
2. **API 端点** - submit-event 改为 events（已修复）
3. **IP 地址** - 真实 iPad 需要使用 Mac IP（已配置）

### 环境依赖
- Xcode 26.2+
- Docker Desktop
- PostgreSQL 15
- Python 3.11+

---

## 📞 技术支持

遇到问题时的检查清单：

1. **后端不响应**
   ```bash
   docker ps | grep mathcoach
   curl http://localhost:8000/health
   ```

2. **iOS 编译错误**
   - Clean Build Folder (⇧⌘K)
   - 删除 DerivedData
   - 重启 Xcode

3. **网络错误**
   - 检查 Docker 是否运行
   - 验证 IP 地址配置
   - 检查 ATS 设置

---

**项目进度：Phase 1-6 完成 ✅**
**总体完成度：约 70%**

下一步：添加家长/教师功能和更多题型。
