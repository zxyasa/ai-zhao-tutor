#!/usr/bin/env python3
"""
每日定时任务入口
由 launchd 在 07:30 和 20:00 各触发一次。

手动测试:
    python run_daily.py                  # 按当前时间决定执行早晨或晚间任务
    python run_daily.py --morning        # 强制执行早晨推送
    python run_daily.py --evening        # 强制执行晚间汇总
    python run_daily.py --dry-run        # 只打印，不写 Notes
    python run_daily.py --morning --student jon   # 只处理 Jon
"""
import sys
import datetime
import logging
import os
import json
from pathlib import Path

# 让 Python 能找到同目录的模块
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ─── 学生配置 ───────────────────────────────
STUDENTS = [
    {"id": "jon_zhao",    "name": "Jon",    "count": 10, "folder": "Jon Maths"},
    {"id": "astrid_zhao", "name": "Astrid", "count": 10, "folder": "Astrid Maths"},
]

CONFIG_PATH = Path(__file__).with_name("config.json")
API_BASE = os.getenv("MATHCOACH_API_BASE", "http://localhost:8000/api/v1")


def _load_runtime_config() -> dict:
    """读取 notes 配置文件，缺失时返回空字典。"""
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        log.warning(f"读取 config.json 失败: {exc}")
        return {}


def _get_parent_phone() -> str:
    """
    读取家长号码，优先级：
    1. 环境变量 MATHCOACH_PARENT_PHONE
    2. config.json parent.phone
    3. 占位值（不会发送）
    """
    from_env = os.getenv("MATHCOACH_PARENT_PHONE", "").strip()
    if from_env:
        return from_env

    cfg = _load_runtime_config()
    from_file = str(cfg.get("parent", {}).get("phone", "")).strip()
    if from_file:
        return from_file

    return "+61400000000"


def run_morning(dry_run: bool = False, only_student: str | None = None):
    """早晨任务：生成题目推送到 Apple Notes"""
    from daily_generator import push_daily_note

    today = datetime.date.today().strftime("%Y-%m-%d")
    log.info(f"=== 早晨推送开始 {today} ===")

    students = STUDENTS
    if only_student:
        students = [s for s in STUDENTS if only_student.lower() in s["id"].lower()]
        if not students:
            log.error(f"找不到学生：{only_student}")
            return

    results = {}
    for student in students:
        ok = push_daily_note(student, dry_run=dry_run)
        results[student["name"]] = "✅" if ok else "❌"

    summary = "  ".join(f"{name} {status}" for name, status in results.items())
    log.info(f"=== 推送完成：{summary} ===")


def run_evening(dry_run: bool = False):
    """
    晚间任务：汇总今日完成情况，发 iMessage 给家长。
    Phase 0 阶段：后端未跟踪完成情况，仅发一条提醒。
    Phase 1+ 后：接入 /api/v1/daily-summary 端点。
    """
    today = datetime.date.today().strftime("%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][
        datetime.date.today().weekday()
    ]

    # 尝试从后端获取汇总
    summary_text = _fetch_api_summary()

    if not summary_text:
        # Phase 0 降级：发基础提醒
        summary_text = (
            f"📊 MathCoach 日报 {today} {weekday}\n"
            f"今天的题目已发到 Notes，记得检查 Jon 和 Astrid 是否完成了 😊"
        )

    log.info(f"晚间汇总内容:\n{summary_text}")

    phone = _get_parent_phone()
    if not dry_run:
        if phone == "+61400000000":
            log.warning("未配置家长手机号（仍为占位值），已跳过发送。")
            log.info("可在 services/notes/config.json 添加 parent.phone，或设置 MATHCOACH_PARENT_PHONE。")
            return
        _send_imessage(phone, summary_text)
    else:
        log.info("[dry-run] 会发送 iMessage 到 " + phone)


def _fetch_api_summary() -> str | None:
    """尝试从后端 API 获取今日汇总，失败返回 None"""
    try:
        import urllib.request
        url = f"{API_BASE}/parent/daily-summary"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
        lines = [f"📊 MathCoach 日报 {datetime.date.today().strftime('%m月%d日')}"]
        for s in data:
            status = "✅ 已完成" if s.get("is_completed") else "⏳ 未完成"
            lines.append(
                f"  {s.get('student_name', 'Student')}: {status} "
                f"进度 {s.get('completed_questions', 0)}/{s.get('target_questions', 0)} "
                f"正确率 {round(float(s.get('accuracy_percent', 0.0)))}% "
                f"🔥 {s.get('current_streak', 0)}天"
            )
        return "\n".join(lines)
    except Exception:
        return None


def _send_imessage(phone: str, message: str):
    """通过 AppleScript 发送 iMessage"""
    import subprocess
    import tempfile

    script = f'''
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "{phone}" of targetService
    send "{message.replace(chr(34), chr(39)).replace(chr(10), "\\n")}" to targetBuddy
end tell
'''
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".applescript", delete=False
        ) as f:
            f.write(script)
            path = f.name
        result = subprocess.run(["osascript", path], capture_output=True, text=True, timeout=15)
        import os; os.unlink(path)
        if result.returncode == 0:
            log.info("iMessage 发送成功 ✅")
        else:
            log.error(f"iMessage 发送失败: {result.stderr.strip()}")
    except Exception as e:
        log.error(f"iMessage 异常: {e}")


# ─────────────────────────────────────────────
#  入口
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    force_morning = "--morning" in args
    force_evening = "--evening" in args
    only_student = next((a.split("=")[1] if "=" in a else args[i + 1]
                         for i, a in enumerate(args)
                         if a == "--student" and i + 1 < len(args)), None)

    if force_morning:
        run_morning(dry_run=dry_run, only_student=only_student)
    elif force_evening:
        run_evening(dry_run=dry_run)
    else:
        # 按时间自动判断
        hour = datetime.datetime.now().hour
        if 5 <= hour < 14:
            run_morning(dry_run=dry_run, only_student=only_student)
        elif hour >= 18:
            run_evening(dry_run=dry_run)
        else:
            log.warning(f"当前时间 {hour}:xx，不在推送时段（早晨 5-14 / 晚间 18+）")
            log.info("使用 --morning 或 --evening 强制运行")
