"""
本地题库（不依赖后端，随时可用）
支持难度 1-5 和技能筛选，由 config.json 控制。
"""
import random
from dataclasses import dataclass


@dataclass
class Question:
    question_text: str
    answer: str
    skill: str
    hint: str = ""


# ─────────────────────────────────────────────
#  难度参数映射
#  difficulty 1-5 → 数字范围
# ─────────────────────────────────────────────

def _range(difficulty: int, presets: list[tuple]) -> tuple:
    """
    presets: [(lo, hi), ...] 按难度1-5排列
    返回对应难度的 (lo, hi)
    """
    idx = max(0, min(difficulty - 1, len(presets) - 1))
    return presets[idx]


# ─────────────────────────────────────────────
#  加法
# ─────────────────────────────────────────────

def gen_addition(difficulty: int = 3) -> Question:
    """
    1: 10以内   2: 两位数   3: 三位数   4: 四位数   5: 带小数
    """
    if difficulty <= 1:
        a, b = random.randint(1, 9), random.randint(1, 9)
        return Question(f"{a} + {b} = ?", str(a + b), "addition",
                        "Count on from the bigger number")
    elif difficulty == 2:
        a, b = random.randint(10, 60), random.randint(10, 60)
        return Question(f"{a} + {b} = ?", str(a + b), "addition",
                        "Add the ones first, then the tens")
    elif difficulty == 3:
        a, b = random.randint(100, 600), random.randint(100, 600)
        return Question(f"{a} + {b} = ?", str(a + b), "addition",
                        "Line up the digits and carry if needed")
    elif difficulty == 4:
        a, b = random.randint(1000, 5000), random.randint(1000, 5000)
        return Question(f"{a} + {b} = ?", str(a + b), "addition",
                        "Work column by column from right to left")
    else:
        a = round(random.uniform(1.1, 9.9), 1)
        b = round(random.uniform(1.1, 9.9), 1)
        return Question(f"{a} + {b} = ?", str(round(a + b, 1)), "addition",
                        "Line up the decimal points")


# ─────────────────────────────────────────────
#  减法
# ─────────────────────────────────────────────

def gen_subtraction(difficulty: int = 3) -> Question:
    """
    1: 10以内   2: 两位数   3: 三位数   4: 四位数   5: 带小数
    """
    if difficulty <= 1:
        b = random.randint(1, 8)
        a = random.randint(b, 9)
        return Question(f"{a} - {b} = ?", str(a - b), "subtraction",
                        "Count back from the bigger number")
    elif difficulty == 2:
        b = random.randint(10, 50)
        a = random.randint(b + 1, b + 40)
        return Question(f"{a} - {b} = ?", str(a - b), "subtraction",
                        "You may need to borrow from the tens")
    elif difficulty == 3:
        b = random.randint(100, 400)
        a = random.randint(b + 1, b + 300)
        return Question(f"{a} - {b} = ?", str(a - b), "subtraction",
                        "Borrow carefully from the left column")
    elif difficulty == 4:
        b = random.randint(1000, 4000)
        a = random.randint(b + 1, b + 3000)
        return Question(f"{a} - {b} = ?", str(a - b), "subtraction",
                        "Work right to left, borrowing where needed")
    else:
        b = round(random.uniform(0.5, 5.0), 1)
        a = round(b + random.uniform(0.5, 5.0), 1)
        return Question(f"{a} - {b} = ?", str(round(a - b, 1)), "subtraction",
                        "Line up the decimal points before subtracting")


# ─────────────────────────────────────────────
#  乘法基础（Astrid, 2-5）
# ─────────────────────────────────────────────

def gen_multiplication_basic(difficulty: int = 2) -> Question:
    """
    1: ×1,×2   2: ×2-5   3: ×2-9   4: 两位数×一位数   5: 两位数×两位数
    """
    if difficulty <= 1:
        a = random.randint(1, 2)
        b = random.randint(1, 10)
    elif difficulty == 2:
        a = random.randint(2, 5)
        b = random.randint(1, 10)
    elif difficulty == 3:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
    elif difficulty == 4:
        a = random.randint(12, 25)
        b = random.randint(2, 9)
    else:
        a = random.randint(11, 19)
        b = random.randint(11, 19)

    if random.random() < 0.5:
        a, b = b, a
    return Question(f"{a} × {b} = ?", str(a * b), "multiplication_basic",
                    f"Think: {min(a,b)} groups of {max(a,b)}")


