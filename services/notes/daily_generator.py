"""
每日题目生成 + 推送到 Apple Notes

用法:
    python daily_generator.py                    # 推送所有学生
    python daily_generator.py --student jon      # 只推送 Jon
    python daily_generator.py --dry-run          # 只打印，不写 Notes
"""
import subprocess
import datetime
import tempfile
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

NOTES_FOLDER = "Jon Maths"  # default, overridden per-student
API_BASE = "http://localhost:8000/api/v1"


# ─────────────────────────────────────────────
#  题目获取（后端优先，降级到本地）
# ─────────────────────────────────────────────

def load_student_config(student_name: str) -> dict:
    """从 config.json 读取学生配置，找不到返回默认值"""
    import json
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        key = student_name.lower()
        return cfg.get("students", {}).get(key, {})
    except Exception as e:
        log.warning(f"读取 config.json 失败 ({e})，使用默认配置")
        return {}


def fetch_questions(student_id: str, student_name: str = "",
                    count: int = 10, difficulty: int = 3,
                    skills: list[str] | None = None) -> list[dict]:
    """
    尝试从后端拉题。后端未运行时自动降级到本地生成。
    返回统一格式的 dict 列表：{question_text, answer, skill, hint}
    """
    try:
        import urllib.request
        import json
        url = f"{API_BASE}/daily-session/{student_id}"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
            log.info(f"[{student_id}] 后端题目拉取成功 ({len(data['items'])} 道)")
            return data["items"]
    except Exception as e:
        log.info(f"[{student_id}] 后端不可用，使用本地题库 (difficulty={difficulty}, skills={skills})")
        from local_questions import generate_from_config, generate_for_student
        if skills:
            questions = generate_from_config(skills, difficulty, count)
        else:
            questions = generate_for_student(student_id, count)
        return [
            {"question_text": q.question_text, "answer": q.answer,
             "skill": q.skill, "hint": q.hint}
            for q in questions
        ]


# ─────────────────────────────────────────────
#  Note 内容格式化
# ─────────────────────────────────────────────

def format_note_html(student_name: str, questions: list[dict], difficulty: int = 3) -> str:
    """
    Apple Notes body 使用 HTML。
    格式化为带编号的题目列表，附答案隐藏区域。
    """
    today = datetime.date.today().strftime("%d %B %Y")
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][
        datetime.date.today().weekday()
    ]

    difficulty_label = {1:"⭐", 2:"⭐⭐", 3:"⭐⭐⭐", 4:"⭐⭐⭐⭐", 5:"⭐⭐⭐⭐⭐"}.get(difficulty, "⭐⭐⭐")
    lines = [
        f"<h2>📐 {student_name}'s Maths Practice</h2>",
        f"<p><b>{weekday} {today}</b> &nbsp;·&nbsp; {len(questions)} questions &nbsp;·&nbsp; {difficulty_label}</p>",
        "<hr>",
        "<ol>",
    ]

    for q in questions:
        hint_html = f"<br><i>💡 提示：{q['hint']}</i>" if q.get("hint") else ""
        lines.append(
            f"<li><p><b>{q['question_text']}</b>"
            f"{hint_html}"
            f"<br>Answer: ___________</p></li>"
        )

    lines += [
        "</ol>",
        "<hr>",
        f"<p>✅ Tell Dad when you're done — today's goal is all {len(questions)}!</p>",
        "<br>",
        "<details><summary>📋 Answers (for Dad)</summary><ol>",
    ]
    for q in questions:
        lines.append(f"<li>{q['answer']}</li>")
    lines += ["</ol></details>"]

    return "\n".join(lines)


# ─────────────────────────────────────────────
#  Apple Notes 推送
# ─────────────────────────────────────────────

def push_to_notes(title: str, html_body: str, folder: str = NOTES_FOLDER, dry_run: bool = False) -> bool:
    """
    通过 AppleScript 在指定 Notes 文件夹创建新便签。
    写入临时 .applescript 文件再执行，避免 shell 转义问题。
    返回 True 表示成功。
    """
    if dry_run:
        log.info(f"[dry-run] 会创建便签：{title}（文件夹：{folder}）")
        print(html_body)
        return True

    # 把 HTML 内容写到临时文件，AppleScript 从文件读（避免引号地狱）
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html_body)
        html_path = f.name

    script = f'''
set htmlPath to "{html_path}"
set noteTitle to "{title}"
set folderName to "{folder}"

-- 读取 HTML 文件内容
set htmlFile to open for access POSIX file htmlPath
set htmlContent to read htmlFile as «class utf8»
close access htmlFile

tell application "Notes"
    -- 确保文件夹存在
    tell account "iCloud"
        if not (exists folder folderName) then
            make new folder with properties {{name:folderName}}
        end if
        set theFolder to folder folderName

        -- 检查今天是否已经推送过（避免重复）
        set todayTitle to noteTitle
        set existingNotes to notes of theFolder whose name is todayTitle
        if (count of existingNotes) is 0 then
            make new note at theFolder with properties {{name:todayTitle, body:htmlContent}}
            return "created"
        else
            -- 已存在则更新内容
            set body of item 1 of existingNotes to htmlContent
            return "updated"
        end if
    end tell
end tell
'''

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".applescript", delete=False, encoding="utf-8"
        ) as sf:
            sf.write(script)
            script_path = sf.name

        result = subprocess.run(
            ["osascript", script_path],
            capture_output=True, text=True, timeout=30
        )
        os.unlink(script_path)
        os.unlink(html_path)

        if result.returncode != 0:
            log.error(f"AppleScript 错误: {result.stderr.strip()}")
            return False

        action = result.stdout.strip()
        log.info(f"便签「{title}」{action} ✅")
        return True

    except subprocess.TimeoutExpired:
        log.error("AppleScript 超时（Notes App 可能未响应）")
        return False
    except Exception as e:
        log.error(f"推送失败: {e}")
        return False


# ─────────────────────────────────────────────
#  主函数
# ─────────────────────────────────────────────

def push_daily_note(student: dict, dry_run: bool = False) -> bool:
    """
    为单个学生生成今日题目并推送到 Notes。
    student 字段来自 config.json（或 run_daily.py 的 STUDENTS 列表）。
    """
    student_id = student["id"]
    name = student["name"]
    folder = student.get("folder", f"{name} Maths")

    # 从 config.json 读取最新设置（每次推送都重新读，改完立即生效）
    cfg = load_student_config(name)
    count      = cfg.get("count",      student.get("count", 10))
    difficulty = cfg.get("difficulty", student.get("difficulty", 3))
    skills     = cfg.get("skills",     student.get("skills", None))
    folder     = cfg.get("folder",     folder)

    log.info(f"开始处理 {name} — 难度:{difficulty} 题数:{count} 技能:{skills}")

    questions = fetch_questions(student_id, name, count, difficulty, skills)
    if not questions:
        log.error(f"{name} 题目获取失败，跳过")
        return False

    today = datetime.date.today().strftime("%Y-%m-%d")
    title = f"Maths - {name} - {today}"
    html_body = format_note_html(name, questions, difficulty)

    return push_to_notes(title, html_body, folder=folder, dry_run=dry_run)
