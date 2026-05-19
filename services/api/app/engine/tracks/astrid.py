import random
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from .base import TrackPlugin

_STYLE_TO_SKILL = {
    "add_no_carry": "yr2_sem1_add_sub_100",
    "sub_no_borrow": "yr2_sem1_add_sub_100",
    "missing_number": "yr2_sem1_missing_number",
    "place_value": "yr2_sem1_place_value",
    "compare": "yr2_sem1_compare_100",
    "word_problem": "yr2_sem1_word_problem",
}


class AstridTrackPlugin(TrackPlugin):
    @property
    def student_id(self) -> str:
        return "astrid_zhao"

    def build_item(
        self,
        db: Session,
        *,
        allowed_skills: Optional[set[str]] = None,
    ) -> Optional[dict]:  # db kept for interface compatibility
        rng = random.Random()
        styles = list(_STYLE_TO_SKILL.keys())
        if allowed_skills is not None:
            styles = [s for s in styles if _STYLE_TO_SKILL[s] in allowed_skills]
        if not styles:
            return None
        style = rng.choice(styles)

        if style == "add_no_carry":
            while True:
                a = rng.randint(10, 79)
                b = rng.randint(1, 19)
                if (a % 10) + (b % 10) < 10 and (a + b) <= 100:
                    c = a + b
                    return {
                        "item_id": f"astrid_add_{uuid4()}",
                        "skill_id": "yr2_sem1_add_sub_100",
                        "question_text": f"{a} + {b} = ?",
                        "question_type": "arithmetic",
                        "difficulty": 1,
                        "parameters": {"a": a, "b": b, "operation": "add", "carry": False},
                        "correct_answer": str(c),
                        "hint": "Add the ones first, then the tens.",
                        "explanation": f"{a} + {b} = {c}.",
                        "validation_rule": "numeric",
                        "__persist_dynamic_item": True,
                    }

        if style == "sub_no_borrow":
            while True:
                a = rng.randint(20, 100)
                b = rng.randint(1, 40)
                if a >= b and (a % 10) >= (b % 10):
                    d = a - b
                    return {
                        "item_id": f"astrid_sub_{uuid4()}",
                        "skill_id": "yr2_sem1_add_sub_100",
                        "question_text": f"{a} - {b} = ?",
                        "question_type": "arithmetic",
                        "difficulty": 1,
                        "parameters": {"a": a, "b": b, "operation": "sub", "borrow": False},
                        "correct_answer": str(d),
                        "hint": "When ones are enough, subtract ones first.",
                        "explanation": f"{a} - {b} = {d}.",
                        "validation_rule": "numeric",
                        "__persist_dynamic_item": True,
                    }

        if style == "missing_number":
            if rng.choice([True, False]):
                a = rng.randint(5, 40)
                b = rng.randint(5, 40)
                c = a + b
                return {
                    "item_id": f"astrid_missing_add_{uuid4()}",
                    "skill_id": "yr2_sem1_missing_number",
                    "question_text": f"□ + {b} = {c}, so □ = ?",
                    "question_type": "arithmetic",
                    "difficulty": 1,
                    "parameters": {"a": a, "b": b, "c": c, "type": "missing_add_left"},
                    "correct_answer": str(a),
                    "hint": "Think: how much should be added to {0} to make {1}?".format(b, c),
                    "explanation": f"Since {a} + {b} = {c}, □ = {a}.",
                    "validation_rule": "numeric",
                    "__persist_dynamic_item": True,
                }
            a = rng.randint(20, 90)
            b = rng.randint(1, min(40, a - 1))
            c = a - b
            return {
                "item_id": f"astrid_missing_sub_{uuid4()}",
                "skill_id": "yr2_sem1_missing_number",
                "question_text": f"{a} - □ = {c}, so □ = ?",
                "question_type": "arithmetic",
                "difficulty": 1,
                "parameters": {"a": a, "b": b, "c": c, "type": "missing_sub_middle"},
                "correct_answer": str(b),
                "hint": "What number should be subtracted from {0} to get {1}?".format(a, c),
                "explanation": f"Since {a} - {b} = {c}, □ = {b}.",
                "validation_rule": "numeric",
                "__persist_dynamic_item": True,
            }

        if style == "place_value":
            n = rng.randint(10, 99)
            if rng.choice([True, False]):
                tens = n // 10
                return {
                    "item_id": f"astrid_place_tens_{uuid4()}",
                    "skill_id": "yr2_sem1_place_value",
                    "question_text": f"How many tens are in {n}?",
                    "question_type": "arithmetic",
                    "difficulty": 1,
                    "parameters": {"number": n, "ask": "tens"},
                    "correct_answer": str(tens),
                    "hint": "The tens digit shows how many tens.",
                    "explanation": f"{n} has {tens} tens.",
                    "validation_rule": "numeric",
                    "__persist_dynamic_item": True,
                }
            ones = n % 10
            return {
                "item_id": f"astrid_place_ones_{uuid4()}",
                "skill_id": "yr2_sem1_place_value",
                "question_text": f"What is the ones digit in {n}?",
                "question_type": "arithmetic",
                "difficulty": 1,
                "parameters": {"number": n, "ask": "ones"},
                "correct_answer": str(ones),
                "hint": "The ones digit is the rightmost digit.",
                "explanation": f"The ones digit in {n} is {ones}.",
                "validation_rule": "numeric",
                "__persist_dynamic_item": True,
            }

        if style == "compare":
            a = rng.randint(10, 99)
            b = rng.randint(10, 99)
            while b == a:
                b = rng.randint(10, 99)
            ans = max(a, b)
            return {
                "item_id": f"astrid_compare_{uuid4()}",
                "skill_id": "yr2_sem1_compare_100",
                "question_text": f"Which number is larger, {a} or {b}? Enter the number only.",
                "question_type": "arithmetic",
                "difficulty": 1,
                "parameters": {"a": a, "b": b},
                "correct_answer": str(ans),
                "hint": "Compare tens first. If tens are equal, compare ones.",
                "explanation": f"The larger number between {a} and {b} is {ans}.",
                "validation_rule": "numeric",
                "__persist_dynamic_item": True,
            }

        if rng.choice([True, False]):
            a = rng.randint(8, 40)
            b = rng.randint(5, 30)
            c = a + b
            return {
                "item_id": f"astrid_word_add_{uuid4()}",
                "skill_id": "yr2_sem1_word_problem",
                "question_text": f"Xiaoming has {a} pencils and buys {b} more. How many pencils does he have in total?",
                "question_type": "arithmetic",
                "difficulty": 1,
                "parameters": {"a": a, "b": b, "operation": "add"},
                "correct_answer": str(c),
                "hint": "The phrase 'buys more' usually means addition.",
                "explanation": f"{a} + {b} = {c}.",
                "validation_rule": "numeric",
                "__persist_dynamic_item": True,
            }

        a = rng.randint(20, 80)
        b = rng.randint(5, min(30, a - 1))
        d = a - b
        return {
            "item_id": f"astrid_word_sub_{uuid4()}",
            "skill_id": "yr2_sem1_word_problem",
            "question_text": f"There are {a} candies in a box. After eating {b}, how many are left?",
            "question_type": "arithmetic",
            "difficulty": 1,
            "parameters": {"a": a, "b": b, "operation": "sub"},
            "correct_answer": str(d),
            "hint": "The phrase 'left' usually means subtraction.",
            "explanation": f"{a} - {b} = {d}.",
            "validation_rule": "numeric",
            "__persist_dynamic_item": True,
        }