# ─────────────────────────────────────────────
#  乘法进阶（Jon, 6-9）
# ─────────────────────────────────────────────

def gen_multiplication(difficulty: int = 3) -> Question:
    """
    1: ×6-7   2: ×6-9   3: ×6-9 混合   4: 两位×一位   5: 两位×两位
    """
    if difficulty <= 1:
        a = random.randint(6, 7)
        b = random.randint(2, 9)
    elif difficulty <= 3:
        a = random.randint(6, 9)
        b = random.randint(2, 9)
    elif difficulty == 4:
        a = random.randint(12, 30)
        b = random.randint(6, 9)
    else:
        a = random.randint(11, 25)
        b = random.randint(11, 25)

    if random.random() < 0.5:
        a, b = b, a
    hint = {
        6: "6 × n = 5n + n", 7: "7 × 8 = 56 (7,8,9... 56,7,8!)",
        8: "8 × n = 2 × 4 × n", 9: "9 × n: digits add to 9",
    }.get(min(a, b), "Use your times tables")
    return Question(f"{a} × {b} = ?", str(a * b), "multiplication", hint)


# ─────────────────────────────────────────────
#  除法
# ─────────────────────────────────────────────

def gen_division(difficulty: int = 3) -> Question:
    """
    1: ÷2,÷5   2: ÷2-5   3: ÷2-9   4: ÷6-9 较大数   5: 带余数
    """
    if difficulty <= 1:
        b = random.choice([2, 5])
        result = random.randint(1, 10)
    elif difficulty == 2:
        b = random.randint(2, 5)
        result = random.randint(2, 10)
    elif difficulty == 3:
        b = random.randint(2, 9)
        result = random.randint(2, 12)
    elif difficulty == 4:
        b = random.randint(6, 9)
        result = random.randint(6, 15)
    else:
        # 带余数
        b = random.randint(3, 9)
        result = random.randint(3, 10)
        remainder = random.randint(1, b - 1)
        a = b * result + remainder
        return Question(f"{a} ÷ {b} = ? remainder ?",
                        f"{result} remainder {remainder}",
                        "division",
                        f"How many {b}s fit in {a}? What's left over?")

    a = b * result
    return Question(f"{a} ÷ {b} = ?", str(result), "division",
                    f"Think: {b} × ? = {a}")


# ─────────────────────────────────────────────
#  小数
# ─────────────────────────────────────────────

def gen_decimal(difficulty: int = 3) -> Question:
    """
    1: 0.1~0.9 加法   2: 一位小数加减   3: 一位小数混合   4: 两位小数   5: 乘以整数
    """
    if difficulty <= 1:
        a = round(random.uniform(0.1, 0.8), 1)
        b = round(random.uniform(0.1, 0.8), 1)
        return Question(f"{a} + {b} = ?", str(round(a + b, 1)), "decimal",
                        "Line up the decimal points")
    elif difficulty <= 3:
        a = round(random.uniform(1.1, 8.9), 1)
        b = round(random.uniform(1.1, 4.9), 1)
        op = random.choice(["+", "-"])
        if op == "-" and b > a:
            a, b = b, a
        ans = round(a + b if op == "+" else a - b, 1)
        return Question(f"{a} {op} {b} = ?", str(ans), "decimal",
                        "Line up the decimal points")
    elif difficulty == 4:
        a = round(random.uniform(1.1, 9.9), 2)
        b = round(random.uniform(1.1, 4.9), 2)
        op = random.choice(["+", "-"])
        if op == "-" and b > a:
            a, b = b, a
        ans = round(a + b if op == "+" else a - b, 2)
        return Question(f"{a} {op} {b} = ?", str(ans), "decimal",
                        "Line up the decimal points carefully")
    else:
        a = round(random.uniform(1.1, 5.9), 1)
        b = random.randint(2, 5)
        return Question(f"{a} × {b} = ?", str(round(a * b, 1)), "decimal",
                        "Multiply as if whole numbers, then place the decimal")


# ─────────────────────────────────────────────
#  分数基础（Astrid）
# ─────────────────────────────────────────────

