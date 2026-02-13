# GitHub Setup Instructions

## Step 1: Configure Git (一次性设置)

在命令行中运行:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 2: Create GitHub Repository

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. Repository name: `mathcoach`
4. Description: "AI-powered math training system for NSW Year 3-6 students"
5. **勾选** "Private" (如果不想公开代码)
6. **不要** 勾选 "Initialize with README" (我们已经有了)
7. 点击 "Create repository"

## Step 3: Push to GitHub

复制 GitHub 给你的仓库 URL (形如 `https://github.com/YOUR_USERNAME/mathcoach.git`)

然后在命令行运行:

```bash
cd c:\Users\zxyas\Workplace\mathcoach

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/mathcoach.git

# 首次提交 (如果还没有提交)
git add .
git commit -m "Initial commit: MathCoach full-stack platform"

# 推送到 GitHub
git push -u origin main
```

如果提示推送到 `master` 而不是 `main`:
```bash
git branch -M main
git push -u origin main
```

## Step 4: Verify Upload

在浏览器打开你的 GitHub 仓库,应该看到:
- ✅ 所有文件和文件夹
- ✅ README.md 显示在首页
- ✅ Commit message 可见

## 今晚在 Mac 上的工作流程

### 1. Clone 仓库
```bash
cd ~/Projects
git clone https://github.com/YOUR_USERNAME/mathcoach.git
cd mathcoach
```

### 2. 按照 MAC_SETUP.md 设置环境
```bash
# 查看设置指南
cat docs/MAC_SETUP.md
```

### 3. 开发 iOS 应用
```bash
# 查看开发清单
cat docs/iOS_CHECKLIST.md
```

## 日常 Git 工作流

### 在 Windows 上 (白天)
```bash
cd c:\Users\zxyas\Workplace\mathcoach

# 拉取最新更改
git pull origin main

# 做一些文档/后端工作
# ...

# 提交更改
git add .
git commit -m "描述你的更改"
git push origin main
```

### 在 Mac 上 (晚上)
```bash
cd ~/Projects/mathcoach

# 拉取最新更改
git pull origin main

# 开发 iOS 应用
# ...

# 提交更改
git add .
git commit -m "描述你的更改"
git push origin main
```

## Git Tips

### 查看状态
```bash
git status
```

### 查看更改
```bash
git diff
```

### 查看提交历史
```bash
git log --oneline --graph
```

### 撤销未提交的更改
```bash
git checkout -- <file>
```

### 创建分支 (可选)
```bash
# 创建新分支
git checkout -b feature/ios-app

# 切换回主分支
git checkout main

# 合并分支
git merge feature/ios-app
```

## Troubleshooting

### Push 被拒绝
```bash
# 拉取最新更改后再推送
git pull origin main
git push origin main
```

### 忘记 commit message
```bash
# 修改最后一次 commit message
git commit --amend -m "新的 commit message"
```

### 需要忽略某些文件
编辑 `.gitignore` 文件,添加需要忽略的文件或文件夹

---

## 下一步

完成 GitHub 设置后,今晚在 Mac 上:
1. ✅ Clone 仓库
2. ✅ 按照 `docs/MAC_SETUP.md` 设置环境
3. ✅ 按照 `docs/iOS_CHECKLIST.md` 开发 iOS 应用
4. ✅ 定期 commit 和 push
