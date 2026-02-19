#!/bin/bash
# 注册 launchd 定时任务
# 用法:
#   bash scheduler.sh          # 安装/更新定时任务
#   bash scheduler.sh unload   # 停止并移除定时任务
#   bash scheduler.sh status   # 查看运行状态

set -e

LABEL="com.zhao.mathcoach.daily"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3)"
RUN_SCRIPT="${SCRIPT_DIR}/run_daily.py"

# ── 停止 ──────────────────────────────────────
if [[ "$1" == "unload" ]]; then
    launchctl unload "$PLIST" 2>/dev/null && echo "✅ 定时任务已停止" || echo "（任务未在运行）"
    rm -f "$PLIST"
    echo "已删除 $PLIST"
    exit 0
fi

# ── 状态 ──────────────────────────────────────
if [[ "$1" == "status" ]]; then
    echo "=== launchctl 状态 ==="
    launchctl list | grep "$LABEL" || echo "（未注册）"
    echo ""
    echo "=== 最近日志 ==="
    tail -20 /tmp/mathcoach_daily.log 2>/dev/null || echo "（暂无日志）"
    exit 0
fi

# ── 安装 ──────────────────────────────────────
echo "Python:  $PYTHON"
echo "脚本:    $RUN_SCRIPT"
echo "Plist:   $PLIST"
echo ""

# 先卸载旧的（忽略错误）
launchctl unload "$PLIST" 2>/dev/null || true

cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${RUN_SCRIPT}</string>
    </array>

    <!-- 工作目录设为脚本所在目录，保证本地模块可以 import -->
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>

    <key>StartCalendarInterval</key>
    <array>
        <!-- 早上 07:30 → 生成题目推送到 Notes -->
        <dict>
            <key>Hour</key><integer>7</integer>
            <key>Minute</key><integer>30</integer>
        </dict>
        <!-- 晚上 20:00 → 发汇总 iMessage -->
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

    <!-- Mac 休眠唤醒后补跑错过的任务 -->
    <key>ProcessType</key>
    <string>Background</string>
</dict>
</plist>
EOF

launchctl load "$PLIST"

echo "✅ 定时任务已注册！"
echo ""
echo "时间表："
echo "  07:30  → 生成题目，推送到 Apple Notes"
echo "  20:00  → 汇总今日情况，发 iMessage"
echo ""
echo "日志文件："
echo "  tail -f /tmp/mathcoach_daily.log"
echo "  tail -f /tmp/mathcoach_daily_err.log"
echo ""
echo "手动立即测试："
echo "  cd ${SCRIPT_DIR}"
echo "  python3 run_daily.py --morning --dry-run    # 预览题目"
echo "  python3 run_daily.py --morning              # 真实推送"