def gen_fraction_basic(difficulty: int = 2) -> Question:
    templates_easy = [
        ("A pizza is cut into 2 equal pieces. You eat 1. What fraction did you eat?", "1/2"),
        ("A cake is cut into 4 equal pieces. You eat 1. What fraction did you eat?", "1/4"),
        ("A chocolate bar has 3 equal pieces. You take 1. What fraction is that?", "1/3"),
        ("A ribbon is cut into 4 equal pieces. 3 are red. What fraction is red?", "3/4"),
        ("A pie is cut into 8 equal slices. You eat 3. What fraction did you eat?", "3/8"),
    ]
    templates_medium = [
        ("A bag has 10 apples. 6 are red. What fraction are red?", "6/10 or 3/5"),
        ("There are 12 students. 8 wear glasses. What fraction wear glasses?", "8/12 or 2/3"),
        ("A rope is cut into 5 pieces. 2 are used. What fraction is used?", "2/5"),
        ("A box has 9 chocolates. 3 are dark. What fraction are dark?", "3/9 or 1/3"),
    ]
    pool = templates_easy if difficulty <= 2 else templates_medium
    q, a = random.choice(pool)
    return Question(q, a, "fraction_basic",
                    "Fraction = part ÷ whole")


# ─────────────────────────────────────────────
#  等价分数（Jon）
# ─────────────────────────────────────────────

def gen_fraction_equiv(difficulty: int = 3) -> Question:
    multiplier = random.randint(2, 4 + difficulty)
    num = random.randint(1, 4)
    den = random.randint(num + 1, 8)
    if random.random() < 0.5:
        return Question(
            f"{num}/{den} = ?/{den * multiplier}",
            str(num * multiplier),
            "fraction_equiv",
            "Multiply top and bottom by the same number"
        )
    else:
        return Question(
            f"{num * multiplier}/{den * multiplier} = {num}/?",
            str(den),
            "fraction_equiv",
            "Divide top and bottom by the same number"
        )


# ─────────────────────────────────────────────
#  时间（Astrid）
# ─────────────────────────────────────────────

def gen_time(difficulty: int = 2) -> Question:
    hour = random.randint(1, 12)
    if difficulty <= 1:
        minute = random.choice([0, 30])
    elif difficulty <= 3:
        minute = random.choice([0, 15, 30, 45])
    else:
        minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])

    if minute == 0:
        display = f"{hour}:00"
        hint = f"o'clock"
    elif minute == 30:
        display = f"{hour}:30"
        hint = "half past"
    elif minute == 15:
        display = f"{hour}:15"
        hint = "quarter past"
    elif minute == 45:
        display = f"{hour}:45"
        hint = "quarter to the next hour"
    else:
        display = f"{hour}:{minute:02d}"
        hint = f"{minute} minutes past {hour}"

    add = random.choice([15, 30, 45, 60])
    new_min = minute + add
    new_hour = hour + new_min // 60
    new_min = new_min % 60
    if new_hour > 12:
        new_hour -= 12

    templates = [
        (f"What time is {display}?", hint),
        (f"It is {display}. What time will it be in {add} minutes?",
         f"{new_hour}:{new_min:02d}"),
    ]
    q, a = random.choice(templates)
    return Question(q, a, "time",
                    "There are 60 minutes in an hour")


# ─────────────────────────────────────────────
#  Jon 专项：两位数进位加法
# ─────────────────────────────────────────────

