import random
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from .base import TrackPlugin


class JonTrackPlugin(TrackPlugin):
    @property
    def student_id(self) -> str:
        return "jon_zhao"

    def build_item(
        self,
        db: Session,
        *,
        allowed_skills: Optional[set[str]] = None,
    ) -> Optional[dict]:  # db kept for interface compatibility
        if allowed_skills is not None and "jon_carry_add_sub_100" not in allowed_skills:
            return None

        rng = random.Random()
        is_add = rng.choice([True, False])

        if is_add:
            while True:
                u1 = rng.randint(5, 9)
                u2 = rng.randint(5, 9)
                t1 = rng.randint(1, 4)
                t2 = rng.randint(1, 4)
                a = t1 * 10 + u1
                b = t2 * 10 + u2
                s = a + b
                if (u1 + u2) >= 10 and s <= 100:
                    return {
                        "item_id": f"jon_add_{uuid4()}",
                        "skill_id": "jon_carry_add_sub_100",
                        "question_text": f"{a} + {b} = ?",
                        "question_type": "arithmetic",
                        "difficulty": 1 if s <= 50 else 2,
                        "parameters": {"a": a, "b": b, "operation": "add"},
                        "correct_answer": str(s),
                        "hint": "Add ones first. If ones are 10 or more, carry to the tens place.",
                        "explanation": f"In ones: {a % 10}+{b % 10} requires carrying, then add tens. The answer is {s}.",
                        "validation_rule": "numeric",
                        "__persist_dynamic_item": True,
                    }
        else:
            while True:
                top_t = rng.randint(2, 9)
                top_u = rng.randint(0, 4)
                bot_t = rng.randint(1, top_t - 1)
                bot_u = rng.randint(top_u + 1, 9)
                a = top_t * 10 + top_u
                b = bot_t * 10 + bot_u
                d = a - b
                if top_u < bot_u and 0 <= d <= 100:
                    return {
                        "item_id": f"jon_sub_{uuid4()}",
                        "skill_id": "jon_carry_add_sub_100",
                        "question_text": f"{a} - {b} = ?",
                        "question_type": "arithmetic",
                        "difficulty": 1 if a <= 60 else 2,
                        "parameters": {"a": a, "b": b, "operation": "sub"},
                        "correct_answer": str(d),
                        "hint": "If the ones digit is not enough, borrow 1 ten.",
                        "explanation": f"The ones digit in {a} is smaller than in {b}, so borrow and subtract. The answer is {d}.",
                        "validation_rule": "numeric",
                        "__persist_dynamic_item": True,
                    }