def gen_addition_carrying(difficulty: int = 3) -> Question:
    """
    保证个位相加 >= 10（必须进位）。
    difficulty 1-2: 两位数+两位数
    difficulty 3-4: 两位数+两位数（更大）
    difficulty 5:   三位数+三位数（含进位）
    """
    if difficulty <= 4:
        # 个位凑出进位：a_ones + b_ones >= 10
        a_ones = random.randint(3, 9)
        b_ones = random.randint(10 - a_ones, 9)   # 保证进位
        if difficulty <= 2:
            a_tens = random.randint(1, 4)
            b_tens = random.randint(1, 4)
        else:
            a_tens = random.randint(2, 7)
            b_tens = random.randint(2, 7)
        a = a_tens * 10 + a_ones
        b = b_tens * 10 + b_ones
    else:
        # 三位数，百位或十位进位
        a = random.randint(150, 650)
        b = random.randint(150, 650)
        # 确保至少一个进位
        while (a % 10 + b % 10 < 10) and ((a // 10 % 10) + (b // 10 % 10) < 10):
            a = random.randint(150, 650)
            b = random.randint(150, 650)

    return Question(
        f"{a} + {b} = ?",
        str(a + b),
        "addition_carrying",
        f"Ones: {a%10}+{b%10}={a%10+b%10}, write {(a+b)%10} carry 1 to tens"
    )


# ─────────────────────────────────────────────
#  Jon 专项：两位数借位减法
# ─────────────────────────────────────────────

def gen_subtraction_borrowing(difficulty: int = 3) -> Question:
    """
    保证个位 a < b（必须借位）。
    difficulty 1-2: 两位数-两位数（结果>0）
    difficulty 3-4: 更大范围
    difficulty 5:   三位数（含借位）
    """
    if difficulty <= 4:
        # a 的个位 < b 的个位 → 必须借位
        b_ones = random.randint(3, 9)
        a_ones = random.randint(0, b_ones - 1)   # a_ones < b_ones
        if difficulty <= 2:
            b_tens = random.randint(1, 4)
            a_tens = random.randint(b_tens + 1, b_tens + 3)  # a_tens > b_tens 保证结果为正
        else:
            b_tens = random.randint(1, 6)
            a_tens = random.randint(b_tens + 1, b_tens + 5)
        a = a_tens * 10 + a_ones
        b = b_tens * 10 + b_ones
    else:
        # 三位数借位
        b = random.randint(130, 480)
        a = random.randint(b + 10, b + 300)
        # 确保个位需要借位
        while a % 10 >= b % 10:
            b = random.randint(130, 480)
            a = random.randint(b + 10, b + 300)

    return Question(
        f"{a} - {b} = ?",
        str(a - b),
        "subtraction_borrowing",
        f"Ones: can't do {a%10}-{b%10}, borrow 1 from tens → {a%10+10}-{b%10}={a%10+10-b%10}"
    )


# ─────────────────────────────────────────────
#  Astrid Year 2：20以内加减法
# ─────────────────────────────────────────────

def gen_yr2_addition(difficulty: int = 1) -> Question:
    """
    difficulty 1: 10以内   2: 20以内   3: 带凑十法   4: 两位数+一位数   5: 两位数+两位数
    """
    if difficulty <= 1:
        a = random.randint(1, 8)
        b = random.randint(1, 9 - a)
        hint = "Count on from the bigger number"
    elif difficulty == 2:
        a = random.randint(5, 14)
        b = random.randint(1, min(6, 20 - a))
        hint = "Make 10 first, then add the rest"
    elif difficulty == 3:
        # 凑十法：a 接近 10
        a = random.randint(7, 9)
        b = random.randint(3, 8)
        hint = f"Make 10: {a}+{10-a}=10, then add {b-(10-a)} more"
    elif difficulty == 4:
        a = random.randint(10, 30)
        b = random.randint(1, 9)
        hint = "Add the ones, then the tens"
    else:
        a = random.randint(10, 40)
        b = random.randint(10, 40)
        hint = "Add ones first, then tens"
    return Question(f"{a} + {b} = ?", str(a + b), "yr2_addition", hint)


def gen_yr2_subtraction(difficulty: int = 1) -> Question:
    """
    difficulty 1: 10以内   2: 20以内   3: 减到10   4: 两位数-一位数   5: 两位数-两位数
    """
    if difficulty <= 1:
        b = random.randint(1, 7)
        a = random.randint(b + 1, 9)
        hint = "Count back from the bigger number"
    elif difficulty == 2:
        b = random.randint(1, 9)
        a = random.randint(b + 1, 18)
        hint = "Think: what do I add to get from the small to the big?"
    elif difficulty == 3:
        # 减到10：a在11-18，减去个位
        a = random.randint(11, 18)
        b = a - 10
        hint = f"Take away {b} to reach 10"
    elif difficulty == 4:
        b = random.randint(1, 9)
        a = random.randint(b + 10, 39)
        hint = "Subtract the ones, keep the tens"
    else:
        b = random.randint(10, 30)
        a = random.randint(b + 1, b + 20)
        hint = "Subtract tens, then ones"
    return Question(f"{a} - {b} = ?", str(a - b), "yr2_subtraction", hint)


def gen_doubles(difficulty: int = 1) -> Question:
    """Double facts: 1+1 to 10+10 and near doubles"""
    if difficulty <= 2:
        n = random.randint(1, 6)
        return Question(f"{n} + {n} = ?", str(n * 2), "doubles",
                        f"Double {n}")
    elif difficulty <= 4:
        n = random.randint(4, 10)
        return Question(f"{n} + {n} = ?", str(n * 2), "doubles",
                        f"Double {n}: {n}×2")
    else:
        # near doubles
        n = random.randint(4, 9)
        off = random.choice([-1, 1])
        a, b = n, n + off
        return Question(f"{a} + {b} = ?", str(a + b), "doubles",
                        f"Near double: double {n} = {n*2}, then {'add' if off>0 else 'subtract'} 1")


def gen_skip_counting(difficulty: int = 1) -> Question:
    """Skip counting by 2, 5, 10"""
    if difficulty <= 1:
        step = random.choice([2, 5, 10])
        start = random.choice([0, 2, 4, 5, 10, 20])
        seq_len = 4
    elif difficulty <= 3:
        step = random.choice([2, 3, 5, 10])
        start = random.randint(0, 20) // step * step
        seq_len = 4
    else:
        step = random.choice([4, 6, 8, 25, 50])
        start = random.randint(0, 10) * step
        seq_len = 3

    seq = [start + i * step for i in range(seq_len + 1)]
    shown = seq[:-1]
    answer = seq[-1]
    shown_str = ", ".join(str(x) for x in shown)
    return Question(
        f"{shown_str}, ___",
        str(answer),
        "skip_counting",
        f"Count by {step}s"
    )


# ─────────────────────────────────────────────
#  技能名 → 生成函数 映射表
# ─────────────────────────────────────────────

SKILL_MAP: dict[str, callable] = {
    "addition":              gen_addition,
    "subtraction":           gen_subtraction,
    "addition_carrying":     gen_addition_carrying,
    "subtraction_borrowing": gen_subtraction_borrowing,
    "multiplication":        gen_multiplication,
    "multiplication_basic":  gen_multiplication_basic,
    "division":              gen_division,
    "decimal":               gen_decimal,
    "fraction_basic":        gen_fraction_basic,
    "fraction_equiv":        gen_fraction_equiv,
    "time":                  gen_time,
    "yr2_addition":          gen_yr2_addition,
    "yr2_subtraction":       gen_yr2_subtraction,
    "doubles":               gen_doubles,
    "skip_counting":         gen_skip_counting,
}


# ─────────────────────────────────────────────
#  公共接口
# ─────────────────────────────────────────────

def generate_from_config(skills: list[str], difficulty: int, count: int) -> list[Question]:
    """
    按 config.json 的设置生成题目。
    - skills: 技能名列表（均等权重）
    - difficulty: 1-5
    - count: 题目数量
    """
    # 过滤掉未知技能
    valid = [s for s in skills if s in SKILL_MAP]
    if not valid:
        valid = ["addition", "subtraction"]

    pool: list[Question] = []
    for skill in valid:
        fn = SKILL_MAP[skill]
        for _ in range(max(count, 8)):   # 每个技能生成足够多候选
            pool.append(fn(difficulty))

    random.shuffle(pool)

    # 去重 + 按技能均衡采样
    seen: set[str] = set()
    per_skill: dict[str, int] = {s: 0 for s in valid}
    result: list[Question] = []

    for q in pool:
        if q.question_text in seen:
            continue
        if len(result) >= count:
            break
        seen.add(q.question_text)
        per_skill[q.skill] = per_skill.get(q.skill, 0) + 1
        result.append(q)

    # 不够就补
    while len(result) < count:
        skill = random.choice(valid)
        result.append(SKILL_MAP[skill](difficulty))

    return result[:count]


def generate_for_student(student_id: str, count: int = 10) -> list[Question]:
    """向后兼容接口（不读 config，用默认设置）"""
    sid = student_id.lower()
    if "astrid" in sid:
        return generate_from_config(
            ["multiplication_basic", "addition", "subtraction"], 2, count)
    else:
        return generate_from_config(
            ["multiplication", "division", "addition"], 3, count)
